from __future__ import annotations

import argparse
import csv
import textwrap
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pandas as pd
from matplotlib import pyplot as plt

from project_utils import project_root


METRIC_COLUMNS = [
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


def scenario_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        df["log_name"].notna()
        & (df["scenario"].astype(str) != "final_score")
        & df["score"].notna()
    ].copy()


def final_row(df: pd.DataFrame) -> pd.Series:
    rows = df[df["scenario"].astype(str) == "final_score"]
    if rows.empty:
        return df.tail(1).iloc[0]
    return rows.iloc[0]


def fmt(value: float) -> str:
    return f"{value:.4f}"


def write_csv(rows: list[dict], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(
    rows: list[dict],
    final_summary: dict[str, float],
    output_path: Path,
    baseline_label: str,
    candidate_label: str,
) -> None:
    scenario_count = len(rows)
    lines = [
        "# Evaluation Run Comparison",
        "",
        f"Baseline: `{baseline_label}`",
        "",
        f"Candidate: `{candidate_label}`",
        "",
        "## Final Score",
        "",
        "| Metric | Baseline | Candidate | Delta |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key, value in final_summary.items():
        if not key.endswith("_delta"):
            delta = final_summary.get(f"{key}_delta")
            if delta is not None:
                lines.append(f"| {key} | {fmt(value)} | {fmt(final_summary[key + '_candidate'])} | {fmt(delta)} |")

    lines.extend(
        [
            "",
            "## Scenario Score Delta",
            "",
            "| Scenario Type | Scenario Token | Baseline | Candidate | Delta | Main candidate limits |",
            "| --- | --- | ---: | ---: | ---: | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {scenario_type} | {scenario} | {baseline_score:.4f} | {candidate_score:.4f} | {score_delta:.4f} | {limits} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- A positive delta means the candidate run scored higher than the baseline on the same scenario token.",
            "- A zero candidate score usually indicates a hard metric failure such as at-fault collision or time-to-collision violation.",
            f"- This comparison uses the same {scenario_count} mini scenario tokens, so it is useful for debugging guidance behavior, but it is still not a paper-level benchmark.",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def plot(rows: list[dict], output_path: Path, baseline_label: str, candidate_label: str) -> None:
    labels = [textwrap.fill(row["scenario_type"].replace("_", " "), width=24) for row in rows]
    baseline = [row["baseline_score"] for row in rows]
    candidate = [row["candidate_score"] for row in rows]
    y = list(range(len(rows)))

    fig, ax = plt.subplots(figsize=(9, 5.4), dpi=150)
    height = 0.36
    ax.barh([pos - height / 2 for pos in y], baseline, height=height, label=baseline_label, color="#4c78a8")
    ax.barh([pos + height / 2 for pos in y], candidate, height=height, label=candidate_label, color="#f58518")
    ax.set_xlim(0, 1.05)
    ax.set_yticks(y, labels)
    ax.set_xlabel("weighted scenario score")
    ax.set_title(f"Baseline vs Guidance mini evaluation ({len(rows)} scenarios)")
    ax.grid(axis="x", linewidth=0.4, alpha=0.35)
    ax.legend(loc="lower right")
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)


def limiting_metrics(row: pd.Series, suffix: str) -> str:
    limits = []
    for column in METRIC_COLUMNS:
        if column == "score":
            continue
        value = row.get(f"{column}_{suffix}")
        if pd.isna(value):
            continue
        numeric = float(value)
        if numeric < 0.999:
            limits.append(f"{column}={numeric:.4f}")
    return "; ".join(limits) or "none below 0.999"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two mini evaluation runs.")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--baseline-label", default="baseline")
    parser.add_argument("--candidate-label", default="candidate")
    parser.add_argument("--output-md", type=Path, default=Path("results/eval_run_comparison.md"))
    parser.add_argument("--output-csv", type=Path, default=Path("results/eval_run_comparison.csv"))
    parser.add_argument("--output-png", type=Path, default=Path("results/eval_run_comparison.png"))
    args = parser.parse_args()

    baseline = pd.read_csv(project_path(args.baseline))
    candidate = pd.read_csv(project_path(args.candidate))

    baseline_scenarios = scenario_rows(baseline)
    candidate_scenarios = scenario_rows(candidate)
    merged = baseline_scenarios.merge(
        candidate_scenarios,
        on="scenario",
        suffixes=("_baseline", "_candidate"),
    )
    merged["score_delta"] = merged["score_candidate"].astype(float) - merged["score_baseline"].astype(float)
    merged = merged.sort_values("score_delta")

    rows = []
    for _, row in merged.iterrows():
        rows.append(
            {
                "scenario": row["scenario"],
                "scenario_type": row["scenario_type_baseline"],
                "baseline_score": float(row["score_baseline"]),
                "candidate_score": float(row["score_candidate"]),
                "score_delta": float(row["score_delta"]),
                "limits": limiting_metrics(row, "candidate"),
            }
        )

    baseline_final = final_row(baseline)
    candidate_final = final_row(candidate)
    final_summary = {}
    for column in METRIC_COLUMNS:
        if column in baseline_final.index and column in candidate_final.index:
            baseline_value = float(baseline_final[column])
            candidate_value = float(candidate_final[column])
            final_summary[column] = baseline_value
            final_summary[f"{column}_candidate"] = candidate_value
            final_summary[f"{column}_delta"] = candidate_value - baseline_value

    write_csv(rows, project_path(args.output_csv))
    write_markdown(
        rows,
        final_summary,
        project_path(args.output_md),
        baseline_label=args.baseline_label,
        candidate_label=args.candidate_label,
    )
    plot(rows, project_path(args.output_png), args.baseline_label, args.candidate_label)
    print(f"saved_md={project_path(args.output_md)}")
    print(f"saved_csv={project_path(args.output_csv)}")
    print(f"saved_plot={project_path(args.output_png)}")


if __name__ == "__main__":
    main()
