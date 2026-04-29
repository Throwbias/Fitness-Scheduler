import pandas as pd
from pathlib import Path

# ... (directory setup)

def save_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """Correctly aggregates metrics using the actual column names in the CSV."""
    summary = (
        df.groupby("algorithm")
        .agg(
            runtime_mean=("runtime", "mean"),
            coverage_mean=("coverage_score", "mean"),
            priority_mean=("priority_score", "mean"),
            utilization_mean=("time_utilization_score", "mean"),
            # Matches the key used in evaluator.py
            fatigue_balance_mean=("fatigue_balance_score", "mean"),
            total_score_mean=("total_score", "mean"),
            total_score_min=("total_score", "min"),
            total_score_max=("total_score", "max"),
            trials=("algorithm", "count"),
        )
        .reset_index()
    )
    
    # ... (save logic)
    return summary