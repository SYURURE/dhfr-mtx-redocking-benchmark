#!/usr/bin/env python3
"""Recalculate preserved scientific summaries from fixed inputs and raw evidence."""

from __future__ import annotations

import csv
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_python(script: Path, arguments: list[str], cwd: Path | None = None) -> None:
    completed = subprocess.run(
        [sys.executable, str(script), *arguments],
        cwd=cwd or ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"Command failed: {script}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def verify_rmsd(
    temporary_directory: Path,
    crystal: str,
    docked: str,
    expected_summary: str,
) -> None:
    output = temporary_directory / (Path(expected_summary).stem + "_recomputed.csv")
    run_python(
        ROOT / "scripts/analysis/calculate_symmetry_rmsd.py",
        [
            "--crystal",
            str(ROOT / crystal),
            "--docked",
            str(ROOT / docked),
            "--csv",
            str(output),
        ],
    )

    actual_rows = read_csv(output)
    expected_rows = read_csv(ROOT / expected_summary)
    if len(actual_rows) != len(expected_rows):
        raise AssertionError(f"RMSD row count mismatch: {expected_summary}")

    for actual, expected in zip(actual_rows, expected_rows, strict=True):
        checks = {
            "pose": expected["pose"],
            "symmetry_rmsd_A": expected["symmetry_rmsd_A"],
            "matched_atoms": expected["matched_heavy_atoms"],
            "candidate_maps": expected["candidate_maps"],
            "full_heavy_atom_match": expected["full_heavy_atom_match"].title(),
        }
        for key, expected_value in checks.items():
            if actual[key] != expected_value:
                raise AssertionError(
                    f"RMSD mismatch in {expected_summary}, pose {expected['pose']}, "
                    f"{key}: expected {expected_value}, got {actual[key]}"
                )


def safe_extract(archive: Path, destination: Path) -> None:
    destination_resolved = destination.resolve()
    with tarfile.open(archive, "r:gz") as handle:
        members = handle.getmembers()
        for member in members:
            target = (destination / member.name).resolve()
            if destination_resolved not in target.parents and target != destination_resolved:
                raise AssertionError(f"Unsafe archive member: {member.name}")
        handle.extractall(destination)


def verify_robustness(temporary_directory: Path) -> None:
    replay = temporary_directory / "robustness_replay"
    replay.mkdir()
    safe_extract(
        ROOT / "data/raw/robustness/4DFR_robustness_results.tar.gz",
        replay,
    )
    source = replay / "robustness_4DFR"
    output = replay / "robustness_recomputed.csv"
    run_python(
        ROOT / "scripts/analysis/analyze_robustness.py",
        [
            "--crystal",
            str(ROOT / "data/reference/4DFR_MTX_A_crystal_historical.sdf"),
            "--run-dir",
            str(source / "runs"),
            "--run-summary",
            str(source / "aws_run_summary.csv"),
            "--output",
            str(output),
        ],
    )
    expected = ROOT / "results/summary/4dfr_robustness_results.csv"
    if output.read_bytes() != expected.read_bytes():
        raise AssertionError("Raw 60-run archive did not reproduce robustness CSV")


def verify_gnina_analysis(temporary_directory: Path) -> None:
    replay = temporary_directory / "gnina_poc_replay"
    shutil.copytree(ROOT / "data/raw/gnina_poc", replay)
    run_python(
        ROOT / "scripts/analysis/analyze_gnina_rescoring.py",
        [],
        cwd=replay,
    )

    comparisons = {
        "gnina_rescoring_comparison.csv": "gnina_rescoring_comparison.csv",
        "ranked_by_cnnscore.csv": "gnina_ranked_by_cnnscore.csv",
        "ranked_by_cnnaffinity.csv": "gnina_ranked_by_cnnaffinity.csv",
    }
    for generated_name, preserved_name in comparisons.items():
        generated = replay / "output" / generated_name
        preserved = ROOT / "results/summary" / preserved_name
        if generated.read_bytes() != preserved.read_bytes():
            raise AssertionError(f"GNINA analysis mismatch: {generated_name}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="dhfr-regression-") as directory:
        temporary_directory = Path(directory)
        verify_rmsd(
            temporary_directory,
            "data/reference/4DFR_MTX_A_crystal_historical.sdf",
            "results/poses/4dfr_mtx_redocked_historical.sdf",
            "results/summary/4dfr_single_run_rmsd.csv",
        )
        verify_rmsd(
            temporary_directory,
            "data/reference/1U72_MTX_crystal_historical.sdf",
            "results/poses/1u72_mtx_redocked.sdf",
            "results/summary/human_1u72_rmsd.csv",
        )
        verify_robustness(temporary_directory)
        verify_gnina_analysis(temporary_directory)

    print("Scientific regression passed")
    print("- 4DFR historical RMSD: reproduced")
    print("- Human 1U72 symmetry-aware RMSD: reproduced")
    print("- Robustness 60-run raw archive -> summary CSV: exact match")
    print("- GNINA raw input/output -> three summary CSVs: exact match")


if __name__ == "__main__":
    main()
