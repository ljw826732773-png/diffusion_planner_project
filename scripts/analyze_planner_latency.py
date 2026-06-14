from __future__ import annotations

import argparse
import csv
from pathlib import Path
from statistics import mean, median

import pandas as pd

from project_utils import project_root


def project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root() / path


def percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize real closed-loop planner runtime.")
    parser.add_argument(
        "--runner-report",
        type=Path,
        default=Path("results/mini_eval_runner_report.csv"),
    )
    parser.add_argument(
        "--aggregated",
        type=Path,
        default=None,
        help="Optional aggregated metrics CSV used to map scenario tokens to scenario types.",
    )
    parser.add_argument("--output-csv", type=Path, default=Path("results/mini_eval_latency_summary.csv"))
    parser.add_argument("--output-md", type=Path, default=Path("results/mini_eval_latency_summary.md"))
    args = parser.parse_args()

    runner = pd.read_csv(project_path(args.runner_report))
    scenario_types = {}
    if args.aggregated is not None:
        aggregated = pd.read_csv(project_path(args.aggregated))
        scenario_rows = aggregated[
            aggregated["log_name"].notna()
            & (aggregated["scenario"].astype(str) != "final_score")
            & aggregated["scenario_type"].notna()
        ]
        scenario_types = dict(
            zip(
                scenario_rows["scenario"].astype(str),
                scenario_rows["scenario_type"].astype(str),
            )
        )
    values = runner["compute_trajectory_runtimes_mean"].astype(float).tolist()
    durations = runner["duration"].astype(float).tolist()
    slowest = runner.sort_values("compute_trajectory_runtimes_mean", ascending=False).head(5)

    summary = {
        "num_scenarios": len(values),
        "mean_compute_runtime_s": mean(values),
        "median_compute_runtime_s": median(values),
        "p90_compute_runtime_s": percentile(values, 0.90),
        "p95_compute_runtime_s": percentile(values, 0.95),
        "max_compute_runtime_s": max(values),
        "mean_simulation_duration_s": mean(durations),
        "max_simulation_duration_s": max(durations),
    }

    csv_path = project_path(args.output_csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary.keys()))
        writer.writeheader()
        writer.writerow(summary)

    md_path = project_path(args.output_md)
    lines = [
        "# Mini Evaluation Latency Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in summary.items():
        if key == "num_scenarios":
            lines.append(f"| {key} | {int(value)} |")
        else:
            lines.append(f"| {key} | {value:.4f} |")
    lines.extend(
        [
            "",
            "## Slowest scenarios",
            "",
            "| Rank | Scenario type | Scenario token | Mean runtime | Duration |",
            "| ---: | --- | --- | ---: | ---: |",
        ]
    )
    for rank, (_, row) in enumerate(slowest.iterrows(), start=1):
        lines.append(
            "| {rank} | {scenario_type} | {scenario_name} | {runtime:.4f} s | {duration:.4f} s |".format(
                rank=rank,
                scenario_type=row.get("scenario_type", "")
                or scenario_types.get(str(row.get("scenario_name", "")), ""),
                scenario_name=row.get("scenario_name", ""),
                runtime=float(row["compute_trajectory_runtimes_mean"]),
                duration=float(row["duration"]),
            )
        )
    lines.extend(
        [
            "",
            "Note: these numbers come from nuPlan closed-loop runner reports. They include planner `compute_trajectory` runtime in the simulator loop, so they are more realistic than the synthetic model-only benchmark.",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"saved_csv={csv_path}")
    print(f"saved_md={md_path}")


if __name__ == "__main__":
    main()
