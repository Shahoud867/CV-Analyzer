"""
Database Persistence Layer
Phase 3: Core Application Implementation

This module handles all database operations using SQLite for storing
job descriptions, analysis results, and application configuration.
"""

import sqlite3
import json
from typing import List, Dict, Any, Optional


class DatabaseManager:
    """
    SQLite database manager for CV analyzer application.
    Handles job descriptions, analysis results, and configuration storage.
    """
    
    def __init__(self, db_path: str = "cv_analyzer.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database tables and connection."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access
            self._create_tables()
        except Exception as e:
            print(f"Database initialization failed: {e}")
            raise
    
    def _create_tables(self):
        """Create database tables if they don't exist."""
        cursor = self.connection.cursor()
        
        # Job descriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_descriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                keywords TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cv_filename TEXT NOT NULL,
                job_description_id INTEGER,
                algorithm_used TEXT NOT NULL,
                relevance_score REAL,
                execution_time REAL,
                comparison_count INTEGER,
                matched_keywords TEXT,
                missing_keywords TEXT,
                total_keywords INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_description_id) REFERENCES job_descriptions (id)
            )
        """)
        
        # Batch analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batch_analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_description_id INTEGER,
                algorithm_used TEXT NOT NULL,
                total_cvs_analyzed INTEGER,
                total_execution_time REAL,
                average_relevance_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (job_description_id) REFERENCES job_descriptions (id)
            )
        """)
        
        # Application configuration table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # CV files metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cv_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_size INTEGER,
                extraction_time REAL,
                validation_status BOOLEAN,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.connection.commit()
    
    def add_job_description(self, title: str, description: str, keywords: List[str]) -> int:
        """
        Add a new job description to the database.
        
        Args:
            title: Job title
            description: Job description
            keywords: List of keywords/skills
            
        Returns:
            ID of the created job description
        """
        cursor = self.connection.cursor()
        
        keywords_json = json.dumps(keywords)
        
        cursor.execute("""
            INSERT INTO job_descriptions (title, description, keywords)
            VALUES (?, ?, ?)
        """, (title, description, keywords_json))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_job_description(self, job_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a job description by ID.
        
        Args:
            job_id: Job description ID
            
        Returns:
            Job description data or None if not found
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM job_descriptions WHERE id = ?
        """, (job_id,))
        
        row = cursor.fetchone()
        if row:
            data = dict(row)
            data['keywords'] = json.loads(data['keywords'])
            return data
        
        return None
    
    def get_all_job_descriptions(self) -> List[Dict[str, Any]]:
        """
        Get all job descriptions.
        
        Returns:
            List of job description data
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM job_descriptions ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        job_descriptions = []
        
        for row in rows:
            data = dict(row)
            data['keywords'] = json.loads(data['keywords'])
            job_descriptions.append(data)
        
        return job_descriptions
    
    def update_job_description(self, job_id: int, title: str, description: str, 
                             keywords: List[str]) -> bool:
        """
        Update an existing job description.
        
        Args:
            job_id: Job description ID
            title: New job title
            description: New job description
            keywords: New list of keywords
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            keywords_json = json.dumps(keywords)
            
            cursor.execute("""
                UPDATE job_descriptions 
                SET title = ?, description = ?, keywords = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (title, description, keywords_json, job_id))
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error updating job description: {e}")
            return False
    
    def delete_job_description(self, job_id: int) -> bool:
        """
        Delete a job description.
        
        Args:
            job_id: Job description ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            # Delete related analysis results first
            cursor.execute("""
                DELETE FROM analysis_results WHERE job_description_id = ?
            """, (job_id,))
            
            cursor.execute("""
                DELETE FROM batch_analysis_results WHERE job_description_id = ?
            """, (job_id,))
            
            # Delete the job description
            cursor.execute("""
                DELETE FROM job_descriptions WHERE id = ?
            """, (job_id,))
            
            self.connection.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error deleting job description: {e}")
            return False
    
    def save_analysis_result(self, cv_filename: str, job_description_id: int,
                           algorithm_used: str, relevance_score: float,
                           execution_time: float, comparison_count: int,
                           matched_keywords: List[str], missing_keywords: List[str],
                           total_keywords: int) -> int:
        """
        Save analysis result to database.
        
        Args:
            cv_filename: Name of the CV file
            job_description_id: ID of the job description used
            algorithm_used: Name of the algorithm used
            relevance_score: Calculated relevance score
            execution_time: Execution time in seconds
            comparison_count: Number of character comparisons made
            matched_keywords: List of matched keywords
            missing_keywords: List of missing keywords
            total_keywords: Total number of keywords searched
            
        Returns:
            ID of the saved analysis result
        """
        cursor = self.connection.cursor()
        
        matched_json = json.dumps(matched_keywords)
        missing_json = json.dumps(missing_keywords)
        
        cursor.execute("""
            INSERT INTO analysis_results 
            (cv_filename, job_description_id, algorithm_used, relevance_score,
             execution_time, comparison_count, matched_keywords, missing_keywords,
             total_keywords)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (cv_filename, job_description_id, algorithm_used, relevance_score,
              execution_time, comparison_count, matched_json, missing_json,
              total_keywords))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def save_batch_analysis_result(self, job_description_id: int, algorithm_used: str,
                                total_cvs_analyzed: int, total_execution_time: float,
                                average_relevance_score: float) -> int:
        """
        Save batch analysis result to database.
        
        Args:
            job_description_id: ID of the job description used
            algorithm_used: Name of the algorithm used
            total_cvs_analyzed: Total number of CVs analyzed
            total_execution_time: Total execution time
            average_relevance_score: Average relevance score
            
        Returns:
            ID of the saved batch result
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO batch_analysis_results 
            (job_description_id, algorithm_used, total_cvs_analyzed,
             total_execution_time, average_relevance_score)
            VALUES (?, ?, ?, ?, ?)
        """, (job_description_id, algorithm_used, total_cvs_analyzed,
              total_execution_time, average_relevance_score))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_analysis_results(self, job_description_id: Optional[int] = None,
                           algorithm: Optional[str] = None,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get analysis results with optional filtering.
        
        Args:
            job_description_id: Filter by job description ID
            algorithm: Filter by algorithm used
            limit: Maximum number of results to return
            
        Returns:
            List of analysis result data
        """
        cursor = self.connection.cursor()
        
        query = """
            SELECT ar.*, jd.title as job_title
            FROM analysis_results ar
            LEFT JOIN job_descriptions jd ON ar.job_description_id = jd.id
            WHERE 1=1
        """
        params = []
        
        if job_description_id:
            query += " AND ar.job_description_id = ?"
            params.append(job_description_id)
        
        if algorithm:
            query += " AND ar.algorithm_used = ?"
            params.append(algorithm)
        
        query += " ORDER BY ar.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            data = dict(row)
            data['matched_keywords'] = json.loads(data['matched_keywords'])
            data['missing_keywords'] = json.loads(data['missing_keywords'])
            results.append(data)
        
        return results
    
    def get_performance_statistics(self) -> Dict[str, Any]:
        """
        Get performance statistics from analysis results.
        
        Returns:
            Dictionary containing performance statistics
        """
        cursor = self.connection.cursor()
        
        # Overall statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_analyses,
                AVG(relevance_score) as avg_relevance_score,
                AVG(execution_time) as avg_execution_time,
                AVG(comparison_count) as avg_comparison_count
            FROM analysis_results
        """)
        
        overall_stats = dict(cursor.fetchone())
        
        # Algorithm-specific statistics
        cursor.execute("""
            SELECT 
                algorithm_used,
                COUNT(*) as count,
                AVG(relevance_score) as avg_relevance_score,
                AVG(execution_time) as avg_execution_time,
                AVG(comparison_count) as avg_comparison_count
            FROM analysis_results
            GROUP BY algorithm_used
        """)
        
        algorithm_stats = []
        for row in cursor.fetchall():
            algorithm_stats.append(dict(row))
        
        # Job description statistics
        cursor.execute("""
            SELECT 
                jd.title,
                COUNT(ar.id) as analysis_count,
                AVG(ar.relevance_score) as avg_relevance_score
            FROM job_descriptions jd
            LEFT JOIN analysis_results ar ON jd.id = ar.job_description_id
            GROUP BY jd.id, jd.title
            ORDER BY analysis_count DESC
        """)
        
        job_stats = []
        for row in cursor.fetchall():
            job_stats.append(dict(row))
        
        return {
            'overall': overall_stats,
            'algorithms': algorithm_stats,
            'job_descriptions': job_stats
        }
    
    def save_cv_file_metadata(self, filename: str, file_path: str, file_size: int,
                            extraction_time: float, validation_status: bool,
                            error_message: Optional[str] = None) -> int:
        """
        Save CV file metadata to database.
        
        Args:
            filename: Name of the CV file
            file_path: Full path to the file
            file_size: Size of the file in bytes
            extraction_time: Time taken to extract text
            validation_status: Whether file validation passed
            error_message: Error message if validation failed
            
        Returns:
            ID of the saved CV file record
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO cv_files 
            (filename, file_path, file_size, extraction_time, validation_status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (filename, file_path, file_size, extraction_time, validation_status, error_message))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_cv_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get CV file metadata.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of CV file metadata
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT * FROM cv_files 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def set_config(self, key: str, value: str) -> bool:
        """
        Set application configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO app_config (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            
            self.connection.commit()
            return True
            
        except Exception as e:
            print(f"Error setting config: {e}")
            return False
    
    def get_config(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get application configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT value FROM app_config WHERE key = ?
        """, (key,))
        
        row = cursor.fetchone()
        return row['value'] if row else default
    
    def get_all_config(self) -> Dict[str, str]:
        """
        Get all configuration values.
        
        Returns:
            Dictionary of all configuration key-value pairs
        """
        cursor = self.connection.cursor()
        
        cursor.execute("""
            SELECT key, value FROM app_config
        """)
        
        rows = cursor.fetchall()
        return {row['key']: row['value'] for row in rows}
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    
