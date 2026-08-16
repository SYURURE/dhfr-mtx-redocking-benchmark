#!/usr/bin/env bash
set -euo pipefail

# Run the 4DFR robustness matrix used in the exercise.
# Usage:
#   bash scripts/docking/run_4dfr_robustness.sh [prepared_4dfr_directory]
#
# The default directory is work/4dfr, as created by run_4dfr_redocking.sh.
# For a small smoke test, override the ranges, for example:
#   SEED_START=1 SEED_END=2 EXHAUSTIVENESS_VALUES="8" bash ...

PROJECT_DIR="${1:-$PWD/work/4dfr}"
RECEPTOR="$PROJECT_DIR/receptor/4DFR_chainA_raw.pdb"
LIGAND="$PROJECT_DIR/ligand/MTX_pH7_4.sdf"
CRYSTAL="$PROJECT_DIR/ligand/4DFR_MTX_A_crystal.sdf"

OUTPUT_ROOT="${OUTPUT_ROOT:-$PROJECT_DIR/robustness_4DFR}"
RUN_DIR="$OUTPUT_ROOT/runs"
LOG_DIR="$OUTPUT_ROOT/logs"
SUMMARY="$OUTPUT_ROOT/aws_run_summary.csv"

SEED_START="${SEED_START:-1}"
SEED_END="${SEED_END:-20}"
read -r -a EXHAUSTIVENESS_ARRAY <<< "${EXHAUSTIVENESS_VALUES:-8 16 32}"
NUM_MODES="${NUM_MODES:-9}"
AUTOBOX_ADD="${AUTOBOX_ADD:-4}"
CPU="${CPU:-$(nproc)}"

for cmd in smina seq date; do
  command -v "$cmd" >/dev/null 2>&1 || {
    echo "ERROR: required command not found: $cmd" >&2
    exit 1
  }
done

for file in "$RECEPTOR" "$LIGAND" "$CRYSTAL"; do
  if [[ ! -f "$file" ]]; then
    echo "ERROR: required input file is missing: $file" >&2
    exit 1
  fi
done

if (( SEED_START > SEED_END )); then
  echo "ERROR: SEED_START must be less than or equal to SEED_END" >&2
  exit 1
fi

mkdir -p "$RUN_DIR" "$LOG_DIR"
echo "seed,exhaustiveness,elapsed_seconds,status,output_file,log_file" > "$SUMMARY"

total_runs=$(( (SEED_END - SEED_START + 1) * ${#EXHAUSTIVENESS_ARRAY[@]} ))
current_run=0

for exhaustiveness in "${EXHAUSTIVENESS_ARRAY[@]}"; do
  for seed in $(seq "$SEED_START" "$SEED_END"); do
    current_run=$((current_run + 1))
    tag="exh${exhaustiveness}_seed${seed}"
    output="$RUN_DIR/${tag}.sdf"
    log="$LOG_DIR/${tag}.log"

    echo "Run ${current_run}/${total_runs}: seed=${seed}, exhaustiveness=${exhaustiveness}"
    start_time=$(date +%s)

    if smina \
      --receptor "$RECEPTOR" \
      --ligand "$LIGAND" \
      --autobox_ligand "$CRYSTAL" \
      --autobox_add "$AUTOBOX_ADD" \
      --exhaustiveness "$exhaustiveness" \
      --num_modes "$NUM_MODES" \
      --seed "$seed" \
      --cpu "$CPU" \
      --out "$output" \
      --log "$log"
    then
      status="success"
    else
      status="failed"
    fi

    end_time=$(date +%s)
    elapsed=$((end_time - start_time))
    echo "${seed},${exhaustiveness},${elapsed},${status},${output},${log}" >> "$SUMMARY"
    echo "Finished ${tag}: status=${status}, elapsed=${elapsed}s"
  done
done

echo "All robustness runs completed"
echo "Summary: $SUMMARY"
