#!/usr/bin/env bash

set -u
set -o pipefail

GNINA_BIN="${GNINA_BIN:-gnina}"
RECEPTOR="input/4DFR_chainA_raw.pdb"
POSE_DIRECTORY="input/poses"

OUTPUT_DIRECTORY="output/poses"
LOG_DIRECTORY="output/logs"
SUMMARY_FILE="output/gnina_run_summary.csv"

CPU_THREADS="${CPU_THREADS:-6}"

mkdir -p \
  "$OUTPUT_DIRECTORY" \
  "$LOG_DIRECTORY" \
  "output/metadata"

if [[ ! -f "$RECEPTOR" ]]; then
    echo "ERROR: receptorがありません: $RECEPTOR" >&2
    exit 1
fi

if ! command -v "$GNINA_BIN" >/dev/null 2>&1; then
    echo "ERROR: gninaが見つかりません" >&2
    exit 1
fi

for required_command in date sha256sum; do
    if ! command -v "$required_command" >/dev/null 2>&1; then
        echo "ERROR: required command not found: $required_command" >&2
        exit 1
    fi
done

shopt -s nullglob
pose_files=("$POSE_DIRECTORY"/pose_*.sdf)
if (( ${#pose_files[@]} == 0 )); then
    echo "ERROR: input poseがありません: $POSE_DIRECTORY" >&2
    exit 1
fi

{
    echo "Run date (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "Operating system: $(uname -a)"
    echo "CPU threads: $CPU_THREADS"
    echo
    echo "GNINA:"
    "$GNINA_BIN" --version 2>&1 || true
    echo
    echo "GNINA binary SHA-256:"
    sha256sum "$(command -v "$GNINA_BIN")" 2>&1 || true
    echo
    echo "Input SHA-256:"
    sha256sum "$RECEPTOR" "$POSE_DIRECTORY"/pose_*.sdf
} > "output/metadata/versions_parameters_and_inputs.txt"

echo \
"pose,elapsed_seconds,status,input_file,output_file" \
> "$SUMMARY_FILE"

for pose_file in "${pose_files[@]}"; do
    filename=$(basename "$pose_file")
    pose_id="${filename#pose_}"
    pose_id="${pose_id%.sdf}"

    output_file="${OUTPUT_DIRECTORY}/pose_${pose_id}_gnina.sdf"
    log_file="${LOG_DIRECTORY}/pose_${pose_id}.log"
    console_file="${LOG_DIRECTORY}/pose_${pose_id}_console.log"

    echo
    echo "=========================================="
    echo "Rescoring Pose ${pose_id}"
    echo "=========================================="

    start_time=$(date +%s)

    if "$GNINA_BIN" \
        --receptor "$RECEPTOR" \
        --ligand "$pose_file" \
        --score_only \
        --cnn_scoring rescore \
        --no_gpu \
        --cpu "$CPU_THREADS" \
        --out "$output_file" \
        --log "$log_file" \
        > "$console_file" 2>&1
    then
        status="success"
    else
        status="failed"
    fi

    end_time=$(date +%s)
    elapsed=$((end_time - start_time))

    echo \
"${pose_id},${elapsed},${status},${pose_file},${output_file}" \
    >> "$SUMMARY_FILE"

    echo "status=${status}"
    echo "elapsed=${elapsed}s"
done

echo
echo "GNINA rescoring completed"
echo "Summary: $SUMMARY_FILE"
