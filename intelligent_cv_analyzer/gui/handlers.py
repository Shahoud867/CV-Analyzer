"""
GUI Event Handlers and Functionality
Phase 3: Desktop Application Implementation

This module contains all the event handlers and functionality for the GUI.
"""

import os
import time
import logging

try:
    from PyQt5.QtWidgets import (
        QFileDialog, QMessageBox, QTableWidgetItem, QListWidgetItem,
    )
    from PyQt5.QtCore import Qt, QMutex
except ImportError:
    pass

# Import our modules
from engine.analyzer import JobDescription
from extractors.pdf_extractor import PDFExtractor
from extractors.docx_extractor import DOCXExtractor
from gui.workers import AnalysisWorker, CompareAllWorker


logger = logging.getLogger(__name__)


class MainWindowHandlers:
    """Event handlers and functionality for the main window."""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.analysis_worker = None
        self.pdf_extractor = PDFExtractor()
        self.docx_extractor = DOCXExtractor()
        # Mutex to protect access to shared analysis_results across threads
        try:
            self.results_mutex = QMutex()
        except Exception:
            self.results_mutex = None
        
        # Store references to handler methods in main window for easy access
        main_window.load_cv_files = self.load_cv_files
        main_window.load_dataset_folder = self.load_dataset_folder
        main_window.clear_cv_files = self.clear_cv_files
        main_window.on_file_selection_changed = self.on_file_selection_changed
        main_window.refresh_job_descriptions = self.refresh_job_descriptions
        main_window.on_job_selection_changed = self.on_job_selection_changed
        main_window.save_job_description = self.save_job_description
        main_window.create_new_job = self.create_new_job
        main_window.delete_job_description = self.delete_job_description
        main_window.start_analysis = self.start_analysis
        main_window.stop_analysis = self.stop_analysis
        main_window.export_results_csv = self.export_results_csv
        main_window.generate_report = self.generate_report
        # Convenience: status log appender
        main_window.append_status = self.append_status
    
    # File Management Methods
    def load_cv_files(self):
        """Load individual CV files."""
        files, _ = QFileDialog.getOpenFileNames(
            self.main_window,
            "Select CV Files",
            "",
            "CV Files (*.pdf *.docx);;PDF Files (*.pdf);;Word Files (*.docx);;All Files (*.*)"
        )
        
        if files:
            # Filter out legacy .doc files and warn user
            supported_files = []
            unsupported_doc_files = []
            
            for file_path in files:
                # Check for legacy .doc (but not .docx)
                if file_path.lower().endswith('.doc') and not file_path.lower().endswith('.docx'):
                    unsupported_doc_files.append(os.path.basename(file_path))
                elif file_path.lower().endswith(('.pdf', '.docx')):
                    supported_files.append(file_path)
                else:
                    # Unknown format
                    unsupported_doc_files.append(os.path.basename(file_path))
            
            # Add supported files
            if supported_files:
                self.main_window.cv_files.extend(supported_files)
                self.update_file_list()
                self.update_file_status()
                self.main_window.status_bar.showMessage(f"Loaded {len(supported_files)} CV files")
            
            # Warn about unsupported files
            if unsupported_doc_files:
                warning_msg = f"The following {len(unsupported_doc_files)} file(s) were skipped:\n\n"
                warning_msg += "\n".join(unsupported_doc_files[:10])
                if len(unsupported_doc_files) > 10:
                    warning_msg += f"\n... and {len(unsupported_doc_files) - 10} more"
                warning_msg += "\n\n⚠ Legacy .doc format is not supported."
                warning_msg += "\nOnly .docx (Office 2007+) and .pdf files are supported."
                warning_msg += "\n\nPlease convert .doc files to .docx using:"
                warning_msg += "\n • Microsoft Word: Open → Save As → .docx"
                warning_msg += "\n • LibreOffice: Open → Save As → .docx"
                
                QMessageBox.warning(
                    self.main_window,
                    "Unsupported File Format",
                    warning_msg
                )
                logger.warning(f"Rejected {len(unsupported_doc_files)} legacy .doc files: {unsupported_doc_files}")
    
    def load_dataset_folder(self):
        """Load entire DataSet folder."""
        folder = QFileDialog.getExistingDirectory(
            self.main_window,
            "Select DataSet Folder",
            "data/cvs"
        )
        
        if folder:
            # Scan folder for CV files
            supported_files = []
            unsupported_doc_files = []
            
            for root, dirs, files in os.walk(folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check for legacy .doc (but not .docx)
                    if file.lower().endswith('.doc') and not file.lower().endswith('.docx'):
                        unsupported_doc_files.append(file)
                    elif file.lower().endswith(('.pdf', '.docx')):
                        supported_files.append(file_path)
            
            # Add supported files
            if supported_files:
                self.main_window.cv_files.extend(supported_files)
                self.update_file_list()
                self.update_file_status()
                
                # Build status message
                status_msg = f"Loaded {len(supported_files)} CV files from DataSet"
                if unsupported_doc_files:
                    status_msg += f" ({len(unsupported_doc_files)} legacy .doc files skipped)"
                
                self.main_window.status_bar.showMessage(status_msg)
                
                # Show detailed warning if legacy files found
                if unsupported_doc_files:
                    warning_msg = f"⚠ Skipped {len(unsupported_doc_files)} legacy .doc file(s):\n\n"
                    warning_msg += "\n".join(unsupported_doc_files[:10])
                    if len(unsupported_doc_files) > 10:
                        warning_msg += f"\n... and {len(unsupported_doc_files) - 10} more"
                    warning_msg += "\n\nLegacy .doc format is NOT supported."
                    warning_msg += "\nOnly .docx (Office 2007+) and .pdf files can be analyzed."
                    warning_msg += "\n\nTo convert .doc files to .docx:"
                    warning_msg += "\n • Microsoft Word: Open → Save As → Word Document (.docx)"
                    warning_msg += "\n • LibreOffice Writer: Open → Save As → .docx format"
                    warning_msg += "\n • Online: Use CloudConvert or similar free converters"
                    
                    QMessageBox.warning(
                        self.main_window,
                        "Unsupported File Format Detected",
                        warning_msg
                    )
                    logger.warning(f"Rejected {len(unsupported_doc_files)} legacy .doc files from dataset: {unsupported_doc_files}")
            else:
                if unsupported_doc_files:
                    # Only unsupported files found
                    QMessageBox.warning(
                        self.main_window,
                        "No Supported Files Found",
                        f"Found {len(unsupported_doc_files)} legacy .doc file(s), but this format is not supported.\n\n"
                        "Only .pdf and .docx (Office 2007+) files can be analyzed.\n\n"
                        "Please convert .doc files to .docx format."
                    )
                else:
                    # No files at all
                    QMessageBox.warning(self.main_window, "No Files", "No CV files found in the selected folder.")
    
    def clear_cv_files(self):
        """Clear all loaded CV files."""
        reply = QMessageBox.question(
            self.main_window,
            "Clear Files",
            "Are you sure you want to clear all loaded CV files?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.main_window.cv_files.clear()
            self.update_file_list()
            self.update_file_status()
            self.main_window.file_preview.clear()
            self.main_window.status_bar.showMessage("All CV files cleared")
    
    def update_file_list(self):
        """Update the file list widget."""
        self.main_window.file_list.clear()
        
        for file_path in self.main_window.cv_files:
            filename = os.path.basename(file_path)
            file_size = self.get_file_size(file_path)
            
            item = QListWidgetItem(f"{filename} ({file_size})")
            item.setData(Qt.UserRole, file_path)
            self.main_window.file_list.addItem(item)
    
    def update_file_status(self):
        """Update file status labels."""
        file_count = len(self.main_window.cv_files)
        total_size = sum(self.get_file_size_mb(f) for f in self.main_window.cv_files)
        
        self.main_window.file_count_label.setText(f"Files loaded: {file_count}")
        self.main_window.file_size_label.setText(f"Total size: {total_size:.1f} MB")
        self.main_window.files_status_label.setText(f"Files: {file_count} loaded")
    
    def get_file_size(self, file_path):
        """Get human-readable file size."""
        try:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            else:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
        except Exception:
            return "Unknown"
    
    def get_file_size_mb(self, file_path):
        """Get file size in MB."""
        try:
            return os.path.getsize(file_path) / (1024 * 1024)
        except Exception:
            return 0
    
    def on_file_selection_changed(self):
        """Handle file selection change."""
        current_item = self.main_window.file_list.currentItem()
        if current_item:
            file_path = current_item.data(Qt.UserRole)
            self.preview_file_content(file_path)
    
    def preview_file_content(self, file_path):
        """Preview file content in the text area."""
        try:
            filename = os.path.basename(file_path)
            
            # Extract text based on file type
            if file_path.lower().endswith('.pdf'):
                result = self.pdf_extractor.extract_text(file_path)
            elif file_path.lower().endswith(('.docx', '.doc')):
                result = self.docx_extractor.extract_text(file_path)
            else:
                self.main_window.file_preview.setText("Unsupported file format")
                return
            
            if result['success']:
                # Show first 500 characters
                preview_text = result['text'][:500]
                if len(result['text']) > 500:
                    preview_text += "..."
                
                self.main_window.file_preview.setText(f"File: {filename}\n\n{preview_text}")
            else:
                self.main_window.file_preview.setText(f"Error extracting text from {filename}:\n{result['error']}")
                
        except Exception as e:
            self.main_window.file_preview.setText(f"Error previewing file: {str(e)}")
    
    # Job Description Methods
    def refresh_job_descriptions(self):
        """Refresh job descriptions from database."""
        try:
            job_descriptions = self.main_window.db.get_all_job_descriptions()
            
            self.main_window.job_combo.clear()
            for job in job_descriptions:
                self.main_window.job_combo.addItem(job['title'], job['id'])
            
            self.main_window.status_bar.showMessage(f"Loaded {len(job_descriptions)} job descriptions")
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to load job descriptions: {str(e)}")
    
    def on_job_selection_changed(self):
        """Handle job description selection change."""
        current_text = self.main_window.job_combo.currentText()
        if current_text:
            try:
                job_id = self.main_window.job_combo.currentData()
                job_data = self.main_window.db.get_job_description(job_id)
                
                if job_data:
                    self.main_window.job_title_edit.setText(job_data['title'])
                    self.main_window.job_desc_edit.setText(job_data['description'] or "")
                    self.main_window.keywords_edit.setText(", ".join(job_data['keywords']))
                    
                    # Store current job description
                    self.main_window.current_job_description = JobDescription(
                        id=job_data['id'],
                        title=job_data['title'],
                        description=job_data['description'],
                        keywords=job_data['keywords'],
                        created_at=job_data['created_at']
                    )
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to load job description: {str(e)}")
    
    def save_job_description(self):
        """Save job description to database."""
        try:
            title = self.main_window.job_title_edit.text().strip()
            description = self.main_window.job_desc_edit.toPlainText().strip()
            keywords_text = self.main_window.keywords_edit.toPlainText().strip()
            
            if not title:
                QMessageBox.warning(self.main_window, "Validation Error", "Job title is required.")
                return
            
            if not keywords_text:
                QMessageBox.warning(self.main_window, "Validation Error", "Keywords are required.")
                return
            
            # Parse keywords
            keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]
            
            if not keywords:
                QMessageBox.warning(self.main_window, "Validation Error", "At least one keyword is required.")
                return
            
            # Save to database
            job_id = self.main_window.db.add_job_description(title, description, keywords)
            
            QMessageBox.information(self.main_window, "Success", f"Job description saved with ID: {job_id}")
            
            # Refresh the combo box
            self.refresh_job_descriptions()
            
            # Select the newly created job
            index = self.main_window.job_combo.findData(job_id)
            if index >= 0:
                self.main_window.job_combo.setCurrentIndex(index)
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to save job description: {str(e)}")
    
    def create_new_job(self):
        """Create a new job description."""
        self.main_window.job_title_edit.clear()
        self.main_window.job_desc_edit.clear()
        self.main_window.keywords_edit.clear()
        self.main_window.job_combo.setCurrentIndex(-1)
        self.main_window.current_job_description = None
    
    def delete_job_description(self):
        """Delete selected job description."""
        if not self.main_window.current_job_description:
            QMessageBox.warning(self.main_window, "No Selection", "Please select a job description to delete.")
            return
        
        reply = QMessageBox.question(
            self.main_window,
            "Delete Job Description",
            f"Are you sure you want to delete '{self.main_window.current_job_description.title}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.main_window.db.delete_job_description(self.main_window.current_job_description.id)
                
                if success:
                    QMessageBox.information(self.main_window, "Success", "Job description deleted successfully.")
                    self.refresh_job_descriptions()
                    self.create_new_job()
                else:
                    QMessageBox.warning(self.main_window, "Error", "Failed to delete job description.")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to delete job description: {str(e)}")
    
    # Demo-only method removed: load_sample_job_descriptions
    
    # Analysis Methods
    def start_analysis(self):
        """Start CV analysis."""
        # Validate inputs
        if not self.main_window.cv_files:
            QMessageBox.warning(self.main_window, "No Files", "Please load CV files first.")
            return
        
        if not self.main_window.current_job_description:
            QMessageBox.warning(self.main_window, "No Job Description", "Please select a job description.")
            return
        
        algorithm = self.main_window.algorithm_combo.currentText()
        if algorithm == "Compare All":
            # Run analysis with all algorithms
            self.run_comparative_analysis()
        else:
            # Run analysis with single algorithm
            self.run_single_analysis(algorithm)
        # Log status
        try:
            self.append_status(
                f"Starting analysis • Algorithm: {algorithm} • Files: {len(self.main_window.cv_files)} • Job: "
                f"{self.main_window.current_job_description.title if self.main_window.current_job_description else ''}"
            )
        except Exception as e:
            logger.warning("Failed to append start analysis status: %s", e, exc_info=True)
    
    def run_single_analysis(self, algorithm):
        """Run analysis with a single algorithm."""
        try:
            # Clean up any existing worker first
            if self.analysis_worker is not None:
                if self.analysis_worker.isRunning():
                    self.analysis_worker.requestInterruption()
                    self.analysis_worker.wait(2000)
                    if self.analysis_worker.isRunning():
                        self.analysis_worker.terminate()
                        self.analysis_worker.wait()
                self.analysis_worker.deleteLater()
                self.analysis_worker = None
            
            # Read case sensitivity from UI
            cs = False
            try:
                cs = bool(self.main_window.case_sensitive_check.isChecked())
            except Exception:
                cs = False
            
            # Create worker thread
            self.analysis_worker = AnalysisWorker(
                self.main_window.analyzer,
                self.main_window.cv_files,
                self.main_window.current_job_description,
                algorithm,
                case_sensitive=cs,
            )
            
            # Connect custom signals to handlers
            self.analysis_worker.analysisFinished.connect(
                lambda batch_result: self.on_analysis_completed({
                    'batch_result': batch_result,
                    'total_files': len(self.main_window.cv_files),
                    'algorithm': algorithm,
                    'job_title': self.main_window.current_job_description.title if self.main_window.current_job_description else ''
                })
            )
            # Progress updates (coarse)
            try:
                self.analysis_worker.progress.connect(self._on_single_progress)
            except Exception as e:
                logger.warning("Failed to connect progress signal: %s", e, exc_info=True)
            self.analysis_worker.error.connect(self.on_analysis_error)
            
            # Connect QThread's built-in finished signal for automatic cleanup
            self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)
            # Ensure we clear our reference when the QObject is destroyed
            try:
                self.analysis_worker.destroyed.connect(lambda: setattr(self, 'analysis_worker', None))
            except Exception as e:
                logger.warning("Failed to connect destroyed signal for analysis worker: %s", e, exc_info=True)
            
            # Update UI
            self.main_window.start_analysis_btn.setEnabled(False)
            self.main_window.stop_analysis_btn.setEnabled(True)
            self.main_window.progress_bar.setVisible(True)
            self.main_window.progress_label.setText(f"Running {algorithm} analysis...")
            
            # Start analysis
            self.analysis_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to start analysis: {str(e)}")

    def _on_single_progress(self, current: int, total: int):
        """Update UI for single analysis progress and append to status log."""
        try:
            self.main_window.progress_bar.setMaximum(max(1, total))
            self.main_window.progress_bar.setValue(current)
            self.main_window.progress_label.setText(f"Running analysis... ({current}/{total})")
            if current == 0:
                self.append_status("Preparing analysis...")
        except Exception as e:
            logger.warning("Failed to update single analysis progress: %s", e, exc_info=True)
    
    def run_comparative_analysis(self):
        """Run analysis with all algorithms for comparison in a background thread."""
        # Clean up any existing worker first
        if self.analysis_worker is not None:
            try:
                if self.analysis_worker.isRunning():
                    self.analysis_worker.requestInterruption()
                    self.analysis_worker.wait(2000)
                    if self.analysis_worker.isRunning():
                        self.analysis_worker.terminate()
                        self.analysis_worker.wait()
            except Exception as e:
                logger.warning("Error stopping existing worker before comparative analysis: %s", e, exc_info=True)
            try:
                self.analysis_worker.deleteLater()
            except Exception as e:
                logger.warning("Error deleting previous worker: %s", e, exc_info=True)
            self.analysis_worker = None

        # Create and start compare-all worker
        cs = False
        try:
            cs = bool(self.main_window.case_sensitive_check.isChecked())
        except Exception as e:
            logger.warning("Failed to read case sensitivity checkbox: %s", e, exc_info=True)
            cs = False
        
        self.analysis_worker = CompareAllWorker(
            self.main_window.analyzer,
            self.main_window.cv_files,
            self.main_window.current_job_description,
            case_sensitive=cs,
        )

        # Connect signals
        self.analysis_worker.progress.connect(self._on_compare_progress)
        self.analysis_worker.error.connect(self.on_analysis_error)
        self.analysis_worker.compareFinished.connect(self._on_compare_all_finished)
        self.analysis_worker.finished.connect(self.analysis_worker.deleteLater)
        try:
            self.analysis_worker.destroyed.connect(lambda: setattr(self, 'analysis_worker', None))
        except Exception as e:
            logger.warning("Failed to connect destroyed signal for compare worker: %s", e, exc_info=True)

        # Update UI
        self.main_window.start_analysis_btn.setEnabled(False)
        self.main_window.stop_analysis_btn.setEnabled(True)
        self.main_window.progress_bar.setVisible(True)
        self.main_window.progress_label.setText("Starting comparative analysis...")

        self.analysis_worker.start()

    def _on_compare_all_finished(self, results_by_algo: dict):
        """Handle completion of compare-all worker."""
        try:
            # Store a snapshot of results in a thread-safe manner
            if getattr(self, 'results_mutex', None):
                self.results_mutex.lock()
            try:
                # Create a shallow copy to avoid external mutation after assignment
                self.main_window.analysis_results = dict(results_by_algo) if results_by_algo else {}
            finally:
                if getattr(self, 'results_mutex', None):
                    self.results_mutex.unlock()
            
            # Save all algorithm results to database
            try:
                for algo, batch_result in results_by_algo.items():
                    self._save_results_to_database(batch_result)
                logger.info("Comparative analysis results saved to database")
            except Exception as e:
                logger.error("Failed to save comparative results to database: %s", e, exc_info=True)
                # Don't block UI update if DB save fails
            
            # Update UI tables
            self.update_results_tab_comparative()
            self.main_window.progress_label.setText("Comparative analysis completed!")
            # Log summary with best algorithm by total time
            try:
                best_algo, best_batch = min(results_by_algo.items(), key=lambda kv: kv[1].total_execution_time)
                self.append_status(
                    f"Compare All completed • Best: {best_algo} in {best_batch.total_execution_time:.3f}s"
                )
            except Exception as e:
                logger.warning("Failed to compute or log best algorithm summary: %s", e, exc_info=True)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to process comparative results: {e}")
        finally:
            # Reset UI
            self.main_window.start_analysis_btn.setEnabled(True)
            self.main_window.stop_analysis_btn.setEnabled(False)
            self.main_window.progress_bar.setVisible(False)

    def _on_compare_progress(self, idx: int, total: int):
        """Progress callback for compare-all; updates UI and status log."""
        try:
            self.main_window.progress_bar.setMaximum(total)
            self.main_window.progress_bar.setValue(idx - 1)
            self.main_window.progress_label.setText(f"Running comparative analysis... ({idx}/{total})")
            # Append which algorithm is running
            try:
                algo = self.analysis_worker.algorithms[idx - 1] if hasattr(self.analysis_worker, 'algorithms') else f"{idx}/{total}"
                self.append_status(f"Running {algo}...")
            except Exception as e:
                logger.warning("Failed to append running algorithm status: %s", e, exc_info=True)
        except Exception as e:
            logger.warning("Failed to update comparative progress: %s", e, exc_info=True)
    
    def stop_analysis(self):
        """Stop running analysis."""
        try:
            worker = self.analysis_worker
            if worker is not None:
                deleted = False
                try:
                    import sip  # type: ignore
                    deleted = sip.isdeleted(worker)  # type: ignore[attr-defined]
                except Exception as e:
                    logger.debug("SIP deleted check failed: %s", e, exc_info=True)
                    deleted = False
                if not deleted:
                    try:
                        if worker.isRunning():
                            worker.requestInterruption()
                            worker.wait(5000)
                            if worker.isRunning():
                                worker.terminate()
                                worker.wait()
                    except RuntimeError as e:
                        logger.debug("Worker runtime error during stop: %s", e, exc_info=True)
                    try:
                        worker.deleteLater()
                    except RuntimeError as e:
                        logger.debug("Worker runtime error during deleteLater: %s", e, exc_info=True)
        finally:
            self.analysis_worker = None
        
        # Reset UI
        self.main_window.start_analysis_btn.setEnabled(True)
        self.main_window.stop_analysis_btn.setEnabled(False)
        self.main_window.progress_bar.setVisible(False)
        self.main_window.progress_label.setText("Analysis stopped.")
    
    def on_analysis_completed(self, result_data):
        """Handle analysis completion."""
        try:
            batch_result = result_data['batch_result']
            algorithm = result_data['algorithm']
            
            # Store results in memory (thread-safe)
            if getattr(self, 'results_mutex', None):
                self.results_mutex.lock()
            try:
                self.main_window.analysis_results = {algorithm: batch_result}
            finally:
                if getattr(self, 'results_mutex', None):
                    self.results_mutex.unlock()
            
            # Save to database
            try:
                self._save_results_to_database(batch_result)
                logger.info("Analysis results saved to database")
            except Exception as e:
                logger.error("Failed to save analysis results to database: %s", e, exc_info=True)
                # Don't block UI update if DB save fails
            
            # Update results tab
            self.update_results_tab_single(batch_result)
            
            # Update status
            self.main_window.status_bar.showMessage(
                f"Analysis completed: {batch_result.total_cvs_analyzed} CVs analyzed in {batch_result.total_execution_time:.3f}s"
            )
            
            # Reset UI
            self.main_window.start_analysis_btn.setEnabled(True)
            self.main_window.stop_analysis_btn.setEnabled(False)
            self.main_window.progress_bar.setVisible(False)
            self.main_window.progress_label.setText("Analysis completed!")
            
            # Switch to results tab
            self.main_window.tab_widget.setCurrentIndex(3)
            # Log
            try:
                self.append_status(
                    f"Completed {algorithm} • {batch_result.total_cvs_analyzed} CVs • Time: {batch_result.total_execution_time:.3f}s • Avg score: {batch_result.average_relevance_score:.3f}"
                )
            except Exception as e:
                logger.warning("Failed to append completion status: %s", e, exc_info=True)
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"Failed to process analysis results: {str(e)}")
    
    def on_analysis_error(self, error_message):
        """Handle analysis error."""
        QMessageBox.critical(self.main_window, "Analysis Error", f"Analysis failed: {error_message}")
        
        # Reset UI
        self.main_window.start_analysis_btn.setEnabled(True)
        self.main_window.stop_analysis_btn.setEnabled(False)
        self.main_window.progress_bar.setVisible(False)
        self.main_window.progress_label.setText("Analysis failed.")
        # Log
        try:
            self.append_status(f"Error: {error_message}")
        except Exception as e:
            logger.warning("Failed to append error status: %s", e, exc_info=True)
    
    # Results Methods
    def update_results_tab_single(self, batch_result):
        """Update results tab for single algorithm analysis."""
        # Update summary
        self.main_window.total_cvs_label.setText(f"Total CVs: {batch_result.total_cvs_analyzed}")
        self.main_window.algorithm_used_label.setText(f"Algorithm: {batch_result.algorithm_used}")
        self.main_window.execution_time_label.setText(f"Execution Time: {batch_result.total_execution_time:.3f}s")
        self.main_window.avg_score_label.setText(f"Average Score: {batch_result.average_relevance_score:.3f}")
        
        # Update results table
        self.update_results_table(batch_result.cv_results)
        
        # Clear performance comparison table
        self.main_window.perf_table.setRowCount(0)
    
    def update_results_tab_comparative(self):
        """Update results tab for comparative analysis."""
        # Take a snapshot of results to avoid concurrent modification
        if getattr(self, 'results_mutex', None):
            self.results_mutex.lock()
        try:
            results_snapshot = dict(self.main_window.analysis_results) if self.main_window.analysis_results else {}
        finally:
            if getattr(self, 'results_mutex', None):
                self.results_mutex.unlock()
        if not results_snapshot:
            return
        
        # Calculate totals
        total_cvs = 0
        total_time = 0
        total_score = 0
        
        for batch_result in results_snapshot.values():
            total_cvs += batch_result.total_cvs_analyzed
            total_time += batch_result.total_execution_time
            total_score += batch_result.average_relevance_score
        
        avg_score = total_score / len(results_snapshot) if results_snapshot else 0
        
        # Update summary
        self.main_window.total_cvs_label.setText(f"Total CVs: {total_cvs}")
        self.main_window.algorithm_used_label.setText("Algorithm: Comparative Analysis")
        self.main_window.execution_time_label.setText(f"Total Time: {total_time:.3f}s")
        self.main_window.avg_score_label.setText(f"Average Score: {avg_score:.3f}")
        
        # Update performance comparison table
        self.update_performance_table()
        
        # Show results from best performing algorithm
        best_algorithm = min(results_snapshot.items(), key=lambda x: x[1].total_execution_time)
        self.update_results_table(best_algorithm[1].cv_results)
    
    def update_results_table(self, cv_results):
        """Update the results table with CV analysis results."""
        # Sort by relevance score descending (highest matches first)
        cv_results = sorted(cv_results, key=lambda r: r.relevance_score, reverse=True)
        
        self.main_window.results_table.setRowCount(len(cv_results))
        
        for row, result in enumerate(cv_results):
            # CV File
            self.main_window.results_table.setItem(row, 0, QTableWidgetItem(result.cv_filename))
            
            # Relevance Score
            score_item = QTableWidgetItem(f"{result.relevance_score:.3f}")
            score_item.setTextAlignment(Qt.AlignCenter)
            self.main_window.results_table.setItem(row, 1, score_item)
            
            # Matches
            matches_item = QTableWidgetItem(f"{len(result.matched_keywords)}/{result.total_keywords}")
            matches_item.setTextAlignment(Qt.AlignCenter)
            self.main_window.results_table.setItem(row, 2, matches_item)
            
            # Missing
            missing_item = QTableWidgetItem(f"{len(result.missing_keywords)}")
            missing_item.setTextAlignment(Qt.AlignCenter)
            self.main_window.results_table.setItem(row, 3, missing_item)
            
            # Execution Time
            time_item = QTableWidgetItem(f"{result.execution_time:.3f}s")
            time_item.setTextAlignment(Qt.AlignCenter)
            self.main_window.results_table.setItem(row, 4, time_item)
            
            # Comparisons
            comp_item = QTableWidgetItem(f"{result.comparison_count}")
            comp_item.setTextAlignment(Qt.AlignCenter)
            self.main_window.results_table.setItem(row, 5, comp_item)
    
    def update_performance_table(self):
        """Update the performance comparison table."""
        # Take snapshot under lock to avoid concurrent modification during iteration
        if getattr(self, 'results_mutex', None):
            self.results_mutex.lock()
        try:
            results_snapshot = dict(self.main_window.analysis_results) if self.main_window.analysis_results else {}
        finally:
            if getattr(self, 'results_mutex', None):
                self.results_mutex.unlock()
        if not results_snapshot:
            return
        
        self.main_window.perf_table.setRowCount(len(results_snapshot))
        
        # Sort algorithms by execution time
        sorted_results = sorted(results_snapshot.items(), key=lambda x: x[1].total_execution_time)
        
        fastest_time = sorted_results[0][1].total_execution_time
        
        for row, (algorithm, batch_result) in enumerate(sorted_results):
            # Algorithm name
            self.main_window.perf_table.setItem(row, 0, QTableWidgetItem(algorithm))
            
            # Execution time
            time_item = QTableWidgetItem(f"{batch_result.total_execution_time:.3f}s")
            time_item.setTextAlignment(Qt.AlignCenter)
            self.main_window.perf_table.setItem(row, 1, time_item)
            
            # Total comparisons
            total_comparisons = sum(r.comparison_count for r in batch_result.cv_results)
            comp_item = QTableWidgetItem(f"{total_comparisons}")
            comp_item.setTextAlignment(Qt.AlignCenter)
            self.main_window.perf_table.setItem(row, 2, comp_item)
            
            # Efficiency (speedup factor)
            speedup = batch_result.total_execution_time / fastest_time if fastest_time > 0 else 1
            eff_item = QTableWidgetItem(f"{speedup:.2f}x")
            eff_item.setTextAlignment(Qt.AlignCenter)
            self.main_window.perf_table.setItem(row, 3, eff_item)
    
    def export_results_csv(self):
        """Export results to CSV file."""
        # Snapshot results to avoid concurrent modification
        if getattr(self, 'results_mutex', None):
            self.results_mutex.lock()
        try:
            results_snapshot = dict(self.main_window.analysis_results) if self.main_window.analysis_results else {}
        finally:
            if getattr(self, 'results_mutex', None):
                self.results_mutex.unlock()
        if not results_snapshot:
            QMessageBox.warning(self.main_window, "No Results", "No analysis results to export.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self.main_window,
            "Export Results",
            f"cv_analysis_results_{int(time.time())}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                # Export the first available result
                batch_result = next(iter(results_snapshot.values()))
                success = self.main_window.analyzer.export_results_to_csv(batch_result, file_path)
                
                if success:
                    QMessageBox.information(self.main_window, "Success", f"Results exported to {file_path}")
                else:
                    QMessageBox.warning(self.main_window, "Error", "Failed to export results.")
                    
            except Exception as e:
                QMessageBox.critical(self.main_window, "Error", f"Failed to export results: {str(e)}")
    
    def generate_report(self):
        """Generate analysis report (DOCX) and notify the user."""
        try:
            from reports.docx_report import generate_academic_report
        except Exception as e:
            QMessageBox.critical(self.main_window, "Report Error", f"Report module not available: {e}")
            return

        try:
            path = generate_academic_report()
            QMessageBox.information(
                self.main_window,
                "Report Generated",
                f"Report saved to:\n{path}"
            )
            try:
                self.append_status(f"Report generated at: {path}")
            except Exception as e:
                logger.warning("Failed to append report generated status: %s", e, exc_info=True)
        except Exception as e:
            QMessageBox.critical(self.main_window, "Report Error", f"Failed to generate report: {e}")

    # Utilities
    def _save_results_to_database(self, batch_result):
        """
        Save batch analysis results to database.
        
        Args:
            batch_result: BatchAnalysisResult object to save
        """
        try:
            # Save batch summary
            job_id = batch_result.job_description.id if batch_result.job_description else 0
            batch_id = self.main_window.db.save_batch_analysis_result(
                job_description_id=job_id,
                algorithm_used=batch_result.algorithm_used,
                total_cvs_analyzed=batch_result.total_cvs_analyzed,
                total_execution_time=batch_result.total_execution_time,
                average_relevance_score=batch_result.average_relevance_score
            )
            
            # Save individual CV results
            for cv_result in batch_result.cv_results:
                self.main_window.db.save_analysis_result(
                    cv_filename=cv_result.cv_filename,
                    job_description_id=job_id,
                    algorithm_used=cv_result.algorithm_used,
                    relevance_score=cv_result.relevance_score,
                    execution_time=cv_result.execution_time,
                    comparison_count=cv_result.comparison_count,
                    matched_keywords=cv_result.matched_keywords,
                    missing_keywords=cv_result.missing_keywords,
                    total_keywords=cv_result.total_keywords
                )
            
            logger.info(f"Saved batch {batch_id} with {len(batch_result.cv_results)} CV results to database")
            
        except Exception as e:
            logger.error(f"Database save failed: {e}", exc_info=True)
            raise
    
    def append_status(self, text: str):
        """Append a timestamped line to the Analysis Status log box and auto-scroll."""
        try:
            from time import strftime
            ts = strftime("%H:%M:%S")
            self.main_window.status_text.append(f"[{ts}] {text}")
            # Ensure caret at end to auto-scroll
            cursor = self.main_window.status_text.textCursor()
            self.main_window.status_text.setTextCursor(cursor)
        except Exception as e:
            logger.warning("Failed to append status text '%s': %s", text, e, exc_info=True)
