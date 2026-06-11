from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd
from matplotlib import pyplot as plt

from project_utils import project_root


FINAL_METRICS = [
    "score",
    "ego_is_comfortable",
    "ego_progress_along_expert_route",
    "no_ego_at_fault_collisions",
    "speed_limit_compliance",
    "time_to_collision_within_bound",
]


def project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root() / path


def parse_run(value: str) -> tuple[float, str, Path, Path]:
    parts = value.split("=", 1)
    if len(parts) != 2:
        raise ValueError(f"Run must be scale=aggregated.csv:runner.csv, got: {value}")
    scale = float(parts[0])
    paths = parts[1].split(":", 1)
    if len(paths) != 2:
        raise ValueError(f"Run must include aggregated and runner paths, got: {value}")
    label = "baseline" if scale == 0 else f"scale_{scale:g}"
    return scale, label, project_path(Path(paths[0])), project_path(Path(paths[1]))


def final_row(df: pd.DataFrame) -> pd.Series:
    rows = df[df["scenario"].astype(str) == "final_score"]
    if rows.empty:
        return df.tail(1).iloc[0]
    return rows.iloc[0]


def scenario_row(df: pd.DataFrame, scenario_type: str) -> pd.Series | None:
    rows = df[
        df["log_name"].notna()
        & (df["scenario_type"].astype(str) == scenario_type)
        & df["score"].notna()
    ]
    if rows.empty:
        return None
    return rows.iloc[0]


def numeric(row: pd.Series | None, column: str) -> float:
    if row is None or column not in row.index or pd.isna(row[column]):
        return float("nan")
    return float(row[column])


def format_scales(rows: list[dict]) -> str:
    return ", ".join(f"`{row['scale']:g}`" for row in rows) or "none"


def collect_row(scale: float, label: str, aggregated_path: Path, runner_path: Path) -> dict:
    aggregated = pd.read_csv(aggregated_path)
    runner = pd.read_csv(runner_path)
    final = final_row(aggregated)
    stop_sign = scenario_row(aggregated, "stopping_at_stop_sign_with_lead")

    row = {
        "scale": scale,
        "label": label,
        "num_scenarios": len(runner),
        "mean_runtime_s": runner["compute_trajectory_runtimes_mean"].astype(float).mean(),
        "max_runtime_s": runner["compute_trajectory_runtimes_mean"].astype(float).max(),
        "stop_sign_score": numeric(stop_sign, "score"),
        "stop_sign_collision": numeric(stop_sign, "no_ego_at_fault_collisions"),
        "stop_sign_ttc": numeric(stop_sign, "time_to_collision_within_bound"),
        "stop_sign_comfort": numeric(stop_sign, "ego_is_comfortable"),
    }
    for metric in FINAL_METRICS:
        row[metric] = numeric(final, metric)
    return row


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(rows: list[dict], output_path: Path) -> None:
    best = max(rows, key=lambda row: row["score"])
    stable_stop_sign = [row for row in rows if row["stop_sign_score"] >= 0.999]
    failed_stop_sign = [row for row in rows if row["stop_sign_score"] < 0.999]
    stable_labels = format_scales(stable_stop_sign)
    failed_labels = format_scales(failed_stop_sign)
    strong_failures = [
        row
        for row in rows
        if row["no_ego_at_fault_collisions"] < 1.0
        or row["time_to_collision_within_bound"] < 1.0
    ]
    safety_line = (
        f"- Safety metric degradation appears at scales: {format_scales(strong_failures)}."
        if strong_failures
        else "- No aggregate collision/TTC degradation appeared in this mini sweep."
    )
    lines = [
        "# Guidance Scale Sweep",
        "",
        "This sweep compares the baseline planner with guidance-enabled runs on the same five mini scenario tokens.",
        "",
        "| Scale | Final score | Collision | TTC | Comfort | Progress | Speed limit | Stop-sign score | Mean runtime |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {scale:g} | {score:.4f} | {no_ego_at_fault_collisions:.4f} | {time_to_collision_within_bound:.4f} | {ego_is_comfortable:.4f} | {ego_progress_along_expert_route:.4f} | {speed_limit_compliance:.4f} | {stop_sign_score:.4f} | {mean_runtime_s:.4f} s |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "## Takeaways",
            "",
            f"- Best final score in this sweep: scale `{best['scale']:g}` with score `{best['score']:.4f}`.",
            f"- Stop-sign scenario preserved full score at scales: {stable_labels}.",
            f"- Stop-sign hard-score degradation appeared at scales: {failed_labels}.",
            safety_line,
            "- This suggests the current collision guidance is too strong or poorly timed for at least one stop-sign scenario.",
            "- These are mini-split diagnostics, not full benchmark conclusions.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(rows: list[dict], output_path: Path) -> None:
    labels = [f"{row['scale']:g}" for row in rows]
    final_scores = [row["score"] for row in rows]
    stop_sign = [row["stop_sign_score"] for row in rows]
    collision = [row["no_ego_at_fault_collisions"] for row in rows]
    ttc = [row["time_to_collision_within_bound"] for row in rows]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), dpi=150)
    x = range(len(rows))

    axes[0].plot(x, final_scores, marker="o", label="final score", color="#4c78a8")
    axes[0].plot(x, stop_sign, marker="o", label="stop-sign scenario", color="#f58518")
    axes[0].set_xticks(list(x), labels)
    axes[0].set_ylim(-0.02, 1.05)
    axes[0].set_xlabel("guidance scale (0 = baseline)")
    axes[0].set_ylabel("score")
    axes[0].set_title("Score vs guidance scale")
    axes[0].grid(linewidth=0.4, alpha=0.35)
    axes[0].legend()

    axes[1].plot(x, collision, marker="o", label="collision metric", color="#54a24b")
    axes[1].plot(x, ttc, marker="o", label="TTC metric", color="#e45756")
    axes[1].set_xticks(list(x), labels)
    axes[1].set_ylim(-0.02, 1.05)
    axes[1].set_xlabel("guidance scale (0 = baseline)")
    axes[1].set_ylabel("metric score")
    axes[1].set_title("Hard safety metrics")
    axes[1].grid(linewidth=0.4, alpha=0.35)
    axes[1].legend()

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize guidance scale sweep results.")
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Run spec: scale=aggregated.csv:runner.csv. Use scale 0 for baseline.",
    )
    parser.add_argument("--output-csv", type=Path, default=Path("results/guidance_scale_sweep.csv"))
    parser.add_argument("--output-md", type=Path, default=Path("results/guidance_scale_sweep.md"))
    parser.add_argument("--output-png", type=Path, default=Path("results/guidance_scale_sweep.png"))
    args = parser.parse_args()

    rows = [collect_row(*parse_run(run)) for run in args.run]
    rows = sorted(rows, key=lambda row: row["scale"])
    write_csv(rows, project_path(args.output_csv))
    write_markdown(rows, project_path(args.output_md))
    plot(rows, project_path(args.output_png))
    print(f"saved_csv={project_path(args.output_csv)}")
    print(f"saved_md={project_path(args.output_md)}")
    print(f"saved_plot={project_path(args.output_png)}")


if __name__ == "__main__":
    main()
