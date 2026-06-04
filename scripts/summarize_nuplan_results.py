from __future__ import annotations

import argparse
import csv
import numbers
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, List

import pandas as pd


def latest_parquet(directory: Path) -> Path | None:
    files = sorted(directory.glob("*.parquet"), key=lambda path: path.stat().st_mtime, reverse=True)
    return files[0] if files else None


def scalar(value: Any) -> Any:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    if isinstance(value, (list, tuple, dict)):
        return str(value)
    if hasattr(value, "tolist") and not isinstance(value, numbers.Real):
        return str(value.tolist())
    return value


def fmt(value: Any, digits: int = 4) -> str:
    value = scalar(value)
    if value == "":
        return ""
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, numbers.Real) or not isinstance(value, str):
        try:
            numeric = float(value)
            return f"{numeric:.{digits}f}".rstrip("0").rstrip(".")
        except (TypeError, ValueError):
            pass
    return str(value)


def write_csv(rows: List[dict[str, Any]], output_path: Path, fieldnames: Iterable[str] | None = None) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        for row in rows:
            for key in row:
                if key not in keys:
                    keys.append(key)
        fieldnames = keys

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(fieldnames))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(item) for item in row) + " |")
    return "\n".join(lines)


def load_runner_report(run_root: Path) -> pd.DataFrame:
    path = run_root / "runner_report.parquet"
    if not path.exists():
        raise FileNotFoundError(f"runner_report.parquet not found under: {run_root}")
    return pd.read_parquet(path)


def load_aggregator(run_root: Path) -> tuple[pd.DataFrame | None, Path | None]:
    path = latest_parquet(run_root / "aggregator_metric")
    if path is None:
        return None, None
    return pd.read_parquet(path), path


def collect_metric_scores(run_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    metrics_dir = run_root / "metrics"
    if not metrics_dir.exists():
        return rows

    for path in sorted(metrics_dir.glob("*.parquet")):
        df = pd.read_parquet(path)
        stat_value_columns = [column for column in df.columns if column.endswith("_stat_value")]
        for _, row in df.iterrows():
            out = {
                "metric_file": path.name,
                "metric_statistics_name": scalar(row.get("metric_statistics_name", path.stem)),
                "scenario_name": scalar(row.get("scenario_name", "")),
                "scenario_type": scalar(row.get("scenario_type", "")),
                "log_name": scalar(row.get("log_name", "")),
                "planner_name": scalar(row.get("planner_name", "")),
                "metric_category": scalar(row.get("metric_category", "")),
                "metric_score": scalar(row.get("metric_score", "")),
                "metric_score_unit": scalar(row.get("metric_score_unit", "")),
            }
            for column in stat_value_columns:
                out[column] = scalar(row.get(column, ""))
            rows.append(out)

    return rows


def dataframe_rows(df: pd.DataFrame) -> list[dict[str, Any]]:
    return [{key: scalar(value) for key, value in row.items()} for row in df.to_dict("records")]


def final_score_row(aggregator: pd.DataFrame | None) -> pd.Series | None:
    if aggregator is None or aggregator.empty:
        return None
    candidates = aggregator[aggregator["scenario"].astype(str) == "final_score"]
    if candidates.empty and "scenario_type" in aggregator.columns:
        candidates = aggregator[aggregator["scenario_type"].astype(str) == "final_score"]
    if candidates.empty:
        return aggregator.tail(1).iloc[0]
    return candidates.iloc[0]


def write_summary(
    run_root: Path,
    runner: pd.DataFrame,
    aggregator: pd.DataFrame | None,
    aggregator_path: Path | None,
    metric_rows: list[dict[str, Any]],
    output_path: Path,
) -> None:
    total = len(runner)
    succeeded = int(runner["succeeded"].sum()) if "succeeded" in runner else 0
    failed = total - succeeded
    mean_duration = runner["duration"].mean() if "duration" in runner and total else 0.0
    mean_runtime = (
        runner["compute_trajectory_runtimes_mean"].mean()
        if "compute_trajectory_runtimes_mean" in runner and total
        else 0.0
    )
    median_runtime = (
        runner["compute_trajectory_runtimes_median"].mean()
        if "compute_trajectory_runtimes_median" in runner and total
        else 0.0
    )

    final = final_score_row(aggregator)
    final_score = scalar(final.get("score", "")) if final is not None else ""
    aggregator_by_scenario: dict[str, pd.Series] = {}
    if aggregator is not None and "scenario" in aggregator.columns:
        for _, row in aggregator.iterrows():
            scenario = scalar(row.get("scenario", ""))
            if scenario and scenario != "final_score":
                aggregator_by_scenario[str(scenario)] = row

    lines = [
        "# nuPlan mini evaluation summary",
        "",
        f"- generated_at: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`",
        f"- run_root: `{run_root}`",
        f"- aggregator_file: `{aggregator_path.name if aggregator_path else ''}`",
        "",
        "## Run status",
        "",
        markdown_table(
            ["total", "succeeded", "failed", "mean_duration_s", "mean_compute_runtime_s", "median_compute_runtime_s"],
            [[total, succeeded, failed, mean_duration, mean_runtime, median_runtime]],
        ),
        "",
        "## Final score",
        "",
        markdown_table(["score"], [[final_score]]),
        "",
    ]

    if final is not None:
        metric_columns = [
            column
            for column in aggregator.columns
            if column
            not in {
                "scenario",
                "log_name",
                "scenario_type",
                "num_scenarios",
                "planner_name",
                "aggregator_type",
                "score",
            }
            and scalar(final.get(column, "")) != ""
        ]
        lines.extend(
            [
                "## Aggregated metric components",
                "",
                markdown_table(["metric", "value"], [[column, final.get(column, "")] for column in metric_columns]),
                "",
            ]
        )

    scenario_rows = []
    for _, row in runner.iterrows():
        scenario_name = str(scalar(row.get("scenario_name", "")))
        scenario_metric_row = aggregator_by_scenario.get(scenario_name)
        scenario_rows.append(
            [
                row.get("succeeded", ""),
                scenario_name,
                scenario_metric_row.get("scenario_type", "") if scenario_metric_row is not None else "",
                scenario_metric_row.get("score", "") if scenario_metric_row is not None else "",
                row.get("log_name", ""),
                row.get("planner_name", ""),
                row.get("duration", ""),
                row.get("compute_trajectory_runtimes_mean", ""),
                row.get("error_message", ""),
            ]
        )
    lines.extend(
        [
            "## Scenario runner report",
            "",
            markdown_table(
                [
                    "succeeded",
                    "scenario_name",
                    "scenario_type",
                    "score",
                    "log_name",
                    "planner",
                    "duration_s",
                    "mean_runtime_s",
                    "error",
                ],
                scenario_rows,
            ),
            "",
            "## Metric files",
            "",
            markdown_table([ "metric_rows" ], [[len(metric_rows)]]),
            "",
            "## Boundary",
            "",
            "This is a mini-split engineering evaluation. It verifies the local closed-loop pipeline, "
            "but it is not a paper-score reproduction on the official full benchmark split.",
            "",
        ]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a nuPlan simulation run.")
    parser.add_argument("--run-root", required=True, type=Path, help="nuPlan simulation run output directory.")
    parser.add_argument("--output-dir", default=Path("results"), type=Path)
    parser.add_argument("--prefix", default="mini_eval")
    args = parser.parse_args()

    run_root = args.run_root.resolve()
    output_dir = args.output_dir.resolve()

    runner = load_runner_report(run_root)
    aggregator, aggregator_path = load_aggregator(run_root)
    metric_rows = collect_metric_scores(run_root)

    runner_rows = dataframe_rows(runner)
    write_csv(runner_rows, output_dir / f"{args.prefix}_runner_report.csv")

    if aggregator is not None:
        write_csv(dataframe_rows(aggregator), output_dir / f"{args.prefix}_aggregated_metrics.csv")

    if metric_rows:
        write_csv(metric_rows, output_dir / f"{args.prefix}_metric_scores.csv")

    write_summary(
        run_root=run_root,
        runner=runner,
        aggregator=aggregator,
        aggregator_path=aggregator_path,
        metric_rows=metric_rows,
        output_path=output_dir / f"{args.prefix}_summary.md",
    )

    print(f"summary_md={output_dir / f'{args.prefix}_summary.md'}")
    print(f"runner_csv={output_dir / f'{args.prefix}_runner_report.csv'}")
    if aggregator is not None:
        print(f"aggregated_metrics_csv={output_dir / f'{args.prefix}_aggregated_metrics.csv'}")
    if metric_rows:
        print(f"metric_scores_csv={output_dir / f'{args.prefix}_metric_scores.csv'}")


if __name__ == "__main__":
    main()
