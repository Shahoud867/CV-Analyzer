"""
Main Application Entry Point
Phase 3: Core Application Implementation

This is the main entry point for the Intelligent CV Analyzer application.
It provides a command-line interface for testing and demonstrating the system.
"""

import sys
import os
from pathlib import Path
from typing import List

try:
    from engine.analyzer import CVAnalyzer, JobDescription
    from extractors.pdf_extractor import PDFExtractor
    from extractors.docx_extractor import DOCXExtractor
    from persistence.db import DatabaseManager
    from reports.performance_runner import run_performance
    from reports.docx_report import generate_academic_report
except ImportError:
    # Fallback when executed as a script
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    from engine.analyzer import CVAnalyzer, JobDescription
    from extractors.pdf_extractor import PDFExtractor
    from extractors.docx_extractor import DOCXExtractor
    from persistence.db import DatabaseManager
    from reports.performance_runner import run_performance
    # Add this fallback import so --report works even in script mode
    try:
        from reports.docx_report import generate_academic_report
    except Exception:
        generate_academic_report = None


class CVAnalyzerApp:
    """
    Main application class that orchestrates the CV analysis process.
    Provides command-line interface and optional GUI launcher.
    """
    
    def __init__(self):
        """Initialize the CV Analyzer application."""
        self.analyzer = CVAnalyzer()
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        self.db = DatabaseManager()
        
        # Check and report library availability
        try:
            import importlib.util as _import_util
            if _import_util.find_spec('docx') is not None:
                print("✅ All text extraction libraries are available (PDF + DOCX)")
            else:
                print("Warning: python-docx not available. DOCX extraction will not work.")
        except Exception:
            print("Warning: Could not verify python-docx availability. DOCX extraction may not work.")
        
    @staticmethod
    def normalize_algorithm(name: str) -> str | None:
        """Normalize user-provided algorithm names to canonical forms.

        Accepts common aliases (case-insensitive) and returns one of:
        "Brute Force", "Rabin-Karp", "KMP", "Compare All". Returns None
        if the name is not recognized.
        """
        if not isinstance(name, str):
            return None
        key = name.strip().lower()
        mapping = {
            # KMP
            "kmp": "KMP",
            # Rabin-Karp
            "rabin-karp": "Rabin-Karp",
            "rabinkarp": "Rabin-Karp",
            "rabin": "Rabin-Karp",
            "rk": "Rabin-Karp",
            # Brute Force
            "brute force": "Brute Force",
            "bruteforce": "Brute Force",
            "brute": "Brute Force",
            "bf": "Brute Force",
            # Compare All (meta mode)
            "compare all": "Compare All",
            "compare": "Compare All",
            "all": "Compare All",
        }
        return mapping.get(key)


    def run_phase4_performance(self, max_files: int = 12):
        """Run Phase 4 performance experiments and generate charts."""
        print("\n" + "="*60)
        print("PHASE 4: PERFORMANCE TESTING & ANALYSIS")
        print("="*60)
        csv_path, charts = run_performance(max_files=max_files)
        print(f"\n✓ Results CSV: {csv_path}")
        print("✓ Charts generated:")
        for k, v in charts.items():
            print(f"  - {k}: {v}")

    def run_cli_analysis(
        self,
        title: str,
        keywords_csv: str,
        dataset: str | None = None,
        files: list[str] | None = None,
        algorithm: str = "KMP",
        out_csv: str | None = None,
        top_n: int = 10,
        case_sensitive: bool = False,
    ):
        """Run a CLI analysis using a dynamically provided job description.

        Args:
            title: Job title
            keywords_csv: Comma-separated keywords
            dataset: Optional folder path to scan for CVs
            files: Optional explicit file paths list
            algorithm: Algorithm to use (Brute Force|Rabin-Karp|KMP|Compare All)
            out_csv: Optional CSV output path
            top_n: How many top CVs to print
            case_sensitive: Match keywords with case sensitivity (default False)
        """
        if not title or not keywords_csv:
            print("Error: --title and --keywords are required for --analyze")
            return

        keywords = [k.strip() for k in keywords_csv.split(',') if k.strip()]
        job = JobDescription(id=0, title=title, description="", keywords=keywords, created_at="")

        # Gather CV files
        cv_files: list[str] = []
        if dataset:
            cv_files.extend(self._get_cv_files_from_dataset(dataset, max_files=1000))
        if files:
            cv_files.extend(files)

        # De-duplicate
        cv_files = list(dict.fromkeys(cv_files))
        if not cv_files:
            print("No CV files provided. Use --dataset <folder> or --files <paths>...")
            return

        # Run analysis
        if algorithm == "Compare All":
            algos = ["Brute Force", "Rabin-Karp", "KMP"]
            results = {}
            for algo in algos:
                batch = self.analyzer.analyze_multiple_cvs(cv_files, job, algo, case_sensitive=case_sensitive)
                results[algo] = batch
            # Show best algorithm by total time
            best_algo, best_batch = min(results.items(), key=lambda kv: kv[1].total_execution_time)
            print(f"\nBest Algorithm: {best_algo}")
            top = self.analyzer.get_top_matching_cvs(best_batch, top_n=top_n)
            print(f"Top {len(top)} CVs for '{title}' with {best_algo}:")
            for i, r in enumerate(top, 1):
                print(f"  {i}. {r.cv_filename}: score={r.relevance_score:.3f}, matches={len(r.matched_keywords)}/{r.total_keywords}")
            if out_csv:
                self.analyzer.export_results_to_csv(best_batch, out_csv)
                print(f"Saved CSV: {out_csv}")
        else:
            batch = self.analyzer.analyze_multiple_cvs(cv_files, job, algorithm, case_sensitive=case_sensitive)
            top = self.analyzer.get_top_matching_cvs(batch, top_n=top_n)
            print(f"\nAlgorithm: {algorithm}")
            print(f"Analyzed {batch.total_cvs_analyzed} CVs in {batch.total_execution_time:.3f}s")
            print(f"Average score: {batch.average_relevance_score:.3f}")
            print(f"Top {len(top)} CVs for '{title}':")
            for i, r in enumerate(top, 1):
                print(f"  {i}. {r.cv_filename}: score={r.relevance_score:.3f}, matches={len(r.matched_keywords)}/{r.total_keywords}")
            if out_csv:
                self.analyzer.export_results_to_csv(batch, out_csv)
                print(f"Saved CSV: {out_csv}")
    
    def _get_cv_files_from_dataset(self, dataset_path: str, max_files: int = 10) -> List[str]:
        """
        Get CV files from the DataSet folder.
        
        Args:
            dataset_path: Path to the DataSet folder
            max_files: Maximum number of files to return
            
        Returns:
            List of CV file paths
        """
        cv_files = []
        
        try:
            if not os.path.exists(dataset_path):
                print(f"DataSet folder not found: {dataset_path}")
                return cv_files
            
            # Get all files in the dataset
            all_files = []
            for root, dirs, files in os.walk(dataset_path):
                for file in files:
                    if file.lower().endswith(('.pdf', '.docx', '.doc')):
                        file_path = os.path.join(root, file)
                        all_files.append(file_path)
            
            # Sort files for consistent results
            all_files.sort()
            
            # Limit to max_files
            cv_files = all_files[:max_files]
            
            print(f"Found {len(all_files)} CV files in DataSet")
            print(f"Analyzing first {len(cv_files)} files:")
            for i, file_path in enumerate(cv_files, 1):
                filename = os.path.basename(file_path)
                print(f"  {i}. {filename}")
            
        except Exception as e:
            print(f"Error scanning DataSet folder: {e}")
        
        return cv_files
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'db'):
            self.db.close()


def launch_gui():
    """Launch the desktop GUI."""
    try:
        # Lazy imports to avoid requiring PyQt5 for CLI use
        from PyQt5.QtWidgets import QApplication
        from gui.main_window import MainWindow
    except Exception as e:
        print(f"GUI launch failed: {e}")
        print("Ensure PyQt5 is installed and gui/main_window.py is available.")
        return

    qt_app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(qt_app.exec_())


def main():
    """Main entry point for the application."""
    app = CVAnalyzerApp()
    
    try:
        if len(sys.argv) > 1:
            if sys.argv[1] == "--performance":
                # Optional arg: number of files
                max_files = 12
                if len(sys.argv) > 2:
                    try:
                        max_files = int(sys.argv[2])
                    except ValueError:
                        pass
                app.run_phase4_performance(max_files=max_files)
            elif sys.argv[1] == "--report":
                if generate_academic_report is None:
                    print("Report generator not available. Please ensure reports/docx_report.py is present.")
                else:
                    path = generate_academic_report()
                    print(f"\n✓ Wrote report: {path}")
            elif sys.argv[1] == "--analyze":
                # Minimal flag parser for --analyze mode
                args = sys.argv[2:]
                def _get(flag: str, default: str | None = None):
                    if flag in args:
                        i = args.index(flag)
                        if i + 1 < len(args):
                            return args[i+1]
                    return default
                def _get_list(flag: str) -> list[str]:
                    vals = []
                    if flag in args:
                        i = args.index(flag)
                        # consume values until next flag or end
                        j = i + 1
                        while j < len(args) and not args[j].startswith('--'):
                            vals.append(args[j])
                            j += 1
                    return vals
                title = _get('--title', '')
                keywords = _get('--keywords', '')
                dataset = _get('--dataset')
                files = _get_list('--files')
                algorithm_raw = _get('--algorithm', 'KMP')
                # Validate and normalize algorithm early to fail fast for bad values
                algorithm = CVAnalyzerApp.normalize_algorithm(algorithm_raw) or ''
                if not algorithm:
                    print(f"Invalid algorithm: {algorithm_raw}")
                    print("Allowed algorithms: KMP, Rabin-Karp, Brute Force, Compare All")
                    print("Tip: You can also use aliases like 'rk', 'brute', or 'compare'.")
                    import sys as _sys
                    _sys.exit(2)
                out_csv = _get('--out')
                top_n = _get('--top', '10')
                try:
                    top_n = int(top_n) if isinstance(top_n, str) else int(top_n)
                except Exception:
                    top_n = 10
                case_sensitive = '--case-sensitive' in args
                app.run_cli_analysis(title, keywords, dataset, files, algorithm, out_csv, top_n, case_sensitive)
            elif sys.argv[1] == "--gui":
                launch_gui()
            elif sys.argv[1] == "--help":
                print("Intelligent CV Analyzer")
                print("Usage:")
                print("  python app.py --performance [N] # Run Phase 4 performance with up to N files")
                print("  python app.py --analyze --title <Job Title> --keywords \"A,B,C\" --dataset <folder> [--algorithm KMP|Rabin-Karp|Brute Force|Compare All] [--out results.csv] [--top 10] [--case-sensitive]")
                print("    - Algorithm aliases supported: kmp | rk | rabin | brute | compare | all")
                print("  python app.py --report          # Generate Phase 6 DOCX report in data/results")
                print("  python app.py --gui             # Launch the desktop GUI")
                print("  python app.py --help            # Show this help")
            else:
                print(f"Unknown option: {sys.argv[1]}")
                print("Use --help for usage information")
        else:
            # Default: show help
            print("Intelligent CV Analyzer")
            print("Run with --help for options or --gui to launch the desktop app.")
    
    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        app.cleanup()


if __name__ == "__main__":
    main()
