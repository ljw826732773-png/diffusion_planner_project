# NuBoard Usage

This project keeps nuPlan simulation artifacts on `D:\nuplan-data\exp` and does not upload raw `.msgpack.xz`, `.nuboard`, metric parquet, or database files to GitHub.

## Existing local run

The verified mini evaluation produced this local NuBoard file:

```text
D:\nuplan-data\exp\exp\simulation\closed_loop_nonreactive_agents\dp\mini5\model\nuboard_1780564082.nuboard
```

It points to the local metric and simulation folders under the same run directory.

## Start NuBoard

From the workspace root:

```powershell
$env:NUPLAN_DEVKIT_ROOT=".\work\nuplan-devkit"
$env:NUPLAN_DATA_ROOT="D:\nuplan-data\dataset"
$env:NUPLAN_MAPS_ROOT="D:\nuplan-data\dataset\maps"
$env:NUPLAN_EXP_ROOT="D:\nuplan-data\exp"
$NuBoard = Get-ChildItem "D:\nuplan-data\exp\exp\simulation\closed_loop_nonreactive_agents\dp\mini5\model" `
  -Filter *.nuboard |
  Select-Object -First 1 -ExpandProperty FullName

conda run -n diffusion_planner python .\work\nuplan-devkit\nuplan\planning\script\run_nuboard.py `
  simulation_path="$NuBoard" `
  port_number=4554
```

Then open:

```text
http://localhost:4554
```

## What to inspect

- Overview tab: compare scenario scores and runner status.
- Histogram tab: inspect low-score metric distributions such as comfort and speed-limit compliance.
- Scenario tab: replay ego motion and planner trajectory in the map context.
- Configuration tab: confirm planner name, scenario filter, and output folders.

## Notes

- NuBoard is an interactive Bokeh server, so it is not committed as a static GitHub artifact.
- The static trajectory plot in `results/nuplan_low_score_trajectory.png` is a lightweight alternative for README display.
- If NuBoard cannot find metrics, check that the `.nuboard` file still points to the original local run folder.
