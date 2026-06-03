from __future__ import annotations

import torch

from project_utils import build_synthetic_inputs, checkpoint_paths, prepare_imports


def main() -> None:
    repo = prepare_imports()

    from diffusion_planner.model.diffusion_planner import Diffusion_Planner
    from diffusion_planner.utils.config import Config

    paths = checkpoint_paths(repo)
    cfg = Config(str(paths["args"]), None)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg.device = device

    inputs = build_synthetic_inputs(cfg, device)
    inputs = cfg.observation_normalizer(inputs)

    model = Diffusion_Planner(cfg).to(device).train()
    with torch.no_grad():
        encoder_outputs, decoder_outputs = model(inputs)

    print(f"repo={repo}")
    print(f"device={device}")
    print(f"torch={torch.__version__}")
    print(f"cuda_available={torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"cuda_device={torch.cuda.get_device_name(0)}")
    print(f"encoding_shape={tuple(encoder_outputs['encoding'].shape)}")
    print(f"score_shape={tuple(decoder_outputs['score'].shape)}")
    print(f"score_isfinite={torch.isfinite(decoder_outputs['score']).all().item()}")


if __name__ == "__main__":
    main()

