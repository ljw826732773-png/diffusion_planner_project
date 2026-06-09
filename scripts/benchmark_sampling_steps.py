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
    project_root,
    strip_module_prefix,
)


def parse_int_list(value: str) -> list[int]:
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


def project_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return project_root() / path


def patch_sampling_steps(decoder_module, steps: int):
    original = decoder_module.dpm_sampler

    def wrapped(*args, **kwargs):
        kwargs["diffusion_steps"] = steps
        return original(*args, **kwargs)

    decoder_module.dpm_sampler = wrapped
    return original


def run_once(model, cfg, inputs):
    with torch.no_grad():
        _, decoder_outputs = model(inputs)
        return decoder_outputs["prediction"].detach()


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark Diffusion-Planner sampling steps.")
    parser.add_argument("--steps", default="5,10,20,50", help="Comma-separated diffusion steps.")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--iterations", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--device", default="auto", choices=["auto", "cuda", "cpu"])
    parser.add_argument("--output-csv", type=Path, default=Path("results/sampling_steps_ablation.csv"))
    parser.add_argument("--output-png", type=Path, default=Path("results/sampling_steps_ablation.png"))
    args = parser.parse_args()

    repo = prepare_imports()

    import diffusion_planner.model.module.decoder as decoder_module
    from diffusion_planner.model.diffusion_planner import Diffusion_Planner
    from diffusion_planner.utils.config import Config

    paths = checkpoint_paths(repo)
    cfg = Config(str(paths["args"]), None)
    if args.device == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device
    if device == "cuda" and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but torch.cuda.is_available() is false")
    cfg.device = device

    model = Diffusion_Planner(cfg).to(device)
    checkpoint = torch.load(paths["model"], map_location=device)
    model.load_state_dict(strip_module_prefix(checkpoint["ema_state_dict"]), strict=True)
    model.eval()

    raw_inputs = build_synthetic_inputs(cfg, device, batch_size=args.batch_size)
    inputs = cfg.observation_normalizer(raw_inputs)
    sampling_inputs = {
        key: value
        for key, value in inputs.items()
        if key not in {"sampled_trajectories", "diffusion_time"}
    }

    rows = []
    baseline = None
    original_sampler = decoder_module.dpm_sampler
    for steps in parse_int_list(args.steps):
        decoder_module.dpm_sampler = original_sampler
        patch_sampling_steps(decoder_module, steps)

        def fn():
            return run_once(model, cfg, sampling_inputs)

        for _ in range(args.warmup):
            fn()
        if device == "cuda":
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()

        torch.manual_seed(3407)
        prediction = fn()
        if baseline is None:
            baseline = prediction
        drift_m = torch.mean(torch.linalg.norm(prediction[:, 0, :, :2] - baseline[:, 0, :, :2], dim=-1)).item()

        times_ms = [time_once(fn, device) for _ in range(args.iterations)]
        peak_memory_mb = torch.cuda.max_memory_allocated() / (1024 * 1024) if device == "cuda" else 0.0
        row = {
            "steps": steps,
            "device": device,
            "batch_size": args.batch_size,
            "iterations": args.iterations,
            "mean_ms": mean(times_ms),
            "median_ms": median(times_ms),
            "min_ms": min(times_ms),
            "max_ms": max(times_ms),
            "calls_per_second": 1000.0 / mean(times_ms),
            "mean_ego_xy_drift_from_first_steps_m": drift_m,
            "peak_memory_mb": peak_memory_mb,
        }
        rows.append(row)
        print(f"steps={steps}: mean={row['mean_ms']:.2f}ms drift={drift_m:.4f}m")

    decoder_module.dpm_sampler = original_sampler

    csv_path = project_path(args.output_csv)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    png_path = project_path(args.output_png)
    fig, ax = plt.subplots(figsize=(7.5, 4.8), dpi=150)
    ax.plot([row["steps"] for row in rows], [row["mean_ms"] for row in rows], marker="o", color="#4c78a8")
    ax.set_xlabel("diffusion sampling steps")
    ax.set_ylabel("mean latency (ms)")
    ax.set_title("Synthetic Sampling Steps Ablation")
    ax.grid(linewidth=0.4, alpha=0.35)
    plt.tight_layout()
    png_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(png_path)
    print(f"saved_csv={csv_path}")
    print(f"saved_plot={png_path}")


if __name__ == "__main__":
    main()
