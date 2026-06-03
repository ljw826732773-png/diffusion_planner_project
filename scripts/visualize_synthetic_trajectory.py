from __future__ import annotations

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


def main() -> None:
    repo = prepare_imports()

    from diffusion_planner.model.diffusion_planner import Diffusion_Planner
    from diffusion_planner.utils.config import Config

    paths = checkpoint_paths(repo)
    cfg = Config(str(paths["args"]), None)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg.device = device

    raw_inputs = build_synthetic_inputs(cfg, device)
    route_lanes = raw_inputs["route_lanes"].detach().cpu()
    neighbor_history = raw_inputs["neighbor_agents_past"].detach().cpu()
    static_objects = raw_inputs["static_objects"].detach().cpu()

    inputs = cfg.observation_normalizer(raw_inputs)
    model = Diffusion_Planner(cfg).to(device).train()
    checkpoint = torch.load(paths["model"], map_location=device)
    model.load_state_dict(strip_module_prefix(checkpoint["ema_state_dict"]), strict=True)

    with torch.no_grad():
        _, decoder_outputs = model(inputs)

    predicted = cfg.state_normalizer.inverse(decoder_outputs["score"][:, :, 1:, :])
    ego_xy = predicted[0, 0, :, :2].detach().cpu()

    results_dir = workspace_root() / "outputs" / "diffusion_planner_project" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    output_path = results_dir / "synthetic_forward_trajectory.png"

    plt.figure(figsize=(9, 6), dpi=150)
    ax = plt.gca()

    for route_id in range(min(route_lanes.shape[1], 12)):
        lane = route_lanes[0, route_id]
        ax.plot(lane[:, 0], lane[:, 1], color="#9aa6b2", linewidth=1.0, alpha=0.55)

    for agent_id in range(min(neighbor_history.shape[1], 14)):
        history = neighbor_history[0, agent_id]
        ax.plot(history[:, 0], history[:, 1], color="#4c78a8", linewidth=0.8, alpha=0.35)
        ax.scatter(history[-1, 0], history[-1, 1], s=10, color="#4c78a8", alpha=0.65)

    ax.scatter(static_objects[0, :, 0], static_objects[0, :, 1], s=30, marker="s", color="#f58518", label="static objects")
    ax.plot(ego_xy[:, 0], ego_xy[:, 1], color="#d62728", linewidth=2.4, label="ego predicted trajectory")
    ax.scatter([0], [0], s=45, color="#2ca02c", label="ego current state")

    ax.set_title("Diffusion-Planner Synthetic Forward Visualization")
    ax.set_xlabel("x / m")
    ax.set_ylabel("y / m")
    ax.grid(True, linewidth=0.4, alpha=0.35)
    ax.axis("equal")
    ax.legend(loc="best")
    plt.tight_layout()
    plt.savefig(output_path)

    print(f"device={device}")
    print(f"saved={output_path}")
    print(f"trajectory_points={ego_xy.shape[0]}")


if __name__ == "__main__":
    main()

