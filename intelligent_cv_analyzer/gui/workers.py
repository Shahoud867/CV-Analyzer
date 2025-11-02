"""
GUI Worker Threads
Handles background analysis tasks for the GUI.
"""

from PyQt5.QtCore import QThread, pyqtSignal


class AnalysisWorker(QThread):
    """Background worker thread for CV analysis."""
    
    progress = pyqtSignal(int, int)   # current, total
    error = pyqtSignal(str)
    analysisFinished = pyqtSignal(object)     # emits BatchAnalysisResult

    def __init__(self, analyzer, cv_files, job_desc, algorithm: str, case_sensitive: bool = False):
        super().__init__()
        self.analyzer = analyzer
        self.cv_files = cv_files
        self.job_desc = job_desc
        self.algorithm = algorithm
        self.case_sensitive = case_sensitive

    def run(self):
        """Run the analysis in background thread."""
        try:
            # Check if thread was interrupted before starting
            if self.isInterruptionRequested():
                return
            
            total = len(self.cv_files) if self.cv_files else 0
            self.progress.emit(0, total)
            
            # Run analysis
            batch_result = self.analyzer.analyze_multiple_cvs(
                self.cv_files, self.job_desc, self.algorithm, case_sensitive=self.case_sensitive
            )
            
            # Check if thread was interrupted during analysis
            if self.isInterruptionRequested():
                return
            
            self.analysisFinished.emit(batch_result)
            
        except Exception as e:
            if not self.isInterruptionRequested():
                self.error.emit(str(e))


class CompareAllWorker(QThread):
    """Background worker that runs all algorithms sequentially for comparison."""

    progress = pyqtSignal(int, int)  # current_algo_index (1-based), total_algorithms
    error = pyqtSignal(str)
    compareFinished = pyqtSignal(object)  # emits Dict[str, BatchAnalysisResult]

    def __init__(self, analyzer, cv_files, job_desc, case_sensitive: bool = False):
        super().__init__()
        self.analyzer = analyzer
        self.cv_files = cv_files
        self.job_desc = job_desc
        self.algorithms = ["Brute Force", "Rabin-Karp", "KMP"]
        self.case_sensitive = case_sensitive

    def run(self):
        try:
            results = {}
            total = len(self.algorithms)
            for idx, algo in enumerate(self.algorithms, start=1):
                if self.isInterruptionRequested():
                    return
                self.progress.emit(idx, total)
                batch = self.analyzer.analyze_multiple_cvs(self.cv_files, self.job_desc, algo, case_sensitive=self.case_sensitive)
                results[algo] = batch
            if not self.isInterruptionRequested():
                self.compareFinished.emit(results)
        except Exception as e:
            if not self.isInterruptionRequested():
                self.error.emit(str(e))