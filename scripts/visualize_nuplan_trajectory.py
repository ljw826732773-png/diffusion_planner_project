from __future__ import annotations

import argparse
import csv
import lzma
import math
import pickle
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import msgpack
from matplotlib import pyplot as plt

from project_utils import prepare_imports, project_root


def load_simulation_log(path: Path):
    return pickle.loads(msgpack.unpackb(lzma.decompress(path.read_bytes()), raw=False))


def center_xy(state):
    center = state.center
    return float(center.x), float(center.y)


def trajectory_xy(states):
    points = []
    for state in states:
        points.append(center_xy(state))
    return points


def relative(points, origin):
    ox, oy = origin
    return [(x - ox, y - oy) for x, y in points]


def path_length(points):
    if len(points) < 2:
        return 0.0
    return sum(
        math.hypot(points[index][0] - points[index - 1][0], points[index][1] - points[index - 1][1])
        for index in range(1, len(points))
    )


def write_summary(rows, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "name",
        "num_points",
        "start_x_m",
        "start_y_m",
        "end_x_m",
        "end_y_m",
        "path_length_m",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_path(name, points):
    if points:
        start_x, start_y = points[0]
        end_x, end_y = points[-1]
    else:
        start_x = start_y = end_x = end_y = 0.0
    return {
        "name": name,
        "num_points": len(points),
        "start_x_m": start_x,
        "start_y_m": start_y,
        "end_x_m": end_x,
        "end_y_m": end_y,
        "path_length_m": path_length(points),
    }


def plot_path(ax, points, label, color, linewidth=2.0, alpha=1.0, linestyle="-"):
    if not points:
        return
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    ax.plot(xs, ys, label=label, color=color, linewidth=linewidth, alpha=alpha, linestyle=linestyle)
    ax.scatter([xs[0]], [ys[0]], color=color, s=28, marker="o", alpha=alpha)
    ax.scatter([xs[-1]], [ys[-1]], color=color, s=36, marker="x", alpha=alpha)


def set_readable_limits(ax, paths) -> None:
    all_points = [point for points in paths for point in points]
    if not all_points:
        return
    xs = [point[0] for point in all_points]
    ys = [point[1] for point in all_points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    x_span = max(max_x - min_x, 1.0)
    y_span = max(max_y - min_y, 1.0)
    x_center = (min_x + max_x) / 2.0
    y_center = (min_y + max_y) / 2.0
    half_x = max(x_span * 0.55, min(y_span * 0.18, 18.0), 5.0)
    half_y = max(y_span * 0.55, 5.0)
    ax.set_xlim(x_center - half_x, x_center + half_x)
    ax.set_ylim(y_center - half_y, y_center + half_y)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot real nuPlan simulation trajectories.")
    parser.add_argument("--log-file", required=True, type=Path, help="Path to a .msgpack.xz simulation log.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/nuplan_low_score_trajectory.png"),
        help="Output PNG path.",
    )
    parser.add_argument(
        "--summary-output",
        type=Path,
        default=Path("results/nuplan_low_score_trajectory_summary.csv"),
        help="Output CSV path.",
    )
    parser.add_argument("--score", default="", help="Optional scenario score displayed in the title.")
    parser.add_argument("--planned-every", type=int, default=40, help="Plot every Nth planned future.")
    args = parser.parse_args()

    prepare_imports()
    log = load_simulation_log(args.log_file)
    history = list(log.simulation_history.data)
    if not history:
        raise RuntimeError(f"No history samples found in {args.log_file}")

    scenario = log.scenario
    scenario_name = getattr(scenario, "scenario_name", "unknown")
    scenario_type = getattr(scenario, "scenario_type", "unknown")
    log_name = getattr(scenario, "log_name", "unknown")

    executed_abs = trajectory_xy([sample.ego_state for sample in history])
    origin = executed_abs[0]
    executed = relative(executed_abs, origin)

    expert_abs = trajectory_xy(scenario.get_expert_ego_trajectory())
    expert = relative(expert_abs, origin)

    first_plan = relative(trajectory_xy(history[0].trajectory.get_sampled_trajectory()), origin)
    last_plan = relative(trajectory_xy(history[-1].trajectory.get_sampled_trajectory()), origin)

    fig, ax = plt.subplots(figsize=(8.5, 7.0), dpi=160)
    plot_path(ax, expert, "expert ego", "#2ca02c", linewidth=2.0, alpha=0.85, linestyle="--")
    plot_path(ax, executed, "executed ego", "#1f77b4", linewidth=2.4, alpha=0.95)
    plot_path(ax, first_plan, "planner future at t=0", "#ff7f0e", linewidth=1.8, alpha=0.85)
    plot_path(ax, last_plan, "planner future at final step", "#9467bd", linewidth=1.6, alpha=0.75)

    for index, sample in enumerate(history):
        if index == 0 or index == len(history) - 1 or index % args.planned_every != 0:
            continue
        planned = relative(trajectory_xy(sample.trajectory.get_sampled_trajectory()), origin)
        plot_path(ax, planned, "_planner intermediate", "#888888", linewidth=0.8, alpha=0.22)

    score_text = f" | score={args.score}" if args.score else ""
    ax.set_title(f"{scenario_type}\n{scenario_name}{score_text}")
    ax.set_xlabel("x relative to first ego pose (m)")
    ax.set_ylabel("y relative to first ego pose (m)")
    set_readable_limits(ax, [expert, executed, first_plan, last_plan])
    ax.set_aspect("equal", adjustable="box")
    ax.grid(linewidth=0.4, alpha=0.35)
    ax.legend(loc="best", fontsize=8)
    fig.text(0.01, 0.01, f"log={log_name}", fontsize=7, color="#555555")
    plt.tight_layout()

    output = args.output
    if not output.is_absolute():
        output = project_root() / output
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output)

    summary_output = args.summary_output
    if not summary_output.is_absolute():
        summary_output = project_root() / summary_output
    write_summary(
        [
            summarize_path("expert_ego", expert),
            summarize_path("executed_ego", executed),
            summarize_path("planner_future_t0", first_plan),
            summarize_path("planner_future_final", last_plan),
        ],
        summary_output,
    )
    print(f"saved_plot={output}")
    print(f"saved_summary={summary_output}")


if __name__ == "__main__":
    main()
