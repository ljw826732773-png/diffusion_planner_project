from __future__ import annotations

import argparse
import csv
import math
from collections import Counter
from pathlib import Path

import pandas as pd

from project_utils import prepare_imports, project_root
from visualize_nuplan_trajectory import load_simulation_log, path_length, trajectory_xy


def project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root() / path


def scenario_type_map(aggregated_path: Path | None) -> dict[str, str]:
    if aggregated_path is None:
        return {}
    aggregated = pd.read_csv(project_path(aggregated_path))
    rows = aggregated[
        aggregated["log_name"].notna()
        & (aggregated["scenario"].astype(str) != "final_score")
        & aggregated["scenario_type"].notna()
    ]
    return dict(zip(rows["scenario"].astype(str), rows["scenario_type"].astype(str)))


def find_log(log_root: Path, scenario_token: str) -> Path | None:
    matches = list(log_root.rglob(f"{scenario_token}.msgpack.xz"))
    if not matches:
        return None
    return matches[0]


def object_type_name(obj) -> str:
    value = getattr(obj, "tracked_object_type", None)
    if value is None:
        return "UNKNOWN"
    return getattr(value, "name", str(value).split(".")[-1])


def summarize_log(path: Path | None) -> dict:
    if path is None:
        return {
            "history_steps": "",
            "ego_path_length_m": "",
            "mean_objects": "",
            "max_objects": "",
            "mean_vehicles": "",
            "max_vehicles": "",
            "mean_pedestrians": "",
            "max_pedestrians": "",
        }

    log = load_simulation_log(path)
    history = list(log.simulation_history.data)
    totals = []
    vehicle_counts = []
    pedestrian_counts = []
    ego_points = []
    for sample in history:
        ego_points.append(sample.ego_state)
        objects = list(sample.observation.tracked_objects.tracked_objects)
        counts = Counter(object_type_name(obj) for obj in objects)
        totals.append(len(objects))
        vehicle_counts.append(counts.get("VEHICLE", 0))
        pedestrian_counts.append(counts.get("PEDESTRIAN", 0))

    def avg(values: list[int]) -> float:
        return sum(values) / len(values) if values else float("nan")

    return {
        "history_steps": len(history),
        "ego_path_length_m": path_length(trajectory_xy(ego_points)),
        "mean_objects": avg(totals),
        "max_objects": max(totals) if totals else float("nan"),
        "mean_vehicles": avg(vehicle_counts),
        "max_vehicles": max(vehicle_counts) if vehicle_counts else float("nan"),
        "mean_pedestrians": avg(pedestrian_counts),
        "max_pedestrians": max(pedestrian_counts) if pedestrian_counts else float("nan"),
    }


def fmt(value) -> str:
    if value == "":
        return ""
    if isinstance(value, str):
        return value
    if math.isnan(float(value)):
        return "nan"
    return f"{float(value):.4f}"


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict], output_path: Path, top_n: int) -> None:
    lines = [
        "# Runtime Outlier Analysis",
        "",
        "Rows are sorted by candidate mean `compute_trajectory` runtime.",
        "",
        "| Rank | Scenario type | Scenario token | Candidate mean | Candidate median | Baseline mean | Delta | Mean objects | Max objects | Mean pedestrians |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rank, row in enumerate(rows[:top_n], start=1):
        lines.append(
            "| {rank} | {scenario_type} | {scenario_name} | {candidate_mean} s | {candidate_median} s | {baseline_mean} s | {delta} s | {mean_objects} | {max_objects} | {mean_pedestrians} |".format(
                rank=rank,
                scenario_type=row["scenario_type"],
                scenario_name=row["scenario_name"],
                candidate_mean=fmt(row["candidate_mean_runtime_s"]),
                candidate_median=fmt(row["candidate_median_runtime_s"]),
                baseline_mean=fmt(row["baseline_mean_runtime_s"]),
                delta=fmt(row["mean_runtime_delta_s"]),
                mean_objects=fmt(row["mean_objects"]),
                max_objects=fmt(row["max_objects"]),
                mean_pedestrians=fmt(row["mean_pedestrians"]),
            )
        )

    worst = rows[0]
    lines.extend(
        [
            "",
            "## Takeaways",
            "",
            f"- Slowest scenario: `{worst['scenario_type']}` / `{worst['scenario_name']}`.",
            f"- Candidate mean runtime is `{fmt(worst['candidate_mean_runtime_s'])} s`, while baseline mean runtime is `{fmt(worst['baseline_mean_runtime_s'])} s`.",
            f"- Candidate median runtime is `{fmt(worst['candidate_median_runtime_s'])} s`, so the outlier is not representative of every planner call.",
            "- Object counts are diagnostic hints only; frame-level profiling is still needed to identify the exact slow call.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze closed-loop runtime outliers.")
    parser.add_argument("--runner", required=True, type=Path)
    parser.add_argument("--baseline-runner", type=Path, default=None)
    parser.add_argument("--aggregated", type=Path, default=None)
    parser.add_argument("--log-root", required=True, type=Path)
    parser.add_argument("--output-csv", type=Path, default=Path("results/runtime_outlier_analysis.csv"))
    parser.add_argument("--output-md", type=Path, default=Path("results/runtime_outlier_analysis.md"))
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    prepare_imports()
    runner = pd.read_csv(project_path(args.runner))
    baseline_runner = pd.read_csv(project_path(args.baseline_runner)) if args.baseline_runner else None
    baseline_runtime = {}
    if baseline_runner is not None:
        baseline_runtime = dict(
            zip(
                baseline_runner["scenario_name"].astype(str),
                baseline_runner["compute_trajectory_runtimes_mean"].astype(float),
            )
        )
    types = scenario_type_map(args.aggregated)
    log_root = args.log_root

    rows = []
    for _, row in runner.iterrows():
        scenario = str(row["scenario_name"])
        candidate_mean = float(row["compute_trajectory_runtimes_mean"])
        candidate_median = float(row["compute_trajectory_runtimes_median"])
        baseline_mean = baseline_runtime.get(scenario, float("nan"))
        log_summary = summarize_log(find_log(log_root, scenario))
        rows.append(
            {
                "scenario_name": scenario,
                "scenario_type": types.get(scenario, ""),
                "candidate_mean_runtime_s": candidate_mean,
                "candidate_median_runtime_s": candidate_median,
                "candidate_runtime_std_s": float(row.get("compute_trajectory_runtimes_std", float("nan"))),
                "candidate_duration_s": float(row["duration"]),
                "baseline_mean_runtime_s": baseline_mean,
                "mean_runtime_delta_s": candidate_mean - baseline_mean
                if not math.isnan(baseline_mean)
                else float("nan"),
                **log_summary,
            }
        )

    rows = sorted(rows, key=lambda item: item["candidate_mean_runtime_s"], reverse=True)
    write_csv(rows, project_path(args.output_csv))
    write_markdown(rows, project_path(args.output_md), args.top_n)
    print(f"saved_csv={project_path(args.output_csv)}")
    print(f"saved_md={project_path(args.output_md)}")


if __name__ == "__main__":
    main()
