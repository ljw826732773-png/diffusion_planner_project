from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict

import torch


def workspace_root() -> Path:
    current_file = Path(__file__).resolve()
    for candidate in current_file.parents:
        if (candidate / "work" / "Diffusion-Planner").exists():
            default_root = candidate
            break
    else:
        for candidate in current_file.parents:
            if (candidate / "README.md").exists() and (candidate / "scripts").exists():
                default_root = candidate
                break
        else:
            default_root = current_file.parents[1]
    return Path(os.environ.get("DP_WORKSPACE_ROOT", default_root)).resolve()


def diffusion_repo() -> Path:
    default_repo = workspace_root() / "work" / "Diffusion-Planner"
    return Path(os.environ.get("DP_REPO_ROOT", default_repo)).resolve()


def nuplan_repo() -> Path:
    default_repo = workspace_root() / "work" / "nuplan-devkit"
    return Path(os.environ.get("NUPLAN_DEVKIT_ROOT", default_repo)).resolve()


def prepare_imports() -> Path:
    repo = diffusion_repo()
    devkit = nuplan_repo()
    for path in (str(repo), str(devkit)):
        if path not in sys.path:
            sys.path.insert(0, path)
    os.environ.setdefault("NUPLAN_DEVKIT_ROOT", str(devkit))
    os.chdir(repo)
    return repo


def checkpoint_paths(repo: Path) -> Dict[str, Path]:
    ckpt_dir = repo / "checkpoints"
    return {
        "args": ckpt_dir / "args.json",
        "model": ckpt_dir / "model.pth",
    }


def build_synthetic_inputs(cfg, device: str, batch_size: int = 1) -> Dict[str, torch.Tensor]:
    torch.manual_seed(3407)

    time_index = torch.arange(cfg.time_len, device=device, dtype=torch.float32)
    future_index = torch.arange(cfg.future_len + 1, device=device, dtype=torch.float32)
    lane_x = torch.arange(cfg.lane_len, device=device, dtype=torch.float32) * 2.0

    neighbor_agents_past = torch.zeros(
        batch_size, cfg.agent_num, cfg.time_len, cfg.agent_state_dim, device=device
    )
    for agent_id in range(cfg.agent_num):
        y_offset = (agent_id % 8 - 3.5) * 2.4
        x_offset = -18.0 + agent_id * 1.3
        neighbor_agents_past[:, agent_id, :, 0] = x_offset + time_index * 0.8
        neighbor_agents_past[:, agent_id, :, 1] = y_offset
        neighbor_agents_past[:, agent_id, :, 2] = 1.0
        neighbor_agents_past[:, agent_id, :, 3] = 0.0
        neighbor_agents_past[:, agent_id, :, 4] = 0.8
        neighbor_agents_past[:, agent_id, :, 5] = 0.0
        neighbor_agents_past[:, agent_id, :, 6] = 4.6
        neighbor_agents_past[:, agent_id, :, 7] = 1.9
        neighbor_agents_past[:, agent_id, :, 8] = 1.0

    lanes = torch.zeros(batch_size, cfg.lane_num, cfg.lane_len, cfg.lane_state_dim, device=device)
    for lane_id in range(cfg.lane_num):
        y_offset = (lane_id % 9 - 4) * 3.5
        curve = torch.sin(lane_x / 16.0 + lane_id * 0.2) * 0.4
        lanes[:, lane_id, :, 0] = lane_x
        lanes[:, lane_id, :, 1] = y_offset + curve
        lanes[:, lane_id, :, 2] = 2.0
        lanes[:, lane_id, :, 3] = 0.0
        lanes[:, lane_id, :, 5] = 1.75
        lanes[:, lane_id, :, 7] = -1.75
        lanes[:, lane_id, :, 8] = 1.0

    route_lanes = torch.zeros(
        batch_size, cfg.route_num, cfg.route_len, cfg.route_state_dim, device=device
    )
    route_x = torch.arange(cfg.route_len, device=device, dtype=torch.float32) * 2.0
    for route_id in range(cfg.route_num):
        y_offset = (route_id - cfg.route_num / 2) * 0.15
        route_lanes[:, route_id, :, 0] = route_x
        route_lanes[:, route_id, :, 1] = y_offset + torch.sin(route_x / 18.0) * 0.25
        route_lanes[:, route_id, :, 2] = 2.0
        route_lanes[:, route_id, :, 3] = 0.0
        route_lanes[:, route_id, :, 5] = 1.75
        route_lanes[:, route_id, :, 7] = -1.75
        route_lanes[:, route_id, :, 8] = 1.0

    static_objects = torch.zeros(
        batch_size, cfg.static_objects_num, cfg.static_objects_state_dim, device=device
    )
    for object_id in range(cfg.static_objects_num):
        static_objects[:, object_id, 0] = 8.0 + object_id * 7.0
        static_objects[:, object_id, 1] = (-1) ** object_id * 5.5
        static_objects[:, object_id, 2] = 1.0
        static_objects[:, object_id, 4] = 4.0
        static_objects[:, object_id, 5] = 2.0
        static_objects[:, object_id, 6 + object_id % 4] = 1.0

    predicted_agents = 1 + cfg.predicted_neighbor_num
    sampled_trajectories = torch.zeros(
        batch_size, predicted_agents, cfg.future_len + 1, 4, device=device
    )
    sampled_trajectories[:, :, :, 0] = future_index * 0.5
    sampled_trajectories[:, :, :, 2] = 1.0
    sampled_trajectories[:, 1:, :, 1] = torch.linspace(
        -6.0, 6.0, cfg.predicted_neighbor_num, device=device
    )[None, :, None]

    return {
        "ego_current_state": torch.tensor(
            [[0.0, 0.0, 1.0, 0.0, 0.8, 0.0, 4.6, 1.9, 0.0, 0.0]],
            device=device,
        ).repeat(batch_size, 1),
        "neighbor_agents_past": neighbor_agents_past,
        "lanes": lanes,
        "lanes_speed_limit": torch.ones(batch_size, cfg.lane_num, 1, device=device) * 10.0,
        "lanes_has_speed_limit": torch.ones(
            batch_size, cfg.lane_num, 1, dtype=torch.bool, device=device
        ),
        "route_lanes": route_lanes,
        "route_lanes_speed_limit": torch.ones(batch_size, cfg.route_num, 1, device=device) * 10.0,
        "route_lanes_has_speed_limit": torch.ones(
            batch_size, cfg.route_num, 1, dtype=torch.bool, device=device
        ),
        "static_objects": static_objects,
        "sampled_trajectories": sampled_trajectories,
        "diffusion_time": torch.full((batch_size,), 0.5, device=device),
    }


def strip_module_prefix(state_dict):
    return {k[len("module."):]: v for k, v in state_dict.items() if k.startswith("module.")}
