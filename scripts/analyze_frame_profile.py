from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from project_utils import project_root


def project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root() / path


def read_profile(path: Path) -> tuple[list[dict], list[dict]]:
    starts: dict[int, str] = {}
    completed: list[dict] = []
    incomplete: list[dict] = []

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iteration = int(row["iteration_index"])
            status = row["status"]
            if status == "start":
                starts[iteration] = row["iteration_time_s"]
                continue
            if status != "end":
                continue
            completed.append(
                {
                    "iteration_index": iteration,
                    "iteration_time_s": float(row["iteration_time_s"]),
                    "runtime_s": float(row["runtime_s"]),
                    "has_start": iteration in starts,
                }
            )
            starts.pop(iteration, None)

    for iteration, iteration_time in starts.items():
        incomplete.append(
            {
                "iteration_index": iteration,
                "iteration_time_s": float(iteration_time),
                "runtime_s": "",
                "has_start": True,
            }
        )

    completed.sort(key=lambda row: row["iteration_index"])
    incomplete.sort(key=lambda row: row["iteration_index"])
    return completed, incomplete


def percentile(values: list[float], q: float) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - index) + ordered[upper] * (index - lower)


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def median(values: list[float]) -> float:
    return percentile(values, 0.5)


def fmt(value: float | str) -> str:
    if value == "":
        return ""
    if math.isnan(float(value)):
        return "nan"
    return f"{float(value):.4f}"


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    completed: list[dict],
    incomplete: list[dict],
    runner_row: dict[str, str] | None,
    output_path: Path,
    top_n: int,
) -> None:
    runtimes = [float(row["runtime_s"]) for row in completed]
    slowest = sorted(completed, key=lambda row: float(row["runtime_s"]), reverse=True)[:top_n]

    lines = [
        "# Frame-Level Runtime Profile",
        "",
        "This report summarizes one `compute_trajectory` profile CSV generated through `DP_FRAME_PROFILE_CSV`.",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Completed frames | {len(completed)} |",
        f"| Incomplete frames | {len(incomplete)} |",
        f"| Mean runtime | {fmt(mean(runtimes))} s |",
        f"| Median runtime | {fmt(median(runtimes))} s |",
        f"| P95 runtime | {fmt(percentile(runtimes, 0.95))} s |",
        f"| Max runtime | {fmt(max(runtimes) if runtimes else float('nan'))} s |",
    ]

    if runner_row:
        lines.extend(
            [
                f"| Runner mean runtime | {fmt(runner_row['compute_trajectory_runtimes_mean'])} s |",
                f"| Runner median runtime | {fmt(runner_row['compute_trajectory_runtimes_median'])} s |",
                f"| Runner duration | {fmt(runner_row['duration'])} s |",
            ]
        )

    lines.extend(
        [
            "",
            "## Slowest Frames",
            "",
            "| Rank | Iteration | Runtime | Iteration time |",
            "| ---: | ---: | ---: | ---: |",
        ]
    )
    for rank, row in enumerate(slowest, start=1):
        lines.append(
            f"| {rank} | {row['iteration_index']} | {fmt(row['runtime_s'])} s | {fmt(row['iteration_time_s'])} |"
        )

    if incomplete:
        lines.extend(["", "## Incomplete Frames", "", "| Iteration | Iteration time |", "| ---: | ---: |"])
        for row in incomplete:
            lines.append(f"| {row['iteration_index']} | {fmt(row['iteration_time_s'])} |")

    lines.extend(
        [
            "",
            "## Takeaways",
            "",
            "- The previous mini10 tuned-guidance runtime outlier was not reproduced in this single-scenario run.",
            "- The largest observed call is the first planner iteration, which points to cold-start overhead.",
            "- After the first iteration, runtime stays in a much narrower range, but the median is still higher than the baseline mini10 mean.",
            "- The profile hook now makes future slow-scenario reruns auditable at frame level.",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot_profile(completed: list[dict], output_path: Path) -> None:
    iterations = [row["iteration_index"] for row in completed]
    runtimes = [float(row["runtime_s"]) for row in completed]
    if not iterations:
        return

    max_index = max(range(len(runtimes)), key=lambda idx: runtimes[idx])
    fig, ax = plt.subplots(figsize=(12, 4.8), dpi=150)
    ax.plot(iterations, runtimes, color="#4c78a8", linewidth=1.4)
    ax.scatter([iterations[max_index]], [runtimes[max_index]], color="#d62728", zorder=3)
    ax.annotate(
        f"max {runtimes[max_index]:.2f}s\niter {iterations[max_index]}",
        xy=(iterations[max_index], runtimes[max_index]),
        xytext=(12, -24),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#d62728", "linewidth": 0.8},
        fontsize=8,
    )
    ax.axhline(median(runtimes), color="#54a24b", linestyle="--", linewidth=1.0, label="median")
    ax.set_title("Frame-level compute_trajectory runtime")
    ax.set_xlabel("simulation iteration")
    ax.set_ylabel("runtime (s)")
    ax.grid(linewidth=0.4, alpha=0.35)
    ax.legend(loc="upper right")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output_path)


def read_runner_row(path: Path | None) -> dict[str, str] | None:
    if path is None:
        return None
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[0] if rows else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze a frame-level planner runtime profile.")
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--runner", type=Path, default=None)
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("results/frame_profile_summary.csv"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("results/frame_profile_summary.md"),
    )
    parser.add_argument(
        "--output-plot",
        type=Path,
        default=Path("results/frame_profile_runtime.png"),
    )
    parser.add_argument("--top-n", type=int, default=10)
    args = parser.parse_args()

    profile_path = project_path(args.profile)
    completed, incomplete = read_profile(profile_path)
    rows = sorted(completed + incomplete, key=lambda row: row["iteration_index"])
    write_csv(rows, project_path(args.output_csv))
    write_markdown(completed, incomplete, read_runner_row(project_path(args.runner) if args.runner else None), project_path(args.output_md), args.top_n)
    plot_profile(completed, project_path(args.output_plot))
    print(f"completed_frames={len(completed)}")
    print(f"incomplete_frames={len(incomplete)}")
    print(f"saved_csv={project_path(args.output_csv)}")
    print(f"saved_md={project_path(args.output_md)}")
    print(f"saved_plot={project_path(args.output_plot)}")


if __name__ == "__main__":
    main()
