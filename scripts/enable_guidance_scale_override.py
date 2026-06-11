from __future__ import annotations

import argparse
from pathlib import Path


IMPORT_NEEDLE = "import math\n"
IMPORT_REPLACEMENT = "import math\nimport os\n"
SCALE_NEEDLE = '                            "guidance_scale": 0.5,\n'
SCALE_REPLACEMENT = (
    '                            "guidance_scale": float(os.environ.get("DP_GUIDANCE_SCALE", "0.5")),\n'
)


def patch_decoder(repo_root: Path) -> bool:
    decoder_path = repo_root / "diffusion_planner" / "model" / "module" / "decoder.py"
    if not decoder_path.exists():
        raise FileNotFoundError(f"decoder.py not found: {decoder_path}")

    text = decoder_path.read_text(encoding="utf-8")
    updated = text
    if "import os\n" not in updated:
        updated = updated.replace(IMPORT_NEEDLE, IMPORT_REPLACEMENT, 1)
    if SCALE_REPLACEMENT not in updated:
        if SCALE_NEEDLE not in updated:
            raise RuntimeError(
                "Could not find the hardcoded guidance_scale line. "
                "The upstream decoder may have changed."
            )
        updated = updated.replace(SCALE_NEEDLE, SCALE_REPLACEMENT, 1)

    if updated != text:
        decoder_path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch upstream Diffusion-Planner guidance scale override.")
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()

    changed = patch_decoder(args.repo_root.resolve())
    print(f"guidance_scale_override={'patched' if changed else 'already_enabled'}")


if __name__ == "__main__":
    main()
