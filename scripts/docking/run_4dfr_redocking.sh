#!/usr/bin/env bash
set -euo pipefail

# Reproducible teaching workflow for 4DFR–methotrexate redocking.
# Usage:
#   conda activate docking
#   bash run_docking.sh [project_directory]
# Optional environment variables:
#   SEED=20260718 CPU=4 EXHAUSTIVENESS=8 NUM_MODES=5 bash run_docking.sh

ROOT="${1:-$PWD/work/4dfr}"
SEED="${SEED:-20260718}"
CPU="${CPU:-$(nproc)}"
EXHAUSTIVENESS="${EXHAUSTIVENESS:-8}"
NUM_MODES="${NUM_MODES:-5}"

for cmd in wget awk grep smina obabel sha256sum; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

mkdir -p "$ROOT"/{raw,receptor,ligand,results,metadata}

PDB_URL="https://files.rcsb.org/download/4DFR.pdb"
MTX_IDEAL_URL="https://files.rcsb.org/ligands/download/MTX_ideal.sdf"
# Experimental MTX coordinates corresponding to author chain A in 4DFR.
MTX_INSTANCE_URL="https://models.rcsb.org/v1/4dfr/ligand?auth_seq_id=161&encoding=sdf&filename=4dfr_D_MTX.sdf&label_asym_id=D"

wget -q --show-progress -O "$ROOT/raw/4DFR.pdb" "$PDB_URL"
wget -q --show-progress -O "$ROOT/ligand/MTX_ideal.sdf" "$MTX_IDEAL_URL"
wget -q --show-progress -O "$ROOT/ligand/4DFR_MTX_A_crystal.sdf" "$MTX_INSTANCE_URL"

# Extract protein chain A exactly as used in the exercise.
awk '/^ATOM/ && substr($0,22,1)=="A" {print} END {print "END"}' \
  "$ROOT/raw/4DFR.pdb" > "$ROOT/receptor/4DFR_chainA_raw.pdb"

# Optional PDB copy of the crystallographic ligand for inspection in PyMOL.
awk '/^HETATM/ && substr($0,18,3)=="MTX" && substr($0,22,1)=="A" {print} END {print "END"}' \
  "$ROOT/raw/4DFR.pdb" > "$ROOT/ligand/4DFR_MTX_A_raw.pdb"

# Generate a 3D input ligand with a heuristic pH 7.4 protonation treatment.
# For a production study, protonation/tautomer states should be curated separately.
obabel "$ROOT/ligand/MTX_ideal.sdf" \
  -O "$ROOT/ligand/MTX_pH7_4.sdf" \
  -p 7.4 --gen3d

rm -f "$ROOT/results/MTX_redocked.sdf" "$ROOT/results/MTX_redocking.log"

COMMON_ARGS=(
  -l "$ROOT/ligand/MTX_pH7_4.sdf"
  --autobox_ligand "$ROOT/ligand/4DFR_MTX_A_crystal.sdf"
  --autobox_add 5
  --exhaustiveness "$EXHAUSTIVENESS"
  --num_modes "$NUM_MODES"
  --seed "$SEED"
  --cpu "$CPU"
  -o "$ROOT/results/MTX_redocked.sdf"
  --log "$ROOT/results/MTX_redocking.log"
)

# The conda-forge build used in the exercise accepted a PDB receptor directly.
# If another build requires PDBQT, the fallback below creates a rigid PDBQT draft.
if ! smina -r "$ROOT/receptor/4DFR_chainA_raw.pdb" "${COMMON_ARGS[@]}"; then
  echo "Direct PDB receptor was rejected; trying an Open Babel rigid PDBQT fallback." >&2
  rm -f "$ROOT/results/MTX_redocked.sdf" "$ROOT/results/MTX_redocking.log"
  obabel "$ROOT/receptor/4DFR_chainA_raw.pdb" \
    -O "$ROOT/receptor/4DFR_chainA_obabel.pdbqt" \
    -xr -p 7.4
  smina -r "$ROOT/receptor/4DFR_chainA_obabel.pdbqt" "${COMMON_ARGS[@]}"
fi

{
  echo "Run date (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "Seed: $SEED"
  echo "CPU: $CPU"
  echo "Exhaustiveness: $EXHAUSTIVENESS"
  echo "Requested modes: $NUM_MODES"
  echo
  echo "smina:"
  smina --version 2>&1 || true
  echo
  echo "Open Babel:"
  obabel -V 2>&1 || true
  echo
  echo "Conda environment:"
  conda info --envs 2>&1 || true
} > "$ROOT/metadata/versions_and_parameters.txt"

sha256sum \
  "$ROOT/raw/4DFR.pdb" \
  "$ROOT/ligand/MTX_ideal.sdf" \
  "$ROOT/ligand/4DFR_MTX_A_crystal.sdf" \
  > "$ROOT/metadata/input_sha256.txt"

POSES=$(grep -c '^\$\$\$\$' "$ROOT/results/MTX_redocked.sdf" || true)
echo "Completed. Output poses: $POSES"
echo "Results: $ROOT/results"
echo "Metadata: $ROOT/metadata"
