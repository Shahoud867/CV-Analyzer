"""
Charts and visualization utilities for performance analysis.

Generates comparative charts across algorithms for:
- Average execution time
- Average comparison count
- Average relevance score (match percentage)

Outputs PNG images to the specified output directory.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


def _ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def _safe_savefig(fig: plt.Figure, out_path: Path):
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def generate_charts(csv_path: str | Path, output_dir: Optional[str | Path] = None) -> dict:
    """
    Generate a set of charts from a performance CSV.

    Args:
        csv_path: Path to the CSV produced by performance_runner.
        output_dir: Directory to save charts. Defaults to same folder as CSV under 'charts/'.

    Returns:
        Dictionary with paths of generated images.
    """
    csv_path = Path(csv_path)
    if output_dir is None:
        output_dir = csv_path.parent / "charts"
    out_dir = _ensure_dir(output_dir)

    df = pd.read_csv(csv_path)

    # Normalize algorithm names for grouping consistency
    if 'algorithm' not in df.columns:
        raise ValueError("CSV must contain an 'algorithm' column")

    # Basic aggregations
    agg = (
        df.groupby('algorithm')
          .agg(avg_exec_time=('execution_time', 'mean'),
               avg_comparisons=('comparisons', 'mean'),
               avg_relevance=('relevance_score', 'mean'),
               runs=('algorithm', 'count'))
          .reset_index()
    )

    generated = {}

    # 1) Average execution time per algorithm
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(agg['algorithm'], agg['avg_exec_time'], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
    ax.set_title('Average Execution Time by Algorithm (seconds)')
    ax.set_ylabel('Time (s)')
    ax.set_xlabel('Algorithm')
    for i, v in enumerate(agg['avg_exec_time']):
        ax.text(i, v, f"{v:.3f}", ha='center', va='bottom')
    out_file = out_dir / 'avg_execution_time_by_algorithm.png'
    _safe_savefig(fig, out_file)
    generated['avg_time'] = str(out_file)

    # 2) Average comparisons per algorithm
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(agg['algorithm'], agg['avg_comparisons'], color=['#9467bd', '#8c564b', '#e377c2'])
    ax.set_title('Average Comparisons by Algorithm')
    ax.set_ylabel('Character Comparisons')
    ax.set_xlabel('Algorithm')
    for i, v in enumerate(agg['avg_comparisons']):
        ax.text(i, v, f"{v:.0f}", ha='center', va='bottom')
    out_file = out_dir / 'avg_comparisons_by_algorithm.png'
    _safe_savefig(fig, out_file)
    generated['avg_comparisons'] = str(out_file)

    # 3) Average relevance per algorithm
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(agg['algorithm'], agg['avg_relevance'], color=['#17becf', '#bcbd22', '#7f7f7f'])
    ax.set_title('Average Relevance Score by Algorithm')
    ax.set_ylabel('Relevance (0-1)')
    ax.set_xlabel('Algorithm')
    ax.set_ylim(0, 1)
    for i, v in enumerate(agg['avg_relevance']):
        ax.text(i, v, f"{v:.2f}", ha='center', va='bottom')
    out_file = out_dir / 'avg_relevance_by_algorithm.png'
    _safe_savefig(fig, out_file)
    generated['avg_relevance'] = str(out_file)

    # Scenario-based charts if columns exist
    # Single vs Multiple keywords
    if 'keywords_count' in df.columns:
        df['scenario'] = df['keywords_count'].apply(lambda k: 'Single Keyword' if k == 1 else 'Multiple Keywords')
        scen = (
            df.groupby(['scenario', 'algorithm'])
              .agg(avg_exec_time=('execution_time', 'mean'),
                   avg_comparisons=('comparisons', 'mean'),
                   avg_relevance=('relevance_score', 'mean'))
              .reset_index()
        )

        # Execution time stacked by scenario
        for metric, filename, ylabel, decimals in [
            ('avg_exec_time', 'scenario_execution_time.png', 'Time (s)', 3),
            ('avg_comparisons', 'scenario_comparisons.png', 'Comparisons', 0),
            ('avg_relevance', 'scenario_relevance.png', 'Relevance (0-1)', 2),
        ]:
            fig, ax = plt.subplots(figsize=(8, 4))
            for scenario in scen['scenario'].unique():
                subset = scen[scen['scenario'] == scenario]
                ax.plot(subset['algorithm'], subset[metric], marker='o', label=scenario)
            ax.set_title(f'{ylabel} by Algorithm and Scenario')
            ax.set_ylabel(ylabel)
            ax.set_xlabel('Algorithm')
            ax.legend()
            out_file = out_dir / filename
            _safe_savefig(fig, out_file)
            generated[f'scenario_{metric}'] = str(out_file)

    # Small vs Large CVs (by size_bucket if available)
    if 'size_bucket' in df.columns:
        size = (
            df.groupby(['size_bucket', 'algorithm'])
              .agg(avg_exec_time=('execution_time', 'mean'),
                   avg_comparisons=('comparisons', 'mean'),
                   avg_relevance=('relevance_score', 'mean'))
              .reset_index()
        )
        for metric, filename, ylabel, decimals in [
            ('avg_exec_time', 'size_execution_time.png', 'Time (s)', 3),
            ('avg_comparisons', 'size_comparisons.png', 'Comparisons', 0),
            ('avg_relevance', 'size_relevance.png', 'Relevance (0-1)', 2),
        ]:
            fig, ax = plt.subplots(figsize=(8, 4))
            for bucket in size['size_bucket'].unique():
                subset = size[size['size_bucket'] == bucket]
                ax.plot(subset['algorithm'], subset[metric], marker='o', label=bucket)
            ax.set_title(f'{ylabel} by Algorithm and CV Size')
            ax.set_ylabel(ylabel)
            ax.set_xlabel('Algorithm')
            ax.legend()
            out_file = out_dir / filename
            _safe_savefig(fig, out_file)
            generated[f'size_{metric}'] = str(out_file)

    return generated


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate charts from a performance CSV")
    parser.add_argument('csv', help='Path to performance CSV')
    parser.add_argument('--out', help='Output directory for charts')
    args = parser.parse_args()

    paths = generate_charts(args.csv, args.out)
    print("Generated charts:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
