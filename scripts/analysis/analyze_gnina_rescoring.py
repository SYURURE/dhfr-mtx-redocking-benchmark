from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import rdFMCS, rdMolAlign
from scipy.stats import spearmanr


CRYSTAL_FILE = Path(
    "input/4DFR_MTX_A_crystal.sdf"
)

INPUT_POSE_DIRECTORY = Path("input/poses")
GNINA_POSE_DIRECTORY = Path("output/poses")

OUTPUT_FILE = Path(
    "output/gnina_rescoring_comparison.csv"
)

CNN_SCORE_SORTED_FILE = Path(
    "output/ranked_by_cnnscore.csv"
)

CNN_AFFINITY_SORTED_FILE = Path(
    "output/ranked_by_cnnaffinity.csv"
)

SUCCESS_THRESHOLD = 2.0

RDLogger.DisableLog("rdApp.warning")


def load_first_molecule(path: Path) -> Chem.Mol:
    supplier = Chem.SDMolSupplier(
        str(path),
        sanitize=False,
        removeHs=False,
        strictParsing=False,
    )

    for molecule in supplier:
        if molecule is not None:
            return molecule

    raise RuntimeError(
        f"分子を読み込めませんでした: {path}"
    )


def prepare_heavy_atoms(
    molecule: Chem.Mol,
) -> Chem.Mol:
    editable = Chem.RWMol(molecule)

    hydrogen_indices = [
        atom.GetIdx()
        for atom in editable.GetAtoms()
        if atom.GetAtomicNum() == 1
    ]

    for atom_index in reversed(
        hydrogen_indices
    ):
        editable.RemoveAtom(atom_index)

    result = editable.GetMol()
    result.UpdatePropertyCache(strict=False)
    Chem.FastFindRings(result)

    return result


def generate_atom_maps(
    probe: Chem.Mol,
    reference: Chem.Mol,
) -> list[list[tuple[int, int]]]:
    mcs = rdFMCS.FindMCS(
        [probe, reference],
        atomCompare=(
            rdFMCS.AtomCompare.CompareElements
        ),
        bondCompare=(
            rdFMCS.BondCompare.CompareAny
        ),
        ringMatchesRingOnly=False,
        completeRingsOnly=False,
        timeout=30,
    )

    if mcs.canceled or mcs.numAtoms == 0:
        raise RuntimeError(
            "MCS探索に失敗しました"
        )

    query = Chem.MolFromSmarts(
        mcs.smartsString
    )

    if query is None:
        raise RuntimeError(
            "MCS SMARTS生成に失敗しました"
        )

    probe_matches = probe.GetSubstructMatches(
        query,
        uniquify=False,
        maxMatches=1000,
    )

    reference_matches = (
        reference.GetSubstructMatches(
            query,
            uniquify=False,
            maxMatches=1000,
        )
    )

    unique_maps: dict[
        tuple[tuple[int, int], ...],
        None,
    ] = {}

    for probe_match in probe_matches:
        for reference_match in reference_matches:
            mapping = tuple(
                zip(
                    probe_match,
                    reference_match,
                )
            )
            unique_maps[mapping] = None

    if not unique_maps:
        raise RuntimeError(
            "原子対応候補がありません"
        )

    return [
        list(mapping)
        for mapping in unique_maps
    ]


def calculate_rmsd(
    probe: Chem.Mol,
    reference: Chem.Mol,
) -> float:
    atom_maps = generate_atom_maps(
        probe,
        reference,
    )

    return rdMolAlign.CalcRMS(
        probe,
        reference,
        map=atom_maps,
        symmetrizeConjugatedTerminalGroups=True,
    )


def get_property(
    molecule: Chem.Mol,
    candidate_names: list[str],
) -> str | None:
    property_lookup = {
        name.lower(): name
        for name in molecule.GetPropNames()
    }

    for candidate in candidate_names:
        actual_name = property_lookup.get(
            candidate.lower()
        )

        if actual_name is not None:
            return molecule.GetProp(
                actual_name
            )

    return None


def get_float_property(
    molecule: Chem.Mol,
    candidate_names: list[str],
) -> float | None:
    value = get_property(
        molecule,
        candidate_names,
    )

    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def add_rank(
    dataframe: pd.DataFrame,
    source_column: str,
    destination_column: str,
    ascending: bool,
) -> None:
    valid = dataframe[source_column].notna()

    dataframe[destination_column] = pd.NA

    dataframe.loc[
        valid,
        destination_column,
    ] = (
        dataframe.loc[valid, source_column]
        .rank(
            ascending=ascending,
            method="min",
        )
        .astype(int)
    )


def main() -> None:
    crystal = prepare_heavy_atoms(
        load_first_molecule(CRYSTAL_FILE)
    )

    rows = []

    input_pattern = re.compile(
        r"pose_(\d+)\.sdf$"
    )

    for input_file in sorted(
        INPUT_POSE_DIRECTORY.glob(
            "pose_*.sdf"
        )
    ):
        match = input_pattern.match(
            input_file.name
        )

        if match is None:
            continue

        pose_number = int(match.group(1))

        gnina_file = (
            GNINA_POSE_DIRECTORY
            / f"pose_{pose_number:02d}_gnina.sdf"
        )

        if not gnina_file.exists():
            print(
                f"GNINA出力なし: Pose {pose_number}"
            )
            continue

        input_molecule = load_first_molecule(
            input_file
        )

        gnina_molecule = load_first_molecule(
            gnina_file
        )

        input_heavy = prepare_heavy_atoms(
            input_molecule
        )

        rmsd = calculate_rmsd(
            input_heavy,
            crystal,
        )

        smina_affinity = get_float_property(
            input_molecule,
            [
                "SMINA_Affinity_Original",
                "minimizedAffinity",
                "Affinity",
                "affinity",
                "vina_affinity",
            ],
        )

        cnnscore = get_float_property(
            gnina_molecule,
            [
                "CNNscore",
                "CNN_score",
            ],
        )

        cnnaffinity = get_float_property(
            gnina_molecule,
            ["CNNaffinity"],
        )

        cnnvariance = get_float_property(
            gnina_molecule,
            [
                "CNNaffinity_variance",
                "CNNvariance",
            ],
        )

        gnina_empirical = get_float_property(
            gnina_molecule,
            ["minimizedAffinity"],
        )

        rows.append(
            {
                "original_pose": pose_number,
                "smina_affinity": smina_affinity,
                "gnina_empirical_score": (
                    gnina_empirical
                ),
                "cnnscore": cnnscore,
                "cnnaffinity": cnnaffinity,
                "cnnvariance": cnnvariance,
                "rmsd": rmsd,
                "native_like": int(
                    rmsd <= SUCCESS_THRESHOLD
                ),
            }
        )

    if not rows:
        raise RuntimeError(
            "解析可能なPoseがありません"
        )

    dataframe = pd.DataFrame(rows)

    add_rank(
        dataframe,
        "smina_affinity",
        "smina_rank",
        ascending=True,
    )

    add_rank(
        dataframe,
        "cnnscore",
        "cnnscore_rank",
        ascending=False,
    )

    add_rank(
        dataframe,
        "cnnaffinity",
        "cnnaffinity_rank",
        ascending=False,
    )

    add_rank(
        dataframe,
        "rmsd",
        "rmsd_rank",
        ascending=True,
    )

    dataframe = dataframe.sort_values(
        "original_pose"
    )

    dataframe.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    dataframe.sort_values(
        "cnnscore",
        ascending=False,
    ).to_csv(
        CNN_SCORE_SORTED_FILE,
        index=False,
    )

    dataframe.sort_values(
        "cnnaffinity",
        ascending=False,
    ).to_csv(
        CNN_AFFINITY_SORTED_FILE,
        index=False,
    )

    display_columns = [
        "original_pose",
        "smina_affinity",
        "smina_rank",
        "cnnscore",
        "cnnscore_rank",
        "cnnaffinity",
        "cnnaffinity_rank",
        "rmsd",
        "rmsd_rank",
        "native_like",
    ]

    print()
    print(
        dataframe[display_columns]
        .round(4)
        .to_string(index=False)
    )

    print()
    print("Top 1比較")

    ranking_methods = [
        (
            "SMINA",
            "smina_affinity",
            True,
        ),
        (
            "CNNscore",
            "cnnscore",
            False,
        ),
        (
            "CNNaffinity",
            "cnnaffinity",
            False,
        ),
    ]

    for label, column, ascending in ranking_methods:
        valid = dataframe.dropna(
            subset=[column]
        )

        top = valid.sort_values(
            column,
            ascending=ascending,
        ).iloc[0]

        print(
            f"{label}: "
            f"Pose {int(top['original_pose'])}, "
            f"RMSD={top['rmsd']:.3f} Å, "
            f"native_like="
            f"{bool(top['native_like'])}"
        )

    best_rmsd_row = dataframe.sort_values(
        "rmsd"
    ).iloc[0]

    print(
        "RMSD最良: "
        f"Pose {int(best_rmsd_row['original_pose'])}, "
        f"RMSD={best_rmsd_row['rmsd']:.3f} Å"
    )

    cnnscore_valid = dataframe.dropna(
        subset=["cnnscore", "rmsd"]
    )

    if len(cnnscore_valid) >= 3:
        correlation = spearmanr(
            cnnscore_valid["cnnscore"],
            cnnscore_valid["rmsd"],
        )

        print()
        print(
            "CNNscoreとRMSDのSpearman相関:"
        )
        print(f"rho = {correlation.statistic:.4f}")
        print(f"p = {correlation.pvalue:.6g}")

    cnnaffinity_valid = dataframe.dropna(
        subset=["cnnaffinity", "rmsd"]
    )

    if len(cnnaffinity_valid) >= 3:
        correlation = spearmanr(
            cnnaffinity_valid["cnnaffinity"],
            cnnaffinity_valid["rmsd"],
        )

        print()
        print(
            "CNNaffinityとRMSDのSpearman相関:"
        )
        print(f"rho = {correlation.statistic:.4f}")
        print(f"p = {correlation.pvalue:.6g}")

    print()
    print(f"結果CSV: {OUTPUT_FILE}")
    print(
        f"CNNscore順位CSV: "
        f"{CNN_SCORE_SORTED_FILE}"
    )


if __name__ == "__main__":
    main()
