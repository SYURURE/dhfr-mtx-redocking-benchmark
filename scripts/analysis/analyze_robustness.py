from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from statistics import mean, median, pstdev

from rdkit import Chem
from rdkit.Chem import rdFMCS, rdMolAlign


SUCCESS_THRESHOLD = 2.0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze the 4DFR seed/exhaustiveness robustness matrix."
    )
    parser.add_argument(
        "--crystal",
        type=Path,
        default=Path("work/4dfr/ligand/4DFR_MTX_A_crystal.sdf"),
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        default=Path("work/4dfr/robustness_4DFR/runs"),
    )
    parser.add_argument(
        "--run-summary",
        type=Path,
        default=Path("work/4dfr/robustness_4DFR/aws_run_summary.csv"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("work/4dfr/robustness_4DFR/robustness_results.csv"),
    )
    return parser.parse_args()


def load_sdf(path: Path) -> list[Chem.Mol]:
    supplier = Chem.SDMolSupplier(
        str(path),
        sanitize=False,
        removeHs=False,
        strictParsing=False,
    )
    return [mol for mol in supplier if mol is not None]


def prepare_heavy_atom_molecule(mol: Chem.Mol) -> Chem.Mol:
    editable = Chem.RWMol(mol)

    hydrogen_indices = [
        atom.GetIdx()
        for atom in editable.GetAtoms()
        if atom.GetAtomicNum() == 1
    ]

    for atom_idx in reversed(hydrogen_indices):
        editable.RemoveAtom(atom_idx)

    result = editable.GetMol()
    result.UpdatePropertyCache(strict=False)
    Chem.FastFindRings(result)
    return result


def make_atom_maps(
    probe: Chem.Mol,
    reference: Chem.Mol,
) -> tuple[list[list[tuple[int, int]]], int]:
    mcs = rdFMCS.FindMCS(
        [probe, reference],
        atomCompare=rdFMCS.AtomCompare.CompareElements,
        bondCompare=rdFMCS.BondCompare.CompareAny,
        ringMatchesRingOnly=False,
        completeRingsOnly=False,
        timeout=30,
    )

    if mcs.canceled or mcs.numAtoms == 0:
        raise RuntimeError("MCS探索に失敗しました")

    query = Chem.MolFromSmarts(mcs.smartsString)
    if query is None:
        raise RuntimeError("MCS SMARTSの生成に失敗しました")

    probe_matches = probe.GetSubstructMatches(
        query,
        uniquify=False,
        maxMatches=1000,
    )
    reference_matches = reference.GetSubstructMatches(
        query,
        uniquify=False,
        maxMatches=1000,
    )

    if not probe_matches or not reference_matches:
        raise RuntimeError("原子対応候補がありません")

    atom_maps: list[list[tuple[int, int]]] = []

    for probe_match in probe_matches:
        for reference_match in reference_matches:
            atom_maps.append(
                list(zip(probe_match, reference_match))
            )

    return atom_maps, mcs.numAtoms


def calculate_symmetry_rmsd(
    probe: Chem.Mol,
    reference: Chem.Mol,
) -> float:
    atom_maps, _ = make_atom_maps(probe, reference)

    return rdMolAlign.CalcRMS(
        probe,
        reference,
        map=atom_maps,
        symmetrizeConjugatedTerminalGroups=True,
    )


def extract_affinities(molecules: list[Chem.Mol]) -> list[float | None]:
    affinities: list[float | None] = []

    candidate_names = [
        "minimizedAffinity",
        "Affinity",
        "affinity",
        "vina_affinity",
    ]

    for mol in molecules:
        value = None

        for name in candidate_names:
            if mol.HasProp(name):
                try:
                    value = float(mol.GetProp(name))
                    break
                except ValueError:
                    pass

        if value is None:
            for prop_name in mol.GetPropNames():
                if "affinity" in prop_name.lower():
                    try:
                        value = float(mol.GetProp(prop_name))
                        break
                    except ValueError:
                        continue

        affinities.append(value)

    return affinities


def load_elapsed_times(summary_file: Path) -> dict[tuple[int, int], int]:
    elapsed: dict[tuple[int, int], int] = {}

    if not summary_file.exists():
        return elapsed

    with summary_file.open(
        newline="",
        encoding="utf-8",
    ) as handle:
        reader = csv.DictReader(handle)

        for row in reader:
            try:
                key = (
                    int(row["seed"]),
                    int(row["exhaustiveness"]),
                )
                elapsed[key] = int(row["elapsed_seconds"])
            except (KeyError, TypeError, ValueError):
                continue

    return elapsed


def main() -> None:
    args = parse_args()

    if not args.crystal.exists():
        raise FileNotFoundError(args.crystal)

    if not args.run_dir.exists():
        raise FileNotFoundError(args.run_dir)

    crystal_molecules = load_sdf(args.crystal)
    if not crystal_molecules:
        raise RuntimeError("結晶MTXを読み込めません")

    crystal = prepare_heavy_atom_molecule(crystal_molecules[0])
    elapsed_times = load_elapsed_times(args.run_summary)

    filename_pattern = re.compile(
        r"exh(?P<exhaustiveness>\d+)_seed(?P<seed>\d+)\.sdf$"
    )

    rows: list[dict[str, object]] = []

    for sdf_file in sorted(args.run_dir.glob("*.sdf")):
        match = filename_pattern.match(sdf_file.name)
        if match is None:
            print(f"スキップ: {sdf_file.name}")
            continue

        seed = int(match.group("seed"))
        exhaustiveness = int(match.group("exhaustiveness"))

        poses_raw = load_sdf(sdf_file)
        if not poses_raw:
            print(f"読込失敗: {sdf_file}")
            continue

        affinities = extract_affinities(poses_raw)
        rmsds: list[float] = []

        for pose_raw in poses_raw:
            pose = prepare_heavy_atom_molecule(pose_raw)
            rmsds.append(
                calculate_symmetry_rmsd(pose, crystal)
            )

        pose1_rmsd = rmsds[0]
        pose1_affinity = affinities[0]
        best_rmsd = min(rmsds)
        best_pose = rmsds.index(best_rmsd) + 1

        top1_success = pose1_rmsd <= SUCCESS_THRESHOLD
        topn_success = best_rmsd <= SUCCESS_THRESHOLD

        rows.append(
            {
                "seed": seed,
                "exhaustiveness": exhaustiveness,
                "elapsed_seconds": elapsed_times.get(
                    (seed, exhaustiveness),
                    "",
                ),
                "pose1_affinity": (
                    "" if pose1_affinity is None
                    else pose1_affinity
                ),
                "pose1_rmsd": pose1_rmsd,
                "best_rmsd": best_rmsd,
                "best_pose": best_pose,
                "top1_success": int(top1_success),
                "topn_success": int(topn_success),
                "num_poses": len(rmsds),
            }
        )

    if not rows:
        raise RuntimeError("解析対象がありません")

    fieldnames = list(rows[0].keys())

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print()
    print(f"解析run数: {len(rows)}")
    print(f"出力: {args.output}")
    print()

    exhaustiveness_values = sorted(
        {int(row["exhaustiveness"]) for row in rows}
    )

    print(
        "Exhaustiveness\tRuns\tTop1_success\t"
        "TopN_success\tMean_pose1_RMSD\tMedian_pose1_RMSD"
    )

    for exhaustiveness in exhaustiveness_values:
        group = [
            row
            for row in rows
            if row["exhaustiveness"] == exhaustiveness
        ]

        pose1_values = [
            float(row["pose1_rmsd"])
            for row in group
        ]

        top1_rate = (
            100
            * sum(int(row["top1_success"]) for row in group)
            / len(group)
        )
        topn_rate = (
            100
            * sum(int(row["topn_success"]) for row in group)
            / len(group)
        )

        print(
            f"{exhaustiveness}\t\t"
            f"{len(group)}\t"
            f"{top1_rate:.1f}%\t\t"
            f"{topn_rate:.1f}%\t\t"
            f"{mean(pose1_values):.3f}\t\t"
            f"{median(pose1_values):.3f}"
        )

    all_pose1 = [float(row["pose1_rmsd"]) for row in rows]

    print()
    print("全条件まとめ")
    print(f"平均Pose1 RMSD: {mean(all_pose1):.3f} Å")
    print(f"中央値: {median(all_pose1):.3f} Å")
    print(f"標準偏差: {pstdev(all_pose1):.3f} Å")
    print(f"最小値: {min(all_pose1):.3f} Å")
    print(f"最大値: {max(all_pose1):.3f} Å")


if __name__ == "__main__":
    main()
