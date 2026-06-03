from __future__ import annotations

import torch

from project_utils import checkpoint_paths, prepare_imports, strip_module_prefix


def main() -> None:
    repo = prepare_imports()

    from diffusion_planner.model.diffusion_planner import Diffusion_Planner
    from diffusion_planner.planner.planner import DiffusionPlanner
    from diffusion_planner.utils.config import Config

    paths = checkpoint_paths(repo)
    cfg = Config(str(paths["args"]), None)
    cfg.device = "cpu"

    model = Diffusion_Planner(cfg)
    checkpoint = torch.load(paths["model"], map_location="cpu")
    state_dict = strip_module_prefix(checkpoint["ema_state_dict"])
    missing, unexpected = model.load_state_dict(state_dict, strict=False)

    print(f"repo={repo}")
    print(f"checkpoint_keys={list(checkpoint.keys())}")
    print(f"loaded_params={len(state_dict)}")
    print(f"missing={len(missing)}")
    print(f"unexpected={len(unexpected)}")
    print("planner_import=ok" if DiffusionPlanner is not None else "planner_import=failed")


if __name__ == "__main__":
    main()

