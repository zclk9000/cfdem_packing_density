#!/bin/bash
set -euo pipefail

# Define case path (absolute)
casePath="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"

echo "Cleaning case at: $casePath"

# Try to use OpenFOAM CleanFunctions if available (cleans CFD time dirs etc.)
if [[ -n "${WM_PROJECT_DIR:-}" && -f "$WM_PROJECT_DIR/bin/tools/CleanFunctions" ]]; then
  # shellcheck disable=SC1090
  source "$WM_PROJECT_DIR/bin/tools/CleanFunctions"
  if [[ -d "$casePath/CFD" ]]; then
    pushd "$casePath/CFD" >/dev/null
    cleanCase || true
    popd >/dev/null
  fi
else
  echo "CleanFunctions not found. Proceeding with manual cleanup."
fi

# ---------------- CFD cleanup ----------------
# Remove reconstructed/working 0, but keep 0.org as template
rm -rf "$casePath/CFD/0" 2>/dev/null || true

# Remove processor directories (from parallel runs)
rm -rf "$casePath/CFD/processor"* 2>/dev/null || true

# Remove mesh (polyMesh) so mesh will be rebuilt by Allrun.sh if needed
rm -rf "$casePath/CFD/constant/polyMesh" 2>/dev/null || true

# Remove time directories (numeric names) at case root, excluding 0.org
if [[ -d "$casePath/CFD" ]]; then
  find "$casePath/CFD" -maxdepth 1 -type d \
    -regex '.*/[0-9]+\(\.[0-9]*\)?' \
    -not -name '0.org' -exec rm -rf {} + 2>/dev/null || true
fi

# Remove CFD post-processing and VTK exports
rm -rf "$casePath/CFD/postProcessing" 2>/dev/null || true
rm -rf "$casePath/CFD/VTK" 2>/dev/null || true
rm -rf "$casePath/CFD/clockData" 2>/dev/null || true

# Remove CFD logs
rm -f "$casePath/CFD"/log* "$casePath/CFD"/*.log 2>/dev/null || true

# ---------------- DEM cleanup ----------------
# Remove DEM logs
rm -f "$casePath/DEM/log.liggghts" 2>/dev/null || true
rm -f "$casePath/DEM/post/thermo.txt" 2>/dev/null || true

# Remove DEM dumps, VTK, STL and other post files
rm -f "$casePath/DEM/post/"*.vtk 2>/dev/null || true
rm -f "$casePath/DEM/post/"*.stl 2>/dev/null || true
rm -f "$casePath/DEM/post/dump"* 2>/dev/null || true
rm -f "$casePath/DEM/post/liggghts_run"* 2>/dev/null || true

# Remove DEM restart files (both LIGGGHTS init and CFDEM write)
rm -f "$casePath/DEM/post/restart/"* 2>/dev/null || true

# Ensure required directories exist after cleanup (to avoid run-time errors)
mkdir -p "$casePath/DEM/post/restart"
touch "$casePath/DEM/post/.gitignore"

# ---------------- Root logs cleanup ----------------
rm -f "$casePath"/log* "$casePath"/*.log 2>/dev/null || true

echo "Cleanup finished."
