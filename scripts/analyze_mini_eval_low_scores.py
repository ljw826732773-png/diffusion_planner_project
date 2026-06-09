from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pandas as pd

from project_utils import project_root


IGNORED_COLUMNS = {
    "scenario",
    "log_name",
    "scenario_type",
    "num_scenarios",
    "planner_name",
    "aggregator_type",
    "score",
}


def project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root() / path


def limiting_metrics(row) -> list[str]:
    metrics = []
    for column, value in row.items():
        if column in IGNORED_COLUMNS or pd.isna(value):
            continue
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            continue
        if numeric < 0.999:
            metrics.append(f"{column}={numeric:.4f}")
    return metrics


def write_csv(rows, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["rank", "scenario", "scenario_type", "log_name", "score", "limiting_metrics"]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows, output_path: Path, total_scenarios: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Mini Evaluation Low-score Analysis",
        "",
        f"Source scenarios: {total_scenarios}",
        "",
        "The simulations all succeeded. This report only highlights lower-scoring scenarios and the metrics that reduced their weighted score.",
        "",
        "| Rank | Scenario Type | Scenario Token | Score | Main limiting metrics |",
        "| ---: | --- | --- | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            "| {rank} | {scenario_type} | {scenario} | {score:.4f} | {metrics} |".format(
                rank=row["rank"],
                scenario_type=row["scenario_type"],
                scenario=row["scenario"],
                score=float(row["score"]),
                metrics=row["limiting_metrics"] or "none below 0.999",
            )
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "",
            "- `ego_is_comfortable=0` usually points to acceleration, jerk, yaw rate, or lateral acceleration exceeding the nuPlan comfort thresholds.",
            "- `speed_limit_compliance<1` means the executed ego trajectory exceeded the mapped speed limit for part of the scenario.",
            "- `ego_progress_along_expert_route<1` means the planner progressed slightly less than the expert route baseline.",
            "- These are mini-split diagnostic results, not paper-level Val14/Test14 conclusions.",
        ]
    )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze low-scoring mini evaluation scenarios.")
    parser.add_argument(
        "--aggregated",
        type=Path,
        default=Path("results/mini_eval_aggregated_metrics.csv"),
        help="Aggregated metric CSV produced by summarize_nuplan_results.py.",
    )
    parser.add_argument("--top-n", type=int, default=3)
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("results/mini_eval_low_score_analysis.md"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("results/mini_eval_low_score_analysis.csv"),
    )
    args = parser.parse_args()

    aggregated = pd.read_csv(project_path(args.aggregated))
    scenario_rows = aggregated[
        aggregated["log_name"].notna()
        & (aggregated["scenario"] != "final_score")
        & aggregated["score"].notna()
    ].copy()
    scenario_rows["score"] = scenario_rows["score"].astype(float)
    scenario_rows = scenario_rows.sort_values("score", ascending=True).head(args.top_n)

    rows = []
    for rank, (_, row) in enumerate(scenario_rows.iterrows(), start=1):
        rows.append(
            {
                "rank": rank,
                "scenario": row["scenario"],
                "scenario_type": row["scenario_type"],
                "log_name": row["log_name"],
                "score": float(row["score"]),
                "limiting_metrics": "; ".join(limiting_metrics(row)),
            }
        )

    output_md = project_path(args.output_md)
    output_csv = project_path(args.output_csv)
    write_markdown(rows, output_md, total_scenarios=len(scenario_rows))
    write_csv(rows, output_csv)
    print(f"saved_md={output_md}")
    print(f"saved_csv={output_csv}")


if __name__ == "__main__":
    main()
