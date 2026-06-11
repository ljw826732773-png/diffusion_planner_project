from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt

from project_utils import prepare_imports, project_root
from visualize_nuplan_trajectory import load_simulation_log, path_length, relative, trajectory_xy


COLORS = ["#4c78a8", "#f58518", "#54a24b", "#e45756", "#b279a2", "#72b7b2"]


def project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root() / path


def parse_run(value: str) -> dict:
    parts = value.split("|", 3)
    if len(parts) != 4:
        raise ValueError(
            "Run must be formatted as label|scale|score|log_file, "
            f"got: {value}"
        )
    label, scale, score, log_file = parts
    return {
        "label": label,
        "scale": scale,
        "score": float(score),
        "log_file": Path(log_file),
    }


def center_xy(state) -> tuple[float, float]:
    center = state.center
    return float(center.x), float(center.y)


def endpoint_error(points: list[tuple[float, float]], reference: list[tuple[float, float]]) -> float:
    if not points or not reference:
        return float("nan")
    index = min(len(points), len(reference)) - 1
    return math.hypot(points[index][0] - reference[index][0], points[index][1] - reference[index][1])


def average_error(points: list[tuple[float, float]], reference: list[tuple[float, float]]) -> float:
    count = min(len(points), len(reference))
    if count == 0:
        return float("nan")
    return sum(
        math.hypot(points[index][0] - reference[index][0], points[index][1] - reference[index][1])
        for index in range(count)
    ) / count


def max_error(points: list[tuple[float, float]], reference: list[tuple[float, float]]) -> float:
    count = min(len(points), len(reference))
    if count == 0:
        return float("nan")
    return max(
        math.hypot(points[index][0] - reference[index][0], points[index][1] - reference[index][1])
        for index in range(count)
    )


def collect(run: dict, origin: tuple[float, float] | None) -> tuple[dict, tuple[float, float]]:
    log = load_simulation_log(run["log_file"])
    history = list(log.simulation_history.data)
    if not history:
        raise RuntimeError(f"No history samples found in {run['log_file']}")

    executed_abs = trajectory_xy([sample.ego_state for sample in history])
    if origin is None:
        origin = executed_abs[0]

    scenario = log.scenario
    expert_abs = trajectory_xy(scenario.get_expert_ego_trajectory())
    executed = relative(executed_abs, origin)
    expert = relative(expert_abs, origin)
    final_plan = relative(trajectory_xy(history[-1].trajectory.get_sampled_trajectory()), origin)

    row = {
        "label": run["label"],
        "scale": run["scale"],
        "score": run["score"],
        "scenario_name": getattr(scenario, "scenario_name", "unknown"),
        "scenario_type": getattr(scenario, "scenario_type", "unknown"),
        "log_name": getattr(scenario, "log_name", "unknown"),
        "num_executed_points": len(executed),
        "executed_path_length_m": path_length(executed),
        "expert_path_length_m": path_length(expert),
        "path_length_delta_m": path_length(executed) - path_length(expert[: len(executed)]),
        "avg_error_to_expert_m": average_error(executed, expert),
        "max_error_to_expert_m": max_error(executed, expert),
        "endpoint_error_to_expert_m": endpoint_error(executed, expert),
        "end_x_m": executed[-1][0],
        "end_y_m": executed[-1][1],
        "final_plan_path_length_m": path_length(final_plan),
    }
    return {
        "run": run,
        "row": row,
        "executed": executed,
        "expert": expert,
        "final_plan": final_plan,
    }, origin


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def format_float(value: float) -> str:
    if math.isnan(value):
        return "nan"
    return f"{value:.3f}"


def write_markdown(rows: list[dict], output_path: Path) -> None:
    scenario_type = rows[0]["scenario_type"]
    scenario_name = rows[0]["scenario_name"]
    best = min(rows, key=lambda row: row["avg_error_to_expert_m"])
    worst = max(rows, key=lambda row: row["avg_error_to_expert_m"])
    successful = [row for row in rows if row["score"] > 0.0]
    failed = [row for row in rows if row["score"] <= 0.0]
    success_labels = ", ".join(f"`{row['label']}`" for row in successful) or "none"
    failed_labels = ", ".join(f"`{row['label']}`" for row in failed) or "none"
    failed_lengths = [row["executed_path_length_m"] for row in failed]
    failed_length_text = (
        f"{min(failed_lengths):.3f}-{max(failed_lengths):.3f} m"
        if failed_lengths
        else "n/a"
    )

    lines = [
        "# Stop-sign Guidance Trajectory Comparison",
        "",
        f"Scenario: `{scenario_type}` / `{scenario_name}`",
        "",
        "| Run | Scale | Score | Path length | Avg error to expert | Max error | Endpoint error |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            "| {label} | {scale} | {score:.4f} | {path_length} m | {avg_error} m | {max_error} m | {endpoint_error} m |".format(
                label=row["label"],
                scale=row["scale"],
                score=row["score"],
                path_length=format_float(row["executed_path_length_m"]),
                avg_error=format_float(row["avg_error_to_expert_m"]),
                max_error=format_float(row["max_error_to_expert_m"]),
                endpoint_error=format_float(row["endpoint_error_to_expert_m"]),
            )
        )
    lines.extend(
        [
            "",
            "## Takeaways",
            "",
            f"- Successful runs in this scenario: {success_labels}. Failed hard-score runs: {failed_labels}.",
            f"- Closest executed path to the expert by average error: `{best['label']}`.",
            f"- Largest average deviation from the expert: `{worst['label']}`.",
            f"- Failed runs have executed path lengths in the range `{failed_length_text}`, compared with baseline `{rows[0]['executed_path_length_m']:.3f} m`.",
            "- The metric score still matters more than geometric closeness alone: collision/TTC hard failures can occur even when the path shape looks broadly plausible.",
            "- This figure is a static trajectory diagnostic. NuBoard is still needed to inspect actor-level interactions frame by frame.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(collected: list[dict], output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.0, 7.2), dpi=160)
    expert = collected[0]["expert"]
    ax.plot(
        [point[0] for point in expert],
        [point[1] for point in expert],
        color="#222222",
        linewidth=2.2,
        linestyle="--",
        label="expert",
    )

    all_paths = [expert]
    for index, item in enumerate(collected):
        color = COLORS[index % len(COLORS)]
        points = item["executed"]
        row = item["row"]
        all_paths.append(points)
        label = f"{row['label']} score={row['score']:.3f}"
        ax.plot(
            [point[0] for point in points],
            [point[1] for point in points],
            color=color,
            linewidth=2.0,
            label=label,
        )
        ax.scatter(points[0][0], points[0][1], color=color, s=28, marker="o")
        ax.scatter(points[-1][0], points[-1][1], color=color, s=42, marker="x")

    all_points = [point for path in all_paths for point in path]
    xs = [point[0] for point in all_points]
    ys = [point[1] for point in all_points]
    x_span = max(max(xs) - min(xs), 1.0)
    y_span = max(max(ys) - min(ys), 1.0)
    ax.set_xlim(min(xs) - x_span * 0.08, max(xs) + x_span * 0.08)
    ax.set_ylim(min(ys) - y_span * 0.12, max(ys) + y_span * 0.12)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(linewidth=0.4, alpha=0.35)
    ax.set_xlabel("x relative to first baseline ego pose (m)")
    ax.set_ylabel("y relative to first baseline ego pose (m)")
    scenario_type = collected[0]["row"]["scenario_type"]
    scenario_name = collected[0]["row"]["scenario_name"]
    ax.set_title(f"{scenario_type}\n{scenario_name}")
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), borderaxespad=0.0, fontsize=8)
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare executed trajectories across guidance runs.")
    parser.add_argument(
        "--run",
        action="append",
        required=True,
        help="Run spec: label|scale|score|log_file. Use scale 0 for baseline.",
    )
    parser.add_argument(
        "--output-png",
        type=Path,
        default=Path("results/guidance_stop_sign_trajectory_comparison.png"),
    )
    parser.add_argument(
        "--output-csv",
        type=Path,
        default=Path("results/guidance_stop_sign_trajectory_comparison.csv"),
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=Path("results/guidance_stop_sign_trajectory_comparison.md"),
    )
    args = parser.parse_args()

    prepare_imports()
    origin = None
    collected = []
    for run_value in args.run:
        item, origin = collect(parse_run(run_value), origin)
        collected.append(item)

    rows = [item["row"] for item in collected]
    write_csv(rows, project_path(args.output_csv))
    write_markdown(rows, project_path(args.output_md))
    plot(collected, project_path(args.output_png))

    print(f"saved_csv={project_path(args.output_csv)}")
    print(f"saved_md={project_path(args.output_md)}")
    print(f"saved_plot={project_path(args.output_png)}")


if __name__ == "__main__":
    main()
