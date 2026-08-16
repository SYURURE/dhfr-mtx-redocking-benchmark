#!/usr/bin/env python3
"""Offline structural checks for the public portfolio package.

This does not rerun SMINA, GNINA, or RDKit. It verifies that the preserved
outputs, summary tables, figures, documentation links, and public-package
privacy checks are internally consistent.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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
        if not path.is_file() or path.suffix.lower() not in text_suffixes:
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
    assert abs(float(best_human["symmetry_rmsd_A"]) - 1.365) < 1e-9
    assert sum(row["native_like_at_2A"].lower() == "true" for row in human) == 3

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
        "LICENSE.md",
        "AI_ASSISTANCE.md",
        "THIRD_PARTY_NOTICES.md",
        ".github/workflows/verify-package.yml",
        "docs/METHODS.md",
        "docs/RESULTS.md",
        "docs/REPRODUCIBILITY.md",
        "docs/LIMITATIONS.md",
        "docs/GITHUB_UPLOAD_GUIDE_JP.md",
        "environment/environment_docking.yml",
        "environment/environment_analysis.yml",
        "environment/environment_pymol.yml",
        "scripts/docking/run_4dfr_redocking.sh",
        "scripts/docking/run_human_1u72_redocking.sh",
        "scripts/docking/run_4dfr_robustness.sh",
        "scripts/docking/run_gnina_rescoring.sh",
        "scripts/analysis/calculate_symmetry_rmsd.py",
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
    verify_markdown_links()
    verify_privacy()

    print("Portfolio verification passed")
    print(f"- Core public-package files: {len(required_files)} present")
    print("- Required files and PNG signatures: OK")
    print("- SDF record counts: 4DFR=5, 1U72=9")
    print("- Summary CSV invariants and SDF affinity consistency: OK")
    print("- Markdown local links: OK")
    print("- Common secret and personal-path patterns: not found")
    print("Note: docking and RDKit calculations were not rerun by this verifier")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, OSError, ValueError, KeyError) as error:
        print(f"VERIFY FAILED: {error}", file=sys.stderr)
        raise SystemExit(1)
