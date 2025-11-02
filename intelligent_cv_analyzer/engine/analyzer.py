"""
CV Analyzer Core Engine
Phase 3: Core Application Implementation

This module contains the main CV analysis engine that orchestrates the entire
analysis process, including text extraction, keyword matching, scoring,
and performance monitoring.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .algorithms import StringMatchingAlgorithms


@dataclass
class CVData:
    """Data class to store CV information and extracted text."""
    filename: str
    file_path: str
    extracted_text: str
    file_size: int
    extraction_time: float
    validation_status: bool
    error_message: Optional[str] = None


@dataclass
class JobDescription:
    """Data class to store job description and keywords."""
    id: int
    title: str
    description: str
    keywords: List[str]
    created_at: str


@dataclass
class AnalysisResult:
    """Data class to store analysis results for a single CV."""
    cv_filename: str
    job_description: str
    algorithm_used: str
    matched_keywords: List[str]
    missing_keywords: List[str]
    relevance_score: float
    execution_time: float
    comparison_count: int
    total_keywords: int
    timestamp: str


@dataclass
class BatchAnalysisResult:
    """Data class to store results from analyzing multiple CVs."""
    job_description: JobDescription
    algorithm_used: str
    cv_results: List[AnalysisResult]
    total_execution_time: float
    average_relevance_score: float
    total_cvs_analyzed: int
    timestamp: str


class CVAnalyzer:
    """
    Main CV analysis engine that coordinates text extraction, keyword matching,
    and performance analysis using different string matching algorithms.
    """
    
    def __init__(self):
        """Initialize the CV analyzer with string matching algorithms."""
        self.algorithms = StringMatchingAlgorithms()
        self.cv_cache: Dict[str, CVData] = {}
        self.analysis_history: List[BatchAnalysisResult] = []
    
    def analyze_cv(self, cv_text: str, keywords: List[str], algorithm: str, case_sensitive: bool = False) -> AnalysisResult:
        """
        Analyze a single CV against a set of keywords using specified algorithm.
        
        Args:
            cv_text: The extracted text from the CV
            keywords: List of keywords to search for
            algorithm: Name of the algorithm to use ("Brute Force", "Rabin-Karp", "KMP")
            
        Returns:
            AnalysisResult object containing analysis results and metrics
        """
        start_time = time.time()
        
        # Validate inputs
        if not cv_text or not keywords:
            return AnalysisResult(
                cv_filename="",
                job_description="",
                algorithm_used=algorithm,
                matched_keywords=[],
                missing_keywords=keywords.copy(),
                relevance_score=0.0,
                execution_time=0.0,
                comparison_count=0,
                total_keywords=len(keywords),
                timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
            )
        
        matched_keywords = []
        missing_keywords = []
        total_comparisons = 0
        total_execution_time = 0.0
        
        # Search for each keyword using the specified algorithm
        for keyword in keywords:
            keyword = keyword.strip()
            if not keyword:
                continue
                
            # Run the specified algorithm
            if algorithm == "Brute Force":
                result = self.algorithms.brute_force_search(cv_text, keyword, case_sensitive=case_sensitive)
            elif algorithm == "Rabin-Karp":
                result = self.algorithms.rabin_karp_search(cv_text, keyword, case_sensitive=case_sensitive)
            elif algorithm == "KMP":
                result = self.algorithms.kmp_search(cv_text, keyword, case_sensitive=case_sensitive)
            else:
                raise ValueError(f"Unknown algorithm: {algorithm}")
            
            # Record results
            total_comparisons += result.comparisons
            total_execution_time += result.execution_time
            
            if result.matches:
                matched_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(matched_keywords, keywords)
        
        execution_time = time.time() - start_time
        
        return AnalysisResult(
            cv_filename="",
            job_description="",
            algorithm_used=algorithm,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            relevance_score=relevance_score,
            execution_time=execution_time,
            comparison_count=total_comparisons,
            total_keywords=len(keywords),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
    
    def analyze_multiple_cvs(self, cv_files: List[str], job_description: JobDescription, 
                           algorithm: str, case_sensitive: bool = False) -> BatchAnalysisResult:
        """
        Analyze multiple CVs against a job description using specified algorithm.
        
        Args:
            cv_files: List of CV file paths
            job_description: Job description with keywords
            algorithm: Name of the algorithm to use
            
        Returns:
            BatchAnalysisResult object containing analysis results for all CVs
        """
        start_time = time.time()
        cv_results = []
        
        for cv_file in cv_files:
            try:
                # Load CV text (this would integrate with text extractors)
                cv_text = self._load_cv_text(cv_file)
                
                # Skip files that failed extraction (empty text)
                if not cv_text or not cv_text.strip():
                    # Create a result indicating extraction failure
                    error_result = AnalysisResult(
                        cv_filename=os.path.basename(cv_file),
                        job_description=job_description.title,
                        algorithm_used=algorithm,
                        matched_keywords=[],
                        missing_keywords=job_description.keywords.copy(),
                        relevance_score=0.0,
                        execution_time=0.0,
                        comparison_count=0,
                        total_keywords=len(job_description.keywords),
                        timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                    )
                    cv_results.append(error_result)
                    continue
                
                # Analyze the CV
                result = self.analyze_cv(cv_text, job_description.keywords, algorithm, case_sensitive=case_sensitive)
                result.cv_filename = os.path.basename(cv_file)
                result.job_description = job_description.title
                
                cv_results.append(result)
                
            except Exception:
                # Handle errors gracefully
                error_result = AnalysisResult(
                    cv_filename=os.path.basename(cv_file),
                    job_description=job_description.title,
                    algorithm_used=algorithm,
                    matched_keywords=[],
                    missing_keywords=job_description.keywords.copy(),
                    relevance_score=0.0,
                    execution_time=0.0,
                    comparison_count=0,
                    total_keywords=len(job_description.keywords),
                    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
                )
                cv_results.append(error_result)
        
        # Calculate batch statistics
        total_execution_time = time.time() - start_time
        valid_results = [r for r in cv_results if r.relevance_score > 0]
        average_relevance_score = (
            sum(r.relevance_score for r in valid_results) / len(valid_results)
            if valid_results else 0.0
        )
        
        batch_result = BatchAnalysisResult(
            job_description=job_description,
            algorithm_used=algorithm,
            cv_results=cv_results,
            total_execution_time=total_execution_time,
            average_relevance_score=average_relevance_score,
            total_cvs_analyzed=len(cv_files),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Store in history
        self.analysis_history.append(batch_result)
        
        return batch_result
    
    def compare_algorithms(self, cv_text: str, keywords: List[str]) -> Dict[str, AnalysisResult]:
        """
        Compare all three algorithms on the same CV text and keywords.
        
        Args:
            cv_text: The extracted text from the CV
            keywords: List of keywords to search for
            
        Returns:
            Dictionary mapping algorithm names to their AnalysisResult objects
        """
        algorithms = ["Brute Force", "Rabin-Karp", "KMP"]
        results = {}
        
        for algorithm in algorithms:
            result = self.analyze_cv(cv_text, keywords, algorithm)
            results[algorithm] = result
        
        return results
    
    def get_top_matching_cvs(self, batch_result: BatchAnalysisResult, 
                           top_n: int = 10) -> List[AnalysisResult]:
        """
        Get the top N CVs with highest relevance scores.
        
        Args:
            batch_result: Results from batch analysis
            top_n: Number of top CVs to return
            
        Returns:
            List of AnalysisResult objects sorted by relevance score
        """
        sorted_results = sorted(
            batch_result.cv_results,
            key=lambda x: x.relevance_score,
            reverse=True
        )
        
        return sorted_results[:top_n]
    
    def get_performance_metrics(self, batch_result: BatchAnalysisResult) -> Dict[str, Any]:
        """
        Extract performance metrics from batch analysis results.
        
        Args:
            batch_result: Results from batch analysis
            
        Returns:
            Dictionary containing performance metrics
        """
        metrics = {
            "algorithm": batch_result.algorithm_used,
            "total_cvs": batch_result.total_cvs_analyzed,
            "total_execution_time": batch_result.total_execution_time,
            "average_execution_time": (
                batch_result.total_execution_time / batch_result.total_cvs_analyzed
                if batch_result.total_cvs_analyzed > 0 else 0
            ),
            "average_relevance_score": batch_result.average_relevance_score,
            "total_comparisons": sum(r.comparison_count for r in batch_result.cv_results),
            "average_comparisons": (
                sum(r.comparison_count for r in batch_result.cv_results) / 
                batch_result.total_cvs_analyzed
                if batch_result.total_cvs_analyzed > 0 else 0
            ),
            "cv_distribution": {
                "high_match": len([r for r in batch_result.cv_results if r.relevance_score >= 0.7]),
                "medium_match": len([r for r in batch_result.cv_results if 0.3 <= r.relevance_score < 0.7]),
                "low_match": len([r for r in batch_result.cv_results if r.relevance_score < 0.3])
            }
        }
        
        return metrics
    
    def _calculate_relevance_score(self, matched_keywords: List[str], 
                                 total_keywords: List[str]) -> float:
        """
        Calculate relevance score based on matched keywords.
        
        Args:
            matched_keywords: List of keywords that were found
            total_keywords: List of all keywords to search for
            
        Returns:
            Relevance score between 0.0 and 1.0
        """
        if not total_keywords:
            return 0.0
        
        # Basic relevance score: percentage of keywords matched
        base_score = len(matched_keywords) / len(total_keywords)
        
        # Bonus for high keyword density (more matches = higher score)
        if len(matched_keywords) > 0:
            density_bonus = min(0.1, len(matched_keywords) * 0.01)
            base_score += density_bonus
        
        # Cap at 1.0
        return min(1.0, base_score)
    
    def _load_cv_text(self, file_path: str) -> str:
        """
        Load and extract text from CV file using appropriate extractors.
        
        Args:
            file_path: Path to the CV file
            
        Returns:
            Extracted text from the CV
        """
        try:
            # Cache lookup first to avoid repeated extraction across algorithms/runs
            if file_path in self.cv_cache:
                cached = self.cv_cache[file_path]
                if cached and isinstance(cached, CVData):
                    return cached.extracted_text
            # Import extractors
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from extractors.pdf_extractor import PDFExtractor
            from extractors.docx_extractor import DOCXExtractor
            
            pdf_extractor = PDFExtractor()
            docx_extractor = DOCXExtractor()
            
            # Determine file type and extract text
            if pdf_extractor.is_supported(file_path):
                result = pdf_extractor.extract_text(file_path)
                if result['success']:
                    text = result['text']
                    # Cache success
                    try:
                        self.cv_cache[file_path] = CVData(
                            filename=os.path.basename(file_path),
                            file_path=file_path,
                            extracted_text=text,
                            file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                            extraction_time=result.get('extraction_time', 0.0),
                            validation_status=True,
                        )
                    except Exception as e:
                        logging.getLogger(__name__).warning("Failed to cache PDF extraction result: %s", e, exc_info=True)
                    return text
                else:
                    print(f"PDF extraction failed for {file_path}: {result['error']}")
                    # Cache failure to avoid repeated attempts during same session
                    self.cv_cache[file_path] = CVData(
                        filename=os.path.basename(file_path),
                        file_path=file_path,
                        extracted_text="",
                        file_size=0,
                        extraction_time=result.get('extraction_time', 0.0),
                        validation_status=False,
                        error_message=str(result.get('error')),
                    )
                    return ""
            
            elif docx_extractor.is_supported(file_path):
                result = docx_extractor.extract_text(file_path)
                if result['success']:
                    text = result['text']
                    try:
                        self.cv_cache[file_path] = CVData(
                            filename=os.path.basename(file_path),
                            file_path=file_path,
                            extracted_text=text,
                            file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                            extraction_time=result.get('extraction_time', 0.0),
                            validation_status=True,
                        )
                    except Exception as e:
                        logging.getLogger(__name__).warning("Failed to cache DOCX extraction result: %s", e, exc_info=True)
                    return text
                else:
                    print(f"DOCX extraction failed for {file_path}: {result['error']}")
                    self.cv_cache[file_path] = CVData(
                        filename=os.path.basename(file_path),
                        file_path=file_path,
                        extracted_text="",
                        file_size=0,
                        extraction_time=result.get('extraction_time', 0.0),
                        validation_status=False,
                        error_message=str(result.get('error')),
                    )
                    return ""
            
            else:
                print(f"Unsupported file format: {file_path}")
                return ""
                
        except Exception as e:
            print(f"Error loading CV text from {file_path}: {e}")
            return ""
    
    def clear_cache(self):
        """Clear the CV text cache."""
        self.cv_cache.clear()
    
    def get_analysis_history(self) -> List[BatchAnalysisResult]:
        """Get the history of all analysis runs."""
        return self.analysis_history.copy()
    
    def export_results_to_csv(self, batch_result: BatchAnalysisResult, 
                            output_path: str) -> bool:
        """
        Export analysis results to CSV file.
        
        Args:
            batch_result: Results to export
            output_path: Path for the CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import csv
            
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'cv_filename', 'job_description', 'algorithm_used',
                    'matched_keywords', 'missing_keywords', 'relevance_score',
                    'execution_time', 'comparison_count', 'total_keywords', 'timestamp'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in batch_result.cv_results:
                    writer.writerow({
                        'cv_filename': result.cv_filename,
                        'job_description': result.job_description,
                        'algorithm_used': result.algorithm_used,
                        'matched_keywords': '; '.join(result.matched_keywords),
                        'missing_keywords': '; '.join(result.missing_keywords),
                        'relevance_score': result.relevance_score,
                        'execution_time': result.execution_time,
                        'comparison_count': result.comparison_count,
                        'total_keywords': result.total_keywords,
                        'timestamp': result.timestamp
                    })
            
            return True
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    
