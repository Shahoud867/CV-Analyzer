"""
Main GUI Window for CV Analyzer
Phase 3: Desktop Application Implementation

This module implements the main PyQt5 GUI window with tabbed interface
for the Intelligent CV Analyzer application.
"""

import sys
import logging

try:
    from PyQt5.QtWidgets import (
        QMainWindow, QTabWidget, QWidget, QVBoxLayout,
        QHBoxLayout, QGridLayout, QLabel, QPushButton, QLineEdit,
        QTextEdit, QListWidget, QComboBox, QProgressBar,
    QTableWidget, QHeaderView,
        QMessageBox, QGroupBox, QCheckBox, QFrame
    )
    from PyQt5.QtGui import QFont
    PYQT5_AVAILABLE = True
except ImportError:
    PYQT5_AVAILABLE = False
    print("Warning: PyQt5 not available. GUI will not work.")

# Import our modules
from engine.analyzer import CVAnalyzer
from persistence.db import DatabaseManager
 

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """
    Main application window with tabbed interface.
    
    Tabs:
    1. File Management - Load and manage CV files
    2. Job Descriptions - Manage job descriptions and keywords
    3. Analysis - Run analysis with algorithm selection
    4. Results - View analysis results and performance metrics
    """
    
    def __init__(self):
        super().__init__()
        
        if not PYQT5_AVAILABLE:
            QMessageBox.critical(None, "Error", "PyQt5 is required for the GUI application.")
            sys.exit(1)
        
        # Initialize components
        self.analyzer = CVAnalyzer()
        self.db = DatabaseManager()
        self.cv_files = []
        self.current_job_description = None
        self.analysis_results = {}
        
        # Initialize handlers
        from .handlers import MainWindowHandlers
        self.handlers = MainWindowHandlers(self)
        
        # Setup UI
        self.setWindowTitle("Intelligent CV Analyzer - String Matching Algorithms")
        self.setGeometry(100, 100, 1200, 800)
        self.setMinimumSize(1000, 700)
        
        # Apply modern styling
        self.setStyleSheet(self.get_modern_stylesheet())
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header
        self.create_header()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)
        
        # Create tabs
        self.create_file_management_tab()
        self.create_job_management_tab()
        self.create_analysis_tab()
        self.create_results_tab()
        
        # Add tabs to main layout
        self.main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.create_status_bar()
        
        # Load initial data
        self.load_initial_data()
    
    def create_header(self):
        """Create application header with title and info."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setMaximumHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_label = QLabel("Intelligent CV Analyzer")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        
        # Subtitle
        subtitle_label = QLabel("String Matching Algorithms: Brute Force • Rabin-Karp • KMP")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d; margin: 5px;")
        
        # Info button
        info_button = QPushButton("ℹ️ Info")
        info_button.setMaximumWidth(80)
        info_button.clicked.connect(self.show_info)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(subtitle_label)
        header_layout.addWidget(info_button)
        
        self.main_layout.addWidget(header_frame)
    
    def create_file_management_tab(self):
        """Create file management tab for CV loading."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File selection section
        file_group = QGroupBox("CV File Management")
        file_layout = QVBoxLayout(file_group)
        
        # File selection buttons
        button_layout = QHBoxLayout()
        
        self.load_files_btn = QPushButton("📁 Load CV Files")
        self.load_files_btn.clicked.connect(self.load_cv_files)
        self.load_files_btn.setMinimumHeight(40)
        
        self.load_dataset_btn = QPushButton("📂 Load DataSet Folder")
        self.load_dataset_btn.clicked.connect(self.load_dataset_folder)
        self.load_dataset_btn.setMinimumHeight(40)
        
        self.clear_files_btn = QPushButton("🗑️ Clear All")
        self.clear_files_btn.clicked.connect(self.clear_cv_files)
        self.clear_files_btn.setMinimumHeight(40)
        
        button_layout.addWidget(self.load_files_btn)
        button_layout.addWidget(self.load_dataset_btn)
        button_layout.addWidget(self.clear_files_btn)
        
        file_layout.addLayout(button_layout)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(200)
        self.file_list.itemSelectionChanged.connect(self.on_file_selection_changed)
        
        file_layout.addWidget(QLabel("Loaded CV Files:"))
        file_layout.addWidget(self.file_list)
        
        # File info section
        info_layout = QHBoxLayout()
        
        self.file_count_label = QLabel("Files loaded: 0")
        self.file_size_label = QLabel("Total size: 0 MB")
        
        info_layout.addWidget(self.file_count_label)
        info_layout.addStretch()
        info_layout.addWidget(self.file_size_label)
        
        file_layout.addLayout(info_layout)
        
        layout.addWidget(file_group)
        
        # File preview section
        preview_group = QGroupBox("File Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.file_preview = QTextEdit()
        self.file_preview.setMaximumHeight(150)
        self.file_preview.setReadOnly(True)
        self.file_preview.setPlaceholderText("Select a file to preview its content...")
        
        preview_layout.addWidget(QLabel("File Content Preview:"))
        preview_layout.addWidget(self.file_preview)
        
        layout.addWidget(preview_group)
        
        # Add tab
        self.tab_widget.addTab(tab, "📁 Files")
    
    def create_job_management_tab(self):
        """Create job description management tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Job description section
        job_group = QGroupBox("Job Description Management")
        job_layout = QVBoxLayout(job_group)
        
        # Job selection
        selection_layout = QHBoxLayout()
        
        self.job_combo = QComboBox()
        self.job_combo.currentTextChanged.connect(self.on_job_selection_changed)
        
        self.refresh_jobs_btn = QPushButton("🔄 Refresh")
        self.refresh_jobs_btn.clicked.connect(self.refresh_job_descriptions)
        
        selection_layout.addWidget(QLabel("Select Job Description:"))
        selection_layout.addWidget(self.job_combo)
        selection_layout.addWidget(self.refresh_jobs_btn)
        
        job_layout.addLayout(selection_layout)
        
        # Job details
        details_layout = QGridLayout()
        
        self.job_title_edit = QLineEdit()
        self.job_title_edit.setPlaceholderText("Job Title")
        
        self.job_desc_edit = QTextEdit()
        self.job_desc_edit.setMaximumHeight(80)
        self.job_desc_edit.setPlaceholderText("Job Description")
        
        self.keywords_edit = QTextEdit()
        self.keywords_edit.setMaximumHeight(100)
        self.keywords_edit.setPlaceholderText("Enter keywords separated by commas")
        
        details_layout.addWidget(QLabel("Title:"), 0, 0)
        details_layout.addWidget(self.job_title_edit, 0, 1)
        details_layout.addWidget(QLabel("Description:"), 1, 0)
        details_layout.addWidget(self.job_desc_edit, 1, 1)
        details_layout.addWidget(QLabel("Keywords:"), 2, 0)
        details_layout.addWidget(self.keywords_edit, 2, 1)
        
        job_layout.addLayout(details_layout)
        
        # Job management buttons
        button_layout = QHBoxLayout()
        
        self.save_job_btn = QPushButton("💾 Save Job")
        self.save_job_btn.clicked.connect(self.save_job_description)
        
        self.new_job_btn = QPushButton("➕ New Job")
        self.new_job_btn.clicked.connect(self.create_new_job)
        
        self.delete_job_btn = QPushButton("🗑️ Delete Job")
        self.delete_job_btn.clicked.connect(self.delete_job_description)
        
        button_layout.addWidget(self.save_job_btn)
        button_layout.addWidget(self.new_job_btn)
        button_layout.addWidget(self.delete_job_btn)
        
        job_layout.addLayout(button_layout)
        
        layout.addWidget(job_group)
        
    # Note: Sample job descriptions UI has been removed for a cleaner production UI
        
        # Add tab
        self.tab_widget.addTab(tab, "💼 Jobs")
    
    def create_analysis_tab(self):
        """Create analysis tab with algorithm selection."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Analysis configuration
        config_group = QGroupBox("Analysis Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Algorithm selection
        algo_layout = QHBoxLayout()
        
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Brute Force", "Rabin-Karp", "KMP", "Compare All"])
        
        self.case_sensitive_check = QCheckBox("Case Sensitive")
        
        algo_layout.addWidget(QLabel("Algorithm:"))
        algo_layout.addWidget(self.algorithm_combo)
        algo_layout.addWidget(self.case_sensitive_check)
        algo_layout.addStretch()
        
        config_layout.addLayout(algo_layout)
        
        # Analysis controls
        control_layout = QHBoxLayout()
        
        self.start_analysis_btn = QPushButton("🚀 Start Analysis")
        self.start_analysis_btn.clicked.connect(self.start_analysis)
        self.start_analysis_btn.setMinimumHeight(50)
        self.start_analysis_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        
        self.stop_analysis_btn = QPushButton("⏹️ Stop Analysis")
        self.stop_analysis_btn.clicked.connect(self.stop_analysis)
        self.stop_analysis_btn.setEnabled(False)
        self.stop_analysis_btn.setMinimumHeight(50)
        
        control_layout.addWidget(self.start_analysis_btn)
        control_layout.addWidget(self.stop_analysis_btn)
        
        config_layout.addLayout(control_layout)
        
        # Progress section
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        
        self.progress_label = QLabel("Ready to analyze...")
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        config_layout.addLayout(progress_layout)
        
        layout.addWidget(config_group)
        
        # Analysis status
        status_group = QGroupBox("Analysis Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(150)
        self.status_text.setReadOnly(True)
        self.status_text.setPlaceholderText("Analysis status will appear here...")
        
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_group)
        
        # Add tab
        self.tab_widget.addTab(tab, "🔍 Analysis")
    
    def create_results_tab(self):
        """Create results visualization tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Results summary
        summary_group = QGroupBox("Analysis Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        # Summary labels
        summary_info_layout = QGridLayout()
        
        self.total_cvs_label = QLabel("Total CVs: 0")
        self.algorithm_used_label = QLabel("Algorithm: None")
        self.execution_time_label = QLabel("Execution Time: 0.000s")
        self.avg_score_label = QLabel("Average Score: 0.000")
        
        summary_info_layout.addWidget(self.total_cvs_label, 0, 0)
        summary_info_layout.addWidget(self.algorithm_used_label, 0, 1)
        summary_info_layout.addWidget(self.execution_time_label, 1, 0)
        summary_info_layout.addWidget(self.avg_score_label, 1, 1)
        
        summary_layout.addLayout(summary_info_layout)
        
        layout.addWidget(summary_group)
        
        # Results table
        results_group = QGroupBox("CV Analysis Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "CV File", "Relevance Score", "Matches", "Missing", "Execution Time", "Comparisons"
        ])
        
        # Set table properties
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        results_layout.addWidget(self.results_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        self.export_csv_btn = QPushButton("📊 Export to CSV")
        self.export_csv_btn.clicked.connect(self.export_results_csv)
        
        self.export_report_btn = QPushButton("📄 Generate Report")
        self.export_report_btn.clicked.connect(self.generate_report)
        
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_report_btn)
        export_layout.addStretch()
        
        results_layout.addLayout(export_layout)
        
        layout.addWidget(results_group)
        
        # Performance comparison
        perf_group = QGroupBox("Performance Comparison")
        perf_layout = QVBoxLayout(perf_group)
        
        self.perf_table = QTableWidget()
        self.perf_table.setColumnCount(4)
        self.perf_table.setHorizontalHeaderLabels([
            "Algorithm", "Execution Time", "Comparisons", "Efficiency"
        ])
        
        perf_header = self.perf_table.horizontalHeader()
        perf_header.setSectionResizeMode(QHeaderView.Stretch)
        self.perf_table.setAlternatingRowColors(True)
        
        perf_layout.addWidget(self.perf_table)
        
        layout.addWidget(perf_group)
        
        # Add tab
        self.tab_widget.addTab(tab, "📊 Results")
    
    def create_status_bar(self):
        """Create status bar with information."""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Add permanent widgets
        self.db_status_label = QLabel("Database: Connected")
        self.files_status_label = QLabel("Files: 0 loaded")
        
        self.status_bar.addPermanentWidget(self.db_status_label)
        self.status_bar.addPermanentWidget(self.files_status_label)
    
    def get_modern_stylesheet(self):
        """Get modern application stylesheet."""
        return """
        QMainWindow {
            background-color: #f8f9fa;
        }
        
        QTabWidget::pane {
            border: 1px solid #dee2e6;
            background-color: white;
        }
        
        QTabWidget::tab-bar {
            alignment: left;
        }
        
        QTabBar::tab {
            background-color: #e9ecef;
            border: 1px solid #dee2e6;
            padding: 8px 16px;
            margin-right: 2px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #007bff;
        }
        
        QTabBar::tab:hover {
            background-color: #f8f9fa;
        }
        
        QGroupBox {
            font-weight: bold;
            border: 2px solid #dee2e6;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
        }
        
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #0056b3;
        }
        
        QPushButton:pressed {
            background-color: #004085;
        }
        
        QPushButton:disabled {
            background-color: #6c757d;
        }
        
        QLineEdit, QTextEdit {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }
        
        QLineEdit:focus, QTextEdit:focus {
            border-color: #007bff;
        }
        
        QComboBox {
            border: 1px solid #ced4da;
            border-radius: 4px;
            padding: 8px;
            background-color: white;
        }
        
        QListWidget {
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
        }
        
        QTableWidget {
            border: 1px solid #ced4da;
            border-radius: 4px;
            background-color: white;
            gridline-color: #dee2e6;
        }
        
        QTableWidget::item {
            padding: 8px;
        }
        
        QTableWidget::item:selected {
            background-color: #007bff;
            color: white;
        }
        
        QProgressBar {
            border: 1px solid #ced4da;
            border-radius: 4px;
            text-align: center;
        }
        
        QProgressBar::chunk {
            background-color: #007bff;
            border-radius: 3px;
        }
        """
    
    def load_initial_data(self):
        """Load initial data on startup."""
        self.refresh_job_descriptions()
        self.update_file_status()
        # All signal connections are already established in tab creation methods,
        # which point to handler-bound methods (e.g., self.load_cv_files etc.).
    
    def refresh_job_descriptions(self):
        """Refresh job descriptions from database."""
        self.handlers.refresh_job_descriptions()
    
    def update_file_status(self):
        """Update file status labels."""
        self.handlers.update_file_status()
    
    def show_info(self):
        """Show application information dialog."""
        QMessageBox.information(
            self, 
            "About CV Analyzer",
            "Intelligent CV Analyzer using String Matching Algorithms\n\n"
            "This application implements three string matching algorithms:\n"
            "• Brute Force - Simple pattern matching\n"
            "• Rabin-Karp - Hash-based optimization\n"
            "• KMP - Optimized pattern matching\n\n"
            "Features:\n"
            "• PDF and DOCX text extraction\n"
            "• Multiple job description management\n"
            "• Performance analysis and comparison\n"
            "• Results export and reporting"
        )
    
    # Removed duplicate analysis methods (handled in gui.handlers)
    
    def closeEvent(self, event):
        """Handle window close event - clean up threads."""
        # Stop any running analysis
        try:
            worker = getattr(self.handlers, 'analysis_worker', None)
            if worker is not None:
                try:
                    import sip  # type: ignore
                    deleted = sip.isdeleted(worker)  # type: ignore[attr-defined]
                except Exception as e:
                    logger.debug("SIP deleted check failed during closeEvent: %s", e, exc_info=True)
                    # If sip isn't available or any issue, assume not deleted and proceed guarded
                    deleted = False

                if not deleted:
                    try:
                        if worker.isRunning():
                            worker.requestInterruption()
                            worker.wait(3000)  # Wait up to 3 seconds
                            if worker.isRunning():
                                worker.terminate()
                                worker.wait()
                    except RuntimeError as e:
                        logger.debug("RuntimeError stopping worker in closeEvent: %s", e, exc_info=True)
                        # Underlying C++ object might be gone; ignore
                    try:
                        worker.deleteLater()
                    except RuntimeError as e:
                        logger.debug("RuntimeError during deleteLater in closeEvent: %s", e, exc_info=True)
                # Clear reference to avoid accessing deleted QObject later
                try:
                    self.handlers.analysis_worker = None
                except Exception as e:
                    logger.debug("Failed clearing analysis_worker reference in closeEvent: %s", e, exc_info=True)
        except Exception as e:
            # Best-effort cleanup; don't block window close
            logger.debug("Unhandled exception during closeEvent cleanup: %s", e, exc_info=True)
        
        # Accept the close event
        event.accept()
