# CV-Analyzer

An intelligent CV analysis system using classic string matching algorithms (Brute Force, Rabin–Karp, KMP) to evaluate CVs against job descriptions. Includes PDF/DOCX text extraction, GUI, CLI utilities, performance benchmarking, and DOCX report generation.

## Project structure
- Core engine: `intelligent_cv_analyzer/engine`
- Extractors: `intelligent_cv_analyzer/extractors`
- GUI: `intelligent_cv_analyzer/gui`
- Reports: `intelligent_cv_analyzer/reports`
- Data: `intelligent_cv_analyzer/data`

See the detailed module docs in `intelligent_cv_analyzer/README.md`.

## Requirements
Python 3.10+ recommended. Install dependencies:

```powershell
pip install -r intelligent_cv_analyzer/requirements.txt
```

## Usage
- GUI:
```powershell
py -3 intelligent_cv_analyzer\app.py --gui
```
- CLI analysis:
```powershell
py -3 intelligent_cv_analyzer\app.py --analyze --title "Backend Developer" --keywords "Python, Django, REST, SQL" --dataset "intelligent_cv_analyzer\data\cvs\DataSet" --algorithm KMP --out intelligent_cv_analyzer\data\results\cli_analysis.csv
```
	- Algorithms: KMP | Rabin-Karp | Brute Force | Compare All
	- Aliases supported: kmp | rk | rabin | brute | compare | all
- Performance suite:
```powershell
py -3 intelligent_cv_analyzer\app.py --performance 12
```
- DOCX report (if `reports/docx_report.py` available):
```powershell
py -3 intelligent_cv_analyzer\app.py --report
```

Notes:
- Supported formats: PDF, DOCX. Legacy `.doc` is not supported.
- Generated CSVs, charts, and the SQLite DB are ignored by `.gitignore`. Recreate using CLI or performance suite.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributors
- Add names or GitHub handles here.
