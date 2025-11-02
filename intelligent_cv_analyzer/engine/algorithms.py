"""
String Matching Algorithms Implementation
Phase 3: Core Application Implementation

This module contains the implementation of three string matching algorithms:
1. Brute Force (Naive Pattern Matching)
2. Rabin-Karp Algorithm
3. Knuth-Morris-Pratt (KMP) Algorithm

Each algorithm is optimized for CV analysis with case-insensitive matching
and comprehensive performance monitoring.
"""

import time
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class SearchResult:
    """Data class to store search results and performance metrics."""
    matches: List[int]  # List of positions where pattern was found
    comparisons: int    # Total number of character comparisons made
    execution_time: float  # Execution time in seconds
    algorithm_name: str    # Name of the algorithm used
    pattern_length: int    # Length of the search pattern
    text_length: int       # Length of the text being searched


class StringMatchingAlgorithms:
    """
    Implementation of three string matching algorithms for CV analysis.
    
    All algorithms support case-insensitive matching and provide detailed
    performance metrics for comparative analysis.
    """
    
    def __init__(self):
        """Initialize the algorithms with default parameters."""
        self.base = 256  # Base for Rabin-Karp hash function
        self.prime = 101  # Prime number for Rabin-Karp modulo operation
    
    def brute_force_search(self, text: str, pattern: str, case_sensitive: bool = False) -> SearchResult:
        """
        Brute Force (Naive) Pattern Matching Algorithm.
        
        Time Complexity: O(n*m) where n=text length, m=pattern length
        Space Complexity: O(1)
        
        Args:
            text: The text to search in
            pattern: The pattern to search for
            case_sensitive: Whether to perform case-sensitive matching
            
        Returns:
            SearchResult object containing matches and performance metrics
        """
        start_time = time.time()
        
        # Normalize text and pattern for case-insensitive matching
        if not case_sensitive:
            text = text.lower()
            pattern = pattern.lower()
        
        n = len(text)
        m = len(pattern)
        matches = []
        comparisons = 0
        
        # Edge case: pattern is longer than text
        if m > n:
            return SearchResult(
                matches=[],
                comparisons=0,
                execution_time=time.time() - start_time,
                algorithm_name="Brute Force",
                pattern_length=m,
                text_length=n
            )
        
        # Main algorithm: check each possible starting position
        for i in range(n - m + 1):
            j = 0
            # Compare characters until mismatch or pattern completion
            while j < m and text[i + j] == pattern[j]:
                comparisons += 1
                j += 1
            
            # Count the mismatch comparison (if any)
            if j < m:
                comparisons += 1
            
            # If all characters matched, we found a match
            if j == m:
                matches.append(i)
        
        execution_time = time.time() - start_time
        
        return SearchResult(
            matches=matches,
            comparisons=comparisons,
            execution_time=execution_time,
            algorithm_name="Brute Force",
            pattern_length=m,
            text_length=n
        )
    
    def rabin_karp_search(self, text: str, pattern: str, case_sensitive: bool = False) -> SearchResult:
        """
        Rabin-Karp Algorithm using rolling hash.
        
        Time Complexity: O(n+m) average case, O(n*m) worst case
        Space Complexity: O(1)
        
        Args:
            text: The text to search in
            pattern: The pattern to search for
            case_sensitive: Whether to perform case-sensitive matching
            
        Returns:
            SearchResult object containing matches and performance metrics
        """
        start_time = time.time()
        
        # Normalize text and pattern for case-insensitive matching
        if not case_sensitive:
            text = text.lower()
            pattern = pattern.lower()
        
        n = len(text)
        m = len(pattern)
        matches = []
        comparisons = 0
        hash_collisions = 0
        
        # Edge case: pattern is longer than text
        if m > n:
            return SearchResult(
                matches=[],
                comparisons=0,
                execution_time=time.time() - start_time,
                algorithm_name="Rabin-Karp",
                pattern_length=m,
                text_length=n
            )
        
        # Calculate hash of pattern and first window of text
        pattern_hash = 0
        text_hash = 0
        h = 1
        
        # Calculate h = base^(m-1) mod prime
        for i in range(m - 1):
            h = (h * self.base) % self.prime
        
        # Calculate initial hash values
        for i in range(m):
            pattern_hash = (self.base * pattern_hash + ord(pattern[i])) % self.prime
            text_hash = (self.base * text_hash + ord(text[i])) % self.prime
        
        # Slide the pattern over text
        for i in range(n - m + 1):
            # Check if hash values match
            if pattern_hash == text_hash:
                # Verify with character-by-character comparison
                j = 0
                while j < m and text[i + j] == pattern[j]:
                    comparisons += 1
                    j += 1
                
                # Count the mismatch comparison (if any)
                if j < m:
                    comparisons += 1
                
                if j == m:
                    matches.append(i)
                else:
                    hash_collisions += 1
            
            # Calculate hash for next window
            if i < n - m:
                text_hash = (self.base * (text_hash - ord(text[i]) * h) + ord(text[i + m])) % self.prime
                # Ensure positive hash value
                if text_hash < 0:
                    text_hash = text_hash + self.prime
        
        execution_time = time.time() - start_time
        
        return SearchResult(
            matches=matches,
            comparisons=comparisons,
            execution_time=execution_time,
            algorithm_name="Rabin-Karp",
            pattern_length=m,
            text_length=n
        )
    
    def kmp_search(self, text: str, pattern: str, case_sensitive: bool = False) -> SearchResult:
        """
        Knuth-Morris-Pratt (KMP) Algorithm with failure function.
        
        Time Complexity: O(n+m) for both preprocessing and matching
        Space Complexity: O(m) for the failure function
        
        Args:
            text: The text to search in
            pattern: The pattern to search for
            case_sensitive: Whether to perform case-sensitive matching
            
        Returns:
            SearchResult object containing matches and performance metrics
        """
        start_time = time.time()
        
        # Normalize text and pattern for case-insensitive matching
        if not case_sensitive:
            text = text.lower()
            pattern = pattern.lower()
        
        n = len(text)
        m = len(pattern)
        matches = []
        comparisons = 0
        
        # Edge case: pattern is longer than text
        if m > n:
            return SearchResult(
                matches=[],
                comparisons=0,
                execution_time=time.time() - start_time,
                algorithm_name="KMP",
                pattern_length=m,
                text_length=n
            )
        
        # Build failure function (LPS array)
        lps = self._build_failure_function(pattern)
        
        i = 0  # Index for text
        j = 0  # Index for pattern
        
        while i < n:
            if text[i] == pattern[j]:
                comparisons += 1
                i += 1
                j += 1
            
            if j == m:
                matches.append(i - j)
                j = lps[j - 1]
            elif i < n and text[i] != pattern[j]:
                comparisons += 1
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        
        execution_time = time.time() - start_time
        
        return SearchResult(
            matches=matches,
            comparisons=comparisons,
            execution_time=execution_time,
            algorithm_name="KMP",
            pattern_length=m,
            text_length=n
        )
    
    def _build_failure_function(self, pattern: str) -> List[int]:
        """
        Build the failure function (LPS array) for KMP algorithm.
        
        LPS[i] = length of the longest proper prefix of pattern[0..i]
        that is also a suffix of pattern[0..i]
        
        Args:
            pattern: The pattern string
            
        Returns:
            List of integers representing the failure function
        """
        m = len(pattern)
        lps = [0] * m
        length = 0  # Length of previous longest prefix suffix
        i = 1
        
        while i < m:
            if pattern[i] == pattern[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        
        return lps
    
    def compare_algorithms(self, text: str, pattern: str, case_sensitive: bool = False) -> Dict[str, SearchResult]:
        """
        Run all three algorithms on the same text and pattern for comparison.
        
        Args:
            text: The text to search in
            pattern: The pattern to search for
            case_sensitive: Whether to perform case-sensitive matching
            
        Returns:
            Dictionary mapping algorithm names to their SearchResult objects
        """
        results = {}
        
        # Run all three algorithms
        results["Brute Force"] = self.brute_force_search(text, pattern, case_sensitive)
        results["Rabin-Karp"] = self.rabin_karp_search(text, pattern, case_sensitive)
        results["KMP"] = self.kmp_search(text, pattern, case_sensitive)
        
        return results
    
    def get_performance_summary(self, results: Dict[str, SearchResult]) -> Dict[str, Any]:
        """
        Generate a performance summary comparing all algorithms.
        
        Args:
            results: Dictionary of SearchResult objects from compare_algorithms
            
        Returns:
            Dictionary containing performance metrics and analysis
        """
        summary = {
            "execution_times": {},
            "comparison_counts": {},
            "match_counts": {},
            "efficiency_ranking": [],
            "performance_analysis": {}
        }
        
        # Extract metrics
        for algo_name, result in results.items():
            summary["execution_times"][algo_name] = result.execution_time
            summary["comparison_counts"][algo_name] = result.comparisons
            summary["match_counts"][algo_name] = len(result.matches)
        
        # Rank algorithms by execution time (ascending = fastest first)
        summary["efficiency_ranking"] = sorted(
            summary["execution_times"].items(),
            key=lambda x: x[1]
        )
        
        # Performance analysis
        fastest_time = min(summary["execution_times"].values())
        for algo_name, exec_time in summary["execution_times"].items():
            speedup = exec_time / fastest_time if fastest_time > 0 else 1
            summary["performance_analysis"][algo_name] = {
                "execution_time": exec_time,
                "speedup_factor": speedup,
                "comparisons": summary["comparison_counts"][algo_name],
                "matches_found": summary["match_counts"][algo_name]
            }
        
        return summary


# Example usage and testing
if __name__ == "__main__":
    # Test the algorithms with sample data
    algorithms = StringMatchingAlgorithms()
    
    # Sample CV text (simplified)
    sample_text = """
    John Smith is a software engineer with 5 years of experience in Python programming.
    He has worked with Django, Flask, and React frameworks. His skills include
    machine learning, data analysis, and database design. He is proficient in
    SQL, MongoDB, and PostgreSQL. He has experience with agile development
    methodologies and version control using Git.
    """
    
    # Sample keywords to search for
    keywords = ["Python", "React", "machine learning", "SQL", "Git"]
    
    print("=== String Matching Algorithms Test ===\n")
    
    for keyword in keywords:
        print(f"Searching for: '{keyword}'")
        print("-" * 50)
        
        results = algorithms.compare_algorithms(sample_text, keyword)
        
        for algo_name, result in results.items():
            print(f"{algo_name:12}: {len(result.matches):2} matches, "
                  f"{result.comparisons:3} comparisons, "
                  f"{result.execution_time*1000:6.2f}ms")
        
        print()
    
    # Performance summary
    print("=== Performance Summary ===")
    results = algorithms.compare_algorithms(sample_text, "Python")
    summary = algorithms.get_performance_summary(results)
    
    print("Execution Times:")
    for algo_name, exec_time in summary["execution_times"].items():
        print(f"  {algo_name:12}: {exec_time*1000:6.2f}ms")
    
    print("\nEfficiency Ranking (fastest first):")
    for i, (algo_name, exec_time) in enumerate(summary["efficiency_ranking"], 1):
        print(f"  {i}. {algo_name:12}: {exec_time*1000:6.2f}ms")
