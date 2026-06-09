from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd
from matplotlib import pyplot as plt


def scenario_rows(aggregated: pd.DataFrame) -> pd.DataFrame:
    rows = aggregated[
        aggregated["scenario"].notna()
        & (aggregated["scenario"].astype(str) != "final_score")
        & aggregated["log_name"].notna()
    ].copy()
    return rows.sort_values("score", ascending=True)


def final_score(aggregated: pd.DataFrame) -> float:
    rows = aggregated[aggregated["scenario"].astype(str) == "final_score"]
    if rows.empty:
        return float(aggregated["score"].dropna().iloc[-1])
    return float(rows.iloc[0]["score"])


def plot(aggregated_path: Path, runner_path: Path, output_path: Path) -> None:
    aggregated = pd.read_csv(aggregated_path)
    runner = pd.read_csv(runner_path)

    scenario_scores = scenario_rows(aggregated)
    merged = scenario_scores.merge(
        runner[["scenario_name", "compute_trajectory_runtimes_mean", "duration"]],
        left_on="scenario",
        right_on="scenario_name",
        how="left",
    )

    labels = merged["scenario_type"].str.replace("_", "\n", regex=False).tolist()
    score_values = merged["score"].astype(float).tolist()
    runtime_values = merged["compute_trajectory_runtimes_mean"].astype(float).tolist()
    duration_values = merged["duration"].astype(float).tolist()
    final = final_score(aggregated)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.2), dpi=150)
    y_positions = range(len(labels))

    axes[0].barh(y_positions, score_values, color="#4c78a8")
    axes[0].axvline(final, color="#d62728", linestyle="--", linewidth=1.2)
    axes[0].set_xlim(0, 1.05)
    axes[0].set_title(f"Scenario Score\nfinal={final:.4f}")
    axes[0].set_xlabel("weighted score")
    axes[0].set_yticks(list(y_positions), labels)
    axes[0].grid(axis="x", linewidth=0.4, alpha=0.35)

    axes[1].barh(y_positions, runtime_values, color="#f58518")
    axes[1].set_title("Planner Runtime")
    axes[1].set_xlabel("mean compute_trajectory runtime (s)")
    axes[1].set_yticks(list(y_positions), labels)
    axes[1].grid(axis="x", linewidth=0.4, alpha=0.35)

    axes[2].barh(y_positions, duration_values, color="#54a24b")
    axes[2].set_title("Simulation Duration")
    axes[2].set_xlabel("duration (s)")
    axes[2].set_yticks(list(y_positions), labels)
    axes[2].grid(axis="x", linewidth=0.4, alpha=0.35)

    fig.suptitle(f"nuPlan mini closed-loop evaluation ({len(labels)} scenarios)", y=1.02, fontsize=13)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, bbox_inches="tight")
    print(f"saved_plot={output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot nuPlan mini evaluation summary.")
    parser.add_argument(
        "--aggregated",
        type=Path,
        default=Path("results/mini_eval_aggregated_metrics.csv"),
    )
    parser.add_argument(
        "--runner",
        type=Path,
        default=Path("results/mini_eval_runner_report.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/mini_eval_score_runtime.png"),
    )
    args = parser.parse_args()
    plot(args.aggregated, args.runner, args.output)


if __name__ == "__main__":
    main()
