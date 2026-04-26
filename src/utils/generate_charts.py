from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

RESULTS_PATH = Path("results/raw/experiment_results.csv")
CHARTS_DIR = Path("analysis/charts")
TABLES_DIR = Path("analysis/tables")


def load_results() -> pd.DataFrame:
    return pd.read_csv(RESULTS_PATH)


def save_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("algorithm")
        .agg(
            runtime_mean=("runtime", "mean"),
            coverage_mean=("coverage_score", "mean"),
            priority_mean=("priority_score", "mean"),
            utilization_mean=("time_utilization_score", "mean"),
            fatigue_balance_mean=("fatigue_balance_score", "mean"),
            total_score_mean=("total_score", "mean"),
            total_score_min=("total_score", "min"),
            total_score_max=("total_score", "max"),
            trials=("algorithm", "count"),
        )
        .reset_index()
    )

    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    summary.to_csv(TABLES_DIR / "summary_table.csv", index=False)
    summary.to_markdown(TABLES_DIR / "summary_table.md", index=False)
    return summary


def chart_random_score_distribution(df: pd.DataFrame):
    random_df = df[df["algorithm"] == "random"]
    greedy_score = df[df["algorithm"] == "greedy"]["total_score"].iloc[0]
    refined_score = df[df["algorithm"] == "refined"]["total_score"].iloc[0]

    plt.figure(figsize=(8, 5))
    plt.hist(random_df["total_score"], bins=10, edgecolor="black")
    plt.axvline(greedy_score, linestyle="--", label="Greedy")
    plt.axvline(refined_score, linestyle="--", label="Refined")
    plt.xlabel("Total Score")
    plt.ylabel("Frequency")
    plt.title("Random Baseline Total Scores vs Greedy and Refined")
    plt.legend()
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "random_score_distribution.png")
    plt.close()


def chart_total_score_comparison(summary: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    plt.bar(summary["algorithm"], summary["total_score_mean"])
    plt.xlabel("Algorithm")
    plt.ylabel("Mean Total Score")
    plt.title("Mean Total Score by Algorithm")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "total_score_comparison.png")
    plt.close()


def chart_fatigue_balance_comparison(summary: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    plt.bar(summary["algorithm"], summary["fatigue_balance_mean"])
    plt.xlabel("Algorithm")
    plt.ylabel("Mean Fatigue Balance Score")
    plt.title("Fatigue Balance by Algorithm")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "fatigue_balance_comparison.png")
    plt.close()


def chart_priority_comparison(summary: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    plt.bar(summary["algorithm"], summary["priority_mean"])
    plt.xlabel("Algorithm")
    plt.ylabel("Mean Priority Score")
    plt.title("Priority Score by Algorithm")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "priority_comparison.png")
    plt.close()


def chart_runtime_comparison(summary: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    plt.bar(summary["algorithm"], summary["runtime_mean"])
    plt.xlabel("Algorithm")
    plt.ylabel("Mean Runtime (seconds)")
    plt.title("Runtime by Algorithm")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "runtime_comparison.png")
    plt.close()


def chart_time_utilization_comparison(summary: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    plt.bar(summary["algorithm"], summary["utilization_mean"])
    plt.xlabel("Algorithm")
    plt.ylabel("Mean Time Utilization Score")
    plt.title("Time Utilization by Algorithm")
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / "time_utilization_comparison.png")
    plt.close()


def main():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    df = load_results()
    summary = save_summary_table(df)

    chart_random_score_distribution(df)
    chart_total_score_comparison(summary)
    chart_fatigue_balance_comparison(summary)
    chart_priority_comparison(summary)
    chart_runtime_comparison(summary)
    chart_time_utilization_comparison(summary)

    print(f"Saved charts to {CHARTS_DIR}")
    print(f"Saved tables to {TABLES_DIR}")


if __name__ == "__main__":
    main()
