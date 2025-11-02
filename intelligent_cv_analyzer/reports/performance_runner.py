"""
Performance Test Runner for Intelligent CV Analyzer (Phase 4)

Runs comparative experiments across algorithms on:
- Small vs Large CVs (by extracted text length / file size)
- Single vs Multiple keyword scenarios

Outputs:
- CSV file in data/results with run-level metrics
- PNG charts in data/results/charts via reports.charts
"""

from __future__ import annotations

import csv
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Dict

# Local imports (assumes app launched from project root)
from engine.analyzer import CVAnalyzer, JobDescription
from extractors.pdf_extractor import PDFExtractor
from extractors.docx_extractor import DOCXExtractor
from reports.charts import generate_charts


DATASET_PATHS = [
    Path("data/cvs/DataSet"),
    Path("data/cvs")
]

RESULTS_DIR = Path("data/results")


@dataclass
class CVItem:
    file_path: Path
    text: str
    text_length: int
    size_bytes: int


def _ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _discover_cvs(max_files: int = 20) -> List[Path]:
    files: List[Path] = []
    for base in DATASET_PATHS:
        if base.exists():
            for root, _, fs in os.walk(base):
                for f in fs:
                    if f.lower().endswith((".pdf", ".docx")):
                        files.append(Path(root) / f)
    # De-duplicate while preserving order
    seen = set()
    unique = []
    for f in files:
        if f not in seen:
            unique.append(f)
            seen.add(f)
    return unique[:max_files]


def _extract_text(paths: List[Path]) -> List[CVItem]:
    pdf = PDFExtractor()
    docx = DOCXExtractor()
    items: List[CVItem] = []
    for p in paths:
        text = ""
        if p.suffix.lower() == ".pdf":
            r = pdf.extract_text(str(p))
            if r.get('success'):
                text = r.get('text', '')
        elif p.suffix.lower() == ".docx":
            r = docx.extract_text(str(p))
            if r.get('success'):
                text = r.get('text', '')
        items.append(CVItem(file_path=p, text=text, text_length=len(text or ""), size_bytes=p.stat().st_size if p.exists() else 0))
    # Filter out empty extractions
    return [it for it in items if it.text_length > 0]


def _bucket_by_size(items: List[CVItem]) -> Dict[str, List[CVItem]]:
    if not items:
        return {"Small": [], "Large": []}
    # Use median text length as split between small and large
    lengths = sorted([it.text_length for it in items])
    median = lengths[len(lengths)//2]
    small = [it for it in items if it.text_length <= median]
    large = [it for it in items if it.text_length > median]
    return {"Small": small, "Large": large}


def _default_job_descriptions() -> List[JobDescription]:
    now = time.strftime("%Y-%m-%d")
    return [
        JobDescription(id=1, title="Data Scientist", description="ML and analytics", 
                       keywords=["Python", "Machine Learning", "TensorFlow", "SQL", "Statistics"], created_at=now),
        JobDescription(id=2, title="Web Developer", description="Frontend and backend", 
                       keywords=["JavaScript", "React", "Node.js", "HTML", "CSS", "MongoDB"], created_at=now),
        JobDescription(id=3, title="Software Tester", description="Automation and QA", 
                       keywords=["Testing", "Selenium", "JUnit", "Manual Testing", "Bug Tracking"], created_at=now),
    ]


def run_performance(max_files: int = 12) -> Tuple[Path, Dict[str, str]]:
    analyzer = CVAnalyzer()

    # Discover and extract
    paths = _discover_cvs(max_files=max_files)
    items = _extract_text(paths)

    # Fallback synthetic CVs if none found
    if not items:
        synth_texts = [
            "Python developer with experience in Django, Flask, SQL, Git, Docker.",
            "Full-stack engineer: JavaScript, React, Node.js, HTML, CSS, MongoDB.",
            "QA tester with Selenium, JUnit, manual testing, bug tracking, agile.",
            "Data scientist focusing on Machine Learning, TensorFlow, Statistics, SQL.",
        ]
        items = [CVItem(file_path=Path(f"synthetic_{i}.txt"), text=t, text_length=len(t), size_bytes=len(t)) for i, t in enumerate(synth_texts, 1)]

    buckets = _bucket_by_size(items)
    jobs = _default_job_descriptions()
    algorithms = ["Brute Force", "Rabin-Karp", "KMP"]

    # Prepare output
    _ensure_dir(RESULTS_DIR)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    csv_path = RESULTS_DIR / f"performance_{timestamp}.csv"

    fields = [
        'cv_filename', 'cv_size', 'text_length', 'size_bucket',
        'job_title', 'algorithm', 'keywords_count', 'scenario',
        'execution_time', 'comparisons', 'relevance_score', 'matches_count'
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for bucket_name, cv_list in buckets.items():
            if not cv_list:
                continue
            # Limit to 6 per bucket for speed
            for cv in cv_list[:6]:
                for job in jobs:
                    # Scenarios: single keyword vs multiple
                    scenarios = [
                        (job.keywords[:1], 'Single'),
                        (job.keywords, 'Multiple')
                    ]
                    for keywords, scen_name in scenarios:
                        for algo in algorithms:
                            res = analyzer.analyze_cv(cv.text, keywords, algo)
                            writer.writerow({
                                'cv_filename': cv.file_path.name,
                                'cv_size': cv.size_bytes,
                                'text_length': cv.text_length,
                                'size_bucket': bucket_name,
                                'job_title': job.title,
                                'algorithm': algo,
                                'keywords_count': len(keywords),
                                'scenario': scen_name,
                                'execution_time': round(res.execution_time, 6),
                                'comparisons': res.comparison_count,
                                'relevance_score': round(res.relevance_score, 6),
                                'matches_count': len(res.matched_keywords),
                            })

    # Generate charts
    charts = generate_charts(csv_path, csv_path.parent / 'charts')
    return csv_path, charts


if __name__ == '__main__':
    path, charts = run_performance()
    print(f"\nPerformance CSV: {path}")
    print("Charts:")
    for k, v in charts.items():
        print(f"  {k}: {v}")
