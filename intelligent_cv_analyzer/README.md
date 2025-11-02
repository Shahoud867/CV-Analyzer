# Intelligent CV Analyzer using String Matching Algorithms

## Project Overview

This project implements an intelligent CV analysis system that uses three different string matching algorithms to extract and compare skills from candidate CVs against predefined job descriptions. The system provides comprehensive performance analysis and generates detailed reports suitable for academic and professional review.

## Features

- **Three String Matching Algorithms**: Brute Force, Rabin-Karp, and Knuth-Morris-Pratt (KMP)
- **Multi-format Support**: PDF and DOCX file processing
- **Performance Analysis**: Detailed timing and comparison metrics
- **Database Integration**: SQLite for storing job descriptions and results
- **Comprehensive Reporting**: CSV export and performance visualization
- **Modular Architecture**: Clean separation of concerns

## System Architecture

```
intelligent_cv_analyzer/
├── engine/                 # Core analysis algorithms and logic
│   ├── algorithms.py      # String matching implementations
│   └── analyzer.py        # Main analysis engine
├── extractors/            # Text extraction modules
│   ├── pdf_extractor.py   # PDF text extraction
│   └── docx_extractor.py  # DOCX text extraction
├── persistence/           # Database operations
│   └── db.py             # SQLite database manager
├── reports/              # Visualization and reporting
├── tests/                # Unit tests
├── data/                 # Sample data and results
│   ├── cvs/              # CV files
│   ├── jobs/             # Job descriptions
│   └── results/           # Analysis outputs
├── app.py                # Main application entry point
└── requirements.txt      # Python dependencies
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the project**
   ```bash
   cd intelligent_cv_analyzer
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```powershell
   # Show usage options
   python app.py --help
   
   # Launch the desktop GUI
   python app.py --gui
   ```

## Usage

### Command Line Interface

```powershell
# Show help
python app.py --help

# Launch GUI
python app.py --gui

# Dynamic analysis with your own Job Description (runtime input)
python app.py --analyze --title "Backend Developer" --keywords "Python, Django, REST, SQL" --dataset "data/cvs/DataSet" --algorithm KMP --out data/results/cli_analysis.csv

# Generate Phase 6 DOCX report
python app.py --report
```

### Programmatic Usage

```python
from engine.analyzer import CVAnalyzer
from engine.algorithms import StringMatchingAlgorithms

# Initialize analyzer
analyzer = CVAnalyzer()

# Sample CV text and keywords
cv_text = "John Smith is a Python developer with Django experience..."
keywords = ["Python", "Django", "React", "SQL"]

# Analyze CV using KMP algorithm
result = analyzer.analyze_cv(cv_text, keywords, "KMP")

print(f"Relevance Score: {result.relevance_score}")
print(f"Matched Keywords: {result.matched_keywords}")
print(f"Execution Time: {result.execution_time:.3f} seconds")
```

## Algorithm Implementation

### 1. Brute Force Algorithm
- **Time Complexity**: O(n×m) where n=text length, m=pattern length
- **Space Complexity**: O(1)
- **Use Case**: Simple baseline implementation

### 2. Rabin-Karp Algorithm
- **Time Complexity**: O(n+m) average case, O(n×m) worst case
- **Space Complexity**: O(1)
- **Use Case**: Hash-based optimization for multiple patterns

### 3. Knuth-Morris-Pratt (KMP) Algorithm
- **Time Complexity**: O(n+m) guaranteed
- **Space Complexity**: O(m)
- **Use Case**: Optimal single pattern matching

## Performance Characteristics

| Algorithm | Best Case | Average Case | Worst Case | Space |
|-----------|-----------|--------------|------------|-------|
| Brute Force | O(n) | O(n×m) | O(n×m) | O(1) |
| Rabin-Karp | O(n+m) | O(n+m) | O(n×m) | O(1) |
| KMP | O(n+m) | O(n+m) | O(n+m) | O(m) |

## Sample Data

This repository does not preload sample job descriptions in production mode. You can add your own job descriptions in the GUI (Jobs tab) or via the database API.

## Database Schema

### Job Descriptions Table
- `id`: Primary key
- `title`: Job title
- `description`: Job description text
- `keywords`: JSON array of keywords
- `created_at`: Creation timestamp

### Analysis Results Table
- `id`: Primary key
- `cv_filename`: Name of analyzed CV
- `job_description_id`: Foreign key to job descriptions
- `algorithm_used`: Algorithm name
- `relevance_score`: Calculated relevance score
- `execution_time`: Algorithm execution time
- `comparison_count`: Number of character comparisons

## Testing

Run the built-in tests:

```bash
# Test algorithms
python -m engine.algorithms

# Test analyzer
python -m engine.analyzer

# Test extractors
python -m extractors.pdf_extractor
python -m extractors.docx_extractor

# Test database
python -m persistence.db
```

## Configuration

The application uses SQLite for data persistence. Configuration is stored in the `app_config` table:

- Database file: `cv_analyzer.db` (created automatically)
- Maximum file size: 50MB per CV
- **Supported formats**: 
  - ✅ **PDF** (.pdf) - Full support via pdfminer.six
  - ✅ **DOCX** (.docx) - Office 2007+ format via python-docx
  - ⚠️ **DOC** (.doc) - Legacy format NOT supported (convert to .docx first)

### Note on Legacy .doc Files
The older Microsoft Word format (.doc, pre-2007) is not supported by the `python-docx` library. If you have legacy .doc files in your dataset:
1. They will be skipped with a warning message
2. Convert them to .docx format using Microsoft Word or LibreOffice
3. Or use alternative extraction tools like `antiword` or `textract`

## Output and Reports

### Analysis Results
- Relevance scores (0.0 to 1.0)
- Matched and missing keywords
- Execution times and comparison counts
- Performance metrics

### Export Options
- CSV format for analysis results
- Performance statistics
- Algorithm comparison charts

### Performance Testing (Phase 4)
Run the automated performance suite and generate charts:

```powershell
python app.py --performance 12
```

Outputs:
- CSV: `data/results/performance_YYYYMMDD_HHMMSS.csv`
- Charts: `data/results/charts/*.png` (execution time, comparisons, relevance; by algorithm, scenario, and size bucket)

### Shortlisting CVs dynamically (runtime JD)
- Provide your job title and comma-separated keywords at runtime:

```powershell
python app.py --analyze --title "Data Scientist" --keywords "Python, Machine Learning, SQL, Statistics" --dataset "data/cvs/DataSet" --algorithm KMP --top 10 --out data/results/ds_shortlist.csv
```
- You can also pass explicit files with `--files <path1> <path2> ...` instead of `--dataset`.

## Error Handling

The system includes comprehensive error handling for:
- File format validation
- Database connection issues
- Text extraction failures
- Algorithm execution errors
- Memory management

## Future Enhancements

- Advanced NLP integration
- Machine learning-based scoring
- Cloud deployment support
- Real-time analysis dashboard

## Academic Context

This project demonstrates:
- String matching algorithm implementation
- Performance analysis and comparison
- System architecture design
- Database integration
- Software engineering best practices

## Phase 5 — Result Discussion & Recommendation

See the detailed analysis and recommendation here:

- reports/phase5_discussion.md

It summarizes comparative metrics from the performance CSV and includes visual charts for: execution time, comparisons, relevance, single vs multiple keywords, and small vs large CVs. The recommended default for real-time use is KMP, with Rabin–Karp as a viable option when batching many keywords.

## License

This project is created for academic purposes and demonstration of string matching algorithms in CV analysis applications.


## Contact

For questions or issues related to this implementation, please refer to the project documentation or contact the development team.
