#!/usr/bin/env bash
set -euo pipefail

# Reproducible teaching workflow for human DHFR (1U72)–methotrexate redocking.
# Usage:
#   conda activate docking
#   bash scripts/docking/run_human_1u72_redocking.sh [project_directory]
# Optional environment variables:
#   SEED=20260719 CPU=4 EXHAUSTIVENESS=16 NUM_MODES=9 bash ...

ROOT="${1:-$PWD/work/human_1u72}"
SEED="${SEED:-20260719}"
CPU="${CPU:-$(nproc)}"
EXHAUSTIVENESS="${EXHAUSTIVENESS:-16}"
NUM_MODES="${NUM_MODES:-9}"

for cmd in wget awk grep smina obabel sha256sum; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

mkdir -p "$ROOT"/{raw,receptor,ligand,results,metadata}

PDB_URL="https://files.rcsb.org/download/1U72.pdb"
MTX_IDEAL_URL="https://files.rcsb.org/ligands/download/MTX_ideal.sdf"
MTX_INSTANCE_URL="https://models.rcsb.org/v1/1u72/ligand?auth_seq_id=188&encoding=sdf&filename=1u72_C_MTX.sdf&label_asym_id=C"

wget -q --show-progress -O "$ROOT/raw/1U72.pdb" "$PDB_URL"
wget -q --show-progress -O "$ROOT/ligand/MTX_ideal.sdf" "$MTX_IDEAL_URL"
wget -q --show-progress -O "$ROOT/ligand/1U72_MTX_crystal.sdf" "$MTX_INSTANCE_URL"

# Keep human DHFR chain A and the NADPH cofactor (PDB residue name NDP).
# MTX and crystallographic waters are excluded from the receptor.
awk '
  /^ATOM/ { print; next }
  /^HETATM/ && substr($0,18,3)=="NDP" { print }
  END { print "END" }
' "$ROOT/raw/1U72.pdb" > "$ROOT/receptor/1U72_hDHFR_NADPH.pdb"

obabel "$ROOT/ligand/MTX_ideal.sdf" \
  -O "$ROOT/ligand/MTX_pH7_4.sdf" \
  -p 7.4 --gen3d

rm -f "$ROOT/results/1U72_MTX_redocked.sdf" "$ROOT/results/1U72_MTX_redocking.log"

smina \
  --receptor "$ROOT/receptor/1U72_hDHFR_NADPH.pdb" \
  --ligand "$ROOT/ligand/MTX_pH7_4.sdf" \
  --autobox_ligand "$ROOT/ligand/1U72_MTX_crystal.sdf" \
  --autobox_add 4 \
  --exhaustiveness "$EXHAUSTIVENESS" \
  --num_modes "$NUM_MODES" \
  --seed "$SEED" \
  --cpu "$CPU" \
  --out "$ROOT/results/1U72_MTX_redocked.sdf" \
  --log "$ROOT/results/1U72_MTX_redocking.log"

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
} > "$ROOT/metadata/versions_and_parameters.txt"

sha256sum \
  "$ROOT/raw/1U72.pdb" \
  "$ROOT/ligand/MTX_ideal.sdf" \
  "$ROOT/ligand/1U72_MTX_crystal.sdf" \
  > "$ROOT/metadata/input_sha256.txt"

POSES=$(grep -c '^\$\$\$\$' "$ROOT/results/1U72_MTX_redocked.sdf" || true)
echo "Completed. Output poses: $POSES"
echo "Results: $ROOT/results"
