#!/usr/bin/env python3
"""Offline structural checks for the public portfolio package.

This lightweight check does not rerun SMINA, GNINA, or RDKit. It verifies
fixed input hashes, raw evidence, preserved outputs, summary tables, figures,
documentation links, the package manifest, and privacy checks.
"""

from __future__ import annotations

import csv
import hashlib
import re
import sys
import tarfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRECTORY_NAMES = {".git", "__pycache__"}


def is_package_file(path: Path) -> bool:
    """Return True only for files that belong to the distributed package."""
    if not path.is_file():
        return False
    relative = path.relative_to(ROOT)
    return not any(part in EXCLUDED_DIRECTORY_NAMES for part in relative.parts)


def require(path: str) -> Path:
    candidate = ROOT / path
    if not candidate.is_file():
        raise AssertionError(f"Missing required file: {path}")
    return candidate


def read_csv(path: str) -> list[dict[str, str]]:
    with require(path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def count_sdf_records(path: str) -> int:
    text = require(path).read_text(encoding="utf-8", errors="replace")
    return sum(1 for line in text.splitlines() if line.strip() == "$$$$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_manifest() -> None:
    manifest = require("MANIFEST.sha256")
    expected: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        digest, relative = line.split("  ", 1)
        expected[relative] = digest

    actual_files = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob("*")
        if is_package_file(path) and path.resolve() != manifest.resolve()
    }
    if set(expected) != actual_files:
        missing = sorted(actual_files - set(expected))
        extra = sorted(set(expected) - actual_files)
        raise AssertionError(f"Manifest file set mismatch; missing={missing}, extra={extra}")

    for relative, digest in expected.items():
        if sha256(ROOT / relative) != digest:
            raise AssertionError(f"Manifest hash mismatch: {relative}")


def verify_reproducibility_data() -> None:
    reference_hashes = {
        "1U72_MTX_crystal_historical.sdf": "63c2d5de73d3097b11776745cd6e8a7939853b620b9058d7ee1c2bbc5ac839a9",
        "1U72.pdb": "3a03a8a1aaadfdc54b0e1e88b537c2c048c04c744c574f36dab6a677f5fa237c",
        "4DFR_MTX_A_crystal_historical.sdf": "33bd1b7e3ec42f988025766fc2392d511a6983937f5361983c6444790e40af24",
        "4DFR.pdb": "57a68d20dc3e7cab4278f4b7006cef0ec0db7e24771bc1c38f4f436668e794e8",
        "MTX_ideal.sdf": "c905eab496dcf8163713016b3cf39969cfacb140f7ec6899fbdddc5e1ed151a9",
    }
    for filename, digest in reference_hashes.items():
        path = require(f"data/reference/{filename}")
        if sha256(path) != digest:
            raise AssertionError(f"Fixed reference hash mismatch: {filename}")

    archive = require("data/raw/robustness/4DFR_robustness_results.tar.gz")
    archive_digest = "a5ab4135fff9b6b1984fa59881e3d4e1d0b412fb309b7194be0fe40c1a1e146f"
    if sha256(archive) != archive_digest:
        raise AssertionError("Robustness raw archive hash mismatch")
    with tarfile.open(archive, "r:gz") as handle:
        names = [member.name for member in handle.getmembers() if member.isfile()]
    if sum(name.endswith(".sdf") for name in names) != 60:
        raise AssertionError("Robustness archive must contain 60 SDF run files")
    if sum("/logs/" in name and name.endswith(".log") for name in names) != 60:
        raise AssertionError("Robustness archive must contain 60 SMINA logs")

    gnina_input = "data/raw/gnina_poc/input"
    gnina_output = "data/raw/gnina_poc/output"
    if count_sdf_records(f"{gnina_input}/smina_poses_original.sdf") != 9:
        raise AssertionError("GNINA original SMINA input must contain 9 poses")
    for pose_number in range(1, 10):
        if count_sdf_records(f"{gnina_input}/poses/pose_{pose_number:02d}.sdf") != 1:
            raise AssertionError(f"GNINA input Pose {pose_number} must contain one record")
        if count_sdf_records(
            f"{gnina_output}/poses/pose_{pose_number:02d}_gnina.sdf"
        ) != 1:
            raise AssertionError(f"GNINA output Pose {pose_number} must contain one record")

    raw_gnina = require(f"{gnina_output}/gnina_rescoring_comparison.csv")
    preserved_gnina = require("results/summary/gnina_rescoring_comparison.csv")
    if raw_gnina.read_bytes() != preserved_gnina.read_bytes():
        raise AssertionError("Preserved GNINA comparison differs from raw evidence copy")


def read_sdf_property(path: str, property_name: str) -> list[float]:
    """Read one numeric property from each SDF record without RDKit."""
    text = require(path).read_text(encoding="utf-8", errors="replace")
    marker = f"> <{property_name}>"
    values: list[float] = []
    for record in text.split("$$$$"):
        lines = record.splitlines()
        for index, line in enumerate(lines):
            if line.strip() == marker:
                if index + 1 >= len(lines):
                    raise AssertionError(f"Missing value for {property_name} in {path}")
                values.append(float(lines[index + 1].strip()))
                break
    return values


def verify_png(path: str) -> None:
    payload = require(path).read_bytes()
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        raise AssertionError(f"Invalid PNG signature: {path}")


def verify_markdown_links() -> None:
    pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
    for markdown_path in ROOT.rglob("*.md"):
        if not is_package_file(markdown_path):
            continue
        text = markdown_path.read_text(encoding="utf-8")
        for target in pattern.findall(text):
            target = target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (markdown_path.parent / target).resolve()
            if not resolved.exists():
                relative = markdown_path.relative_to(ROOT)
                raise AssertionError(f"Broken local link in {relative}: {target}")


def verify_privacy() -> None:
    patterns = {
        "Windows user path": re.compile(r"C:\\Users\\[^\\\s]+", re.I),
        "Linux home path": re.compile(r"/home/[^/\s]+", re.I),
        "WSL user path": re.compile(r"/mnt/c/Users/[^/\s]+", re.I),
        "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    }
    text_suffixes = {
        ".md", ".txt", ".csv", ".py", ".sh", ".pml", ".yml", ".yaml", ".log"
    }
    for path in ROOT.rglob("*"):
        if not is_package_file(path) or path.suffix.lower() not in text_suffixes:
            continue
        if path.resolve() == Path(__file__).resolve():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in patterns.items():
            if pattern.search(text):
                relative = path.relative_to(ROOT)
                raise AssertionError(f"Potential {label} in {relative}")


def verify_results() -> None:
    if count_sdf_records("results/poses/4dfr_mtx_redocked_historical.sdf") != 5:
        raise AssertionError("Historical 4DFR SDF must contain 5 poses")
    if count_sdf_records("results/poses/1u72_mtx_redocked.sdf") != 9:
        raise AssertionError("1U72 SDF must contain 9 poses")

    four_dfr = read_csv("results/summary/4dfr_single_run_rmsd.csv")
    human = read_csv("results/summary/human_1u72_rmsd.csv")
    robustness = read_csv("results/summary/4dfr_robustness_results.csv")
    gnina = read_csv("results/summary/gnina_rescoring_comparison.csv")

    assert len(four_dfr) == 5
    assert len(human) == 9
    assert len(robustness) == 60
    assert len(gnina) == 9

    four_dfr_sdf_affinities = read_sdf_property(
        "results/poses/4dfr_mtx_redocked_historical.sdf", "minimizedAffinity"
    )
    human_sdf_affinities = read_sdf_property(
        "results/poses/1u72_mtx_redocked.sdf", "minimizedAffinity"
    )
    assert len(four_dfr_sdf_affinities) == len(four_dfr)
    assert len(human_sdf_affinities) == len(human)
    for row, sdf_value in zip(four_dfr, four_dfr_sdf_affinities, strict=True):
        assert abs(float(row["smina_affinity_kcal_mol"]) - sdf_value) < 1e-9
    for row, sdf_value in zip(human, human_sdf_affinities, strict=True):
        assert abs(float(row["smina_affinity_kcal_mol"]) - sdf_value) < 1e-9

    best_4dfr = min(four_dfr, key=lambda row: float(row["symmetry_rmsd_A"]))
    assert best_4dfr["pose"] == "3"
    assert abs(float(best_4dfr["symmetry_rmsd_A"]) - 1.516) < 1e-9

    best_human = min(human, key=lambda row: float(row["symmetry_rmsd_A"]))
    assert best_human["pose"] == "1"
    assert abs(float(best_human["symmetry_rmsd_A"]) - 1.092) < 1e-9
    assert sum(row["native_like_at_2A"].lower() == "true" for row in human) == 3
    assert {int(row["candidate_maps"]) for row in four_dfr} == {8}
    assert {int(row["candidate_maps"]) for row in human} == {4}

    assert {int(row["exhaustiveness"]) for row in robustness} == {8, 16, 32}
    assert sum(int(row["top1_success"]) for row in robustness) == 0
    assert sum(int(row["topn_success"]) for row in robustness) == 60

    cnn_top = max(gnina, key=lambda row: float(row["cnnscore"]))
    rmsd_best = min(gnina, key=lambda row: float(row["rmsd"]))
    assert cnn_top["original_pose"] == "2"
    assert rmsd_best["original_pose"] == "2"
    assert int(cnn_top["native_like"]) == 1


def main() -> None:
    required_files = [
        "README.md",
        "CHANGELOG.md",
        "LICENSE.md",
        "AI_ASSISTANCE.md",
        "AI_REPRODUCIBILITY_REVIEW.md",
        "THIRD_PARTY_NOTICES.md",
        ".github/workflows/verify-package.yml",
        ".github/workflows/reproduce-core.yml",
        "docs/METHODS.md",
        "docs/RESULTS.md",
        "docs/REPRODUCIBILITY.md",
        "docs/LIMITATIONS.md",
        "docs/VALIDATION.md",
        "docs/GITHUB_UPLOAD_GUIDE_JP.md",
        "environment/environment_docking.yml",
        "environment/environment_analysis.yml",
        "environment/environment_pymol.yml",
        "environment/environment_gnina_runtime.yml",
        "environment/docking-linux-64-explicit.txt",
        "environment/gnina-runtime-linux-64-explicit.txt",
        "data/README.md",
        "data/reference/SHA256SUMS",
        "data/raw/robustness/4DFR_robustness_results.tar.gz",
        "data/raw/gnina_poc/input/smina_poses_original.sdf",
        "data/raw/gnina_poc/output/gnina_rescoring_comparison.csv",
        "scripts/docking/run_4dfr_redocking.sh",
        "scripts/docking/run_human_1u72_redocking.sh",
        "scripts/docking/run_4dfr_robustness.sh",
        "scripts/docking/run_gnina_rescoring.sh",
        "scripts/analysis/calculate_symmetry_rmsd.py",
        "scripts/generate_manifest.py",
        "scripts/tests/test_scientific_regression.py",
        "scripts/tests/test_source_syntax.py",
        "scripts/visualization/plot_single_run_results.py",
    ]
    for required_file in required_files:
        require(required_file)

    required_pngs = [
        "results/figures/4dfr/4dfr_rmsd_by_pose.png",
        "results/figures/human_1u72/human_1u72_rmsd_by_pose.png",
        "results/figures/human_1u72/human_vs_ecoli_top1_comparison.png",
        "results/figures/robustness/success_rate_by_exhaustiveness.png",
        "results/figures/gnina/cnnscore_vs_rmsd.png",
        "results/figures/gnina/rank_comparison.png",
    ]
    for png in required_pngs:
        verify_png(png)

    verify_results()
    verify_reproducibility_data()
    verify_markdown_links()
    verify_privacy()
    verify_manifest()

    print("Portfolio verification passed")
    print(f"- Core public-package files: {len(required_files)} present")
    print("- Required files and PNG signatures: OK")
    print("- SDF record counts: 4DFR=5, 1U72=9")
    print("- Summary CSV invariants and SDF affinity consistency: OK")
    print("- Fixed reference hashes and raw robustness/GNINA evidence: OK")
    print("- Markdown local links: OK")
    print("- MANIFEST.sha256 file set and hashes: OK")
    print("- Common secret and personal-path patterns: not found")
    print("Note: docking and RDKit calculations were not rerun by this verifier")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f"VERIFY FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
