from __future__ import annotations

import argparse
from pathlib import Path


IMPORT_NEEDLE = "import abc\nimport time\n"
IMPORT_REPLACEMENT = "import abc\nimport csv\nimport os\nimport time\n"
PATH_IMPORT_NEEDLE = "from dataclasses import dataclass\n"
PATH_IMPORT_REPLACEMENT = "from dataclasses import dataclass\nfrom pathlib import Path\n"

HELPER_NEEDLE = "@dataclass(frozen=True)\nclass PlannerInitialization:\n"
HELPER = '''def _profile_compute_trajectory_event(current_input, status: str, runtime_s: float | None = None) -> None:
    profile_path = os.environ.get("DP_FRAME_PROFILE_CSV")
    if not profile_path:
        return

    iteration = getattr(current_input, "iteration", None)
    iteration_index = getattr(iteration, "index", "")
    iteration_time_s = getattr(iteration, "time_s", "")
    path = Path(profile_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    has_header = path.exists() and path.stat().st_size > 0
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["iteration_index", "iteration_time_s", "status", "runtime_s"],
        )
        if not has_header:
            writer.writeheader()
        writer.writerow(
            {
                "iteration_index": iteration_index,
                "iteration_time_s": iteration_time_s,
                "status": status,
                "runtime_s": "" if runtime_s is None else f"{runtime_s:.9f}",
            }
        )


@dataclass(frozen=True)
class PlannerInitialization:
'''

START_NEEDLE = "        start_time = time.perf_counter()\n"
START_REPLACEMENT = (
    "        start_time = time.perf_counter()\n"
    '        _profile_compute_trajectory_event(current_input, "start")\n'
)
EXCEPT_NEEDLE = (
    "        except Exception as e:\n"
    "            self._compute_trajectory_runtimes.append(time.perf_counter() - start_time)\n"
    "            raise e\n\n"
    "        self._compute_trajectory_runtimes.append(time.perf_counter() - start_time)\n"
    "        return trajectory\n"
)
EXCEPT_REPLACEMENT = (
    "        except Exception as e:\n"
    "            runtime_s = time.perf_counter() - start_time\n"
    "            self._compute_trajectory_runtimes.append(runtime_s)\n"
    '            _profile_compute_trajectory_event(current_input, "error", runtime_s)\n'
    "            raise e\n\n"
    "        runtime_s = time.perf_counter() - start_time\n"
    "        self._compute_trajectory_runtimes.append(runtime_s)\n"
    '        _profile_compute_trajectory_event(current_input, "end", runtime_s)\n'
    "        return trajectory\n"
)


def patch_abstract_planner(repo_root: Path) -> bool:
    planner_path = repo_root / "nuplan" / "planning" / "simulation" / "planner" / "abstract_planner.py"
    if not planner_path.exists():
        raise FileNotFoundError(f"abstract_planner.py not found: {planner_path}")

    text = planner_path.read_text(encoding="utf-8")
    updated = text
    if "import csv\n" not in updated:
        updated = updated.replace(IMPORT_NEEDLE, IMPORT_REPLACEMENT, 1)
    if "from pathlib import Path\n" not in updated:
        updated = updated.replace(PATH_IMPORT_NEEDLE, PATH_IMPORT_REPLACEMENT, 1)
    updated = updated.replace(
        "@dataclass(frozen=True)\ndef _profile_compute_trajectory_event",
        "def _profile_compute_trajectory_event",
    )
    updated = updated.replace(
        "\n\nclass PlannerInitialization:\n",
        "\n\n@dataclass(frozen=True)\nclass PlannerInitialization:\n",
        1,
    )
    if "def _profile_compute_trajectory_event" not in updated:
        updated = updated.replace(HELPER_NEEDLE, HELPER, 1)
    if '_profile_compute_trajectory_event(current_input, "start")' not in updated:
        updated = updated.replace(START_NEEDLE, START_REPLACEMENT, 1)
    if '_profile_compute_trajectory_event(current_input, "end", runtime_s)' not in updated:
        if EXCEPT_NEEDLE not in updated:
            raise RuntimeError("Could not find compute_trajectory timing block to patch.")
        updated = updated.replace(EXCEPT_NEEDLE, EXCEPT_REPLACEMENT, 1)

    if updated != text:
        planner_path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Patch nuPlan AbstractPlanner frame-level profiling.")
    parser.add_argument("--repo-root", required=True, type=Path)
    args = parser.parse_args()

    changed = patch_abstract_planner(args.repo_root.resolve())
    print(f"frame_profile_override={'patched' if changed else 'already_enabled'}")


if __name__ == "__main__":
    main()
