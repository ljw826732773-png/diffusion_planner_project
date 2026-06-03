from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from statistics import mean, median

import matplotlib

matplotlib.use("Agg")

import torch
from matplotlib import pyplot as plt

from project_utils import (
    build_synthetic_inputs,
    checkpoint_paths,
    prepare_imports,
    strip_module_prefix,
    workspace_root,
)


def parse_int_list(value: str):
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def synchronize(device: str) -> None:
    if device == "cuda":
        torch.cuda.synchronize()


def time_once(fn, device: str) -> float:
    synchronize(device)
    start = time.perf_counter()
    fn()
    synchronize(device)
    return (time.perf_counter() - start) * 1000.0


def summarize(times_ms, batch_size: int):
    calls_per_second = 1000.0 / mean(times_ms)
    return {
        "mean_ms": mean(times_ms),
        "median_ms": median(times_ms),
        "min_ms": min(times_ms),
        "max_ms": max(times_ms),
        "calls_per_second": calls_per_second,
        "samples_per_second": calls_per_second * batch_size,
    }


def run_benchmark(model, cfg, device: str, mode: str, batch_size: int, warmup: int, iterations: int):
    raw_inputs = build_synthetic_inputs(cfg, device, batch_size=batch_size)
    inputs = cfg.observation_normalizer(raw_inputs)

    if mode == "denoise_forward":
        model.train()

        def fn():
            with torch.no_grad():
                _, decoder_outputs = model(inputs)
                _ = decoder_outputs["score"].detach()

    elif mode == "sampling_inference":
        model.eval()
        sampling_inputs = {
            key: value
            for key, value in inputs.items()
            if key not in {"sampled_trajectories", "diffusion_time"}
        }

        def fn():
            with torch.no_grad():
                _, decoder_outputs = model(sampling_inputs)
                _ = decoder_outputs["prediction"].detach()

    else:
        raise ValueError(f"Unknown mode: {mode}")

    for _ in range(warmup):
        fn()

    if device == "cuda":
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()

    times_ms = [time_once(fn, device) for _ in range(iterations)]
    stats = summarize(times_ms, batch_size)
    peak_memory_mb = (
        torch.cuda.max_memory_allocated() / (1024 * 1024) if device == "cuda" else 0.0
    )

    return {
        "mode": mode,
        "batch_size": batch_size,
        "iterations": iterations,
        "warmup": warmup,
        "device": device,
        "torch": torch.__version__,
        "peak_memory_mb": peak_memory_mb,
        **stats,
    }


def write_csv(rows, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "mode",
        "batch_size",
        "iterations",
        "warmup",
        "device",
        "torch",
        "mean_ms",
        "median_ms",
        "min_ms",
        "max_ms",
        "calls_per_second",
        "samples_per_second",
        "peak_memory_mb",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_results(rows, output_path: Path) -> None:
    labels = [f"{row['mode']}\nbs={row['batch_size']}" for row in rows]
    latencies = [row["mean_ms"] for row in rows]
    memories = [row["peak_memory_mb"] for row in rows]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5), dpi=150)
    y_positions = range(len(labels))

    axes[0].barh(y_positions, latencies, color="#4c78a8")
    axes[0].set_title("Mean Latency")
    axes[0].set_xlabel("ms")
    axes[0].set_yticks(list(y_positions), labels)
    axes[0].invert_yaxis()
    axes[0].grid(axis="x", linewidth=0.4, alpha=0.35)

    axes[1].barh(y_positions, memories, color="#f58518")
    axes[1].set_title("Peak CUDA Memory")
    axes[1].set_xlabel("MB")
    axes[1].set_yticks(list(y_positions), labels)
    axes[1].invert_yaxis()
    axes[1].grid(axis="x", linewidth=0.4, alpha=0.35)

    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Diffusion-Planner synthetic inference.")
    parser.add_argument("--batch-sizes", default="1", help="Comma-separated batch sizes, e.g. 1,2")
    parser.add_argument(
        "--modes",
        default="denoise_forward,sampling_inference",
        help="Comma-separated modes: denoise_forward,sampling_inference",
    )
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--sampling-iterations", type=int, default=5)
    args = parser.parse_args()

    repo = prepare_imports()

    from diffusion_planner.model.diffusion_planner import Diffusion_Planner
    from diffusion_planner.utils.config import Config

    paths = checkpoint_paths(repo)
    cfg = Config(str(paths["args"]), None)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg.device = device

    model = Diffusion_Planner(cfg).to(device)
    checkpoint = torch.load(paths["model"], map_location=device)
    model.load_state_dict(strip_module_prefix(checkpoint["ema_state_dict"]), strict=True)

    rows = []
    for batch_size in parse_int_list(args.batch_sizes):
        for mode in [item.strip() for item in args.modes.split(",") if item.strip()]:
            iterations = args.sampling_iterations if mode == "sampling_inference" else args.iterations
            result = run_benchmark(model, cfg, device, mode, batch_size, args.warmup, iterations)
            rows.append(result)
            print(
                f"{mode} bs={batch_size}: "
                f"mean={result['mean_ms']:.2f}ms, "
                f"calls/s={result['calls_per_second']:.2f}, "
                f"samples/s={result['samples_per_second']:.2f}, "
                f"peak_mem={result['peak_memory_mb']:.1f}MB"
            )

    results_dir = workspace_root() / "outputs" / "diffusion_planner_project" / "results"
    csv_path = results_dir / "inference_benchmark.csv"
    png_path = results_dir / "inference_benchmark.png"
    write_csv(rows, csv_path)
    plot_results(rows, png_path)
    print(f"saved_csv={csv_path}")
    print(f"saved_plot={png_path}")


if __name__ == "__main__":
    main()
