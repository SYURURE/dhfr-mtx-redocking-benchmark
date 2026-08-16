#!/usr/bin/env python3
"""Symmetry-aware, fixed-coordinate heavy-atom RMSD for redocking poses.

The coordinates are NOT superposed before RMSD calculation. This is intentional:
redocking evaluation should preserve the receptor coordinate frame and assess the
position, orientation, and conformation of each predicted pose relative to the
crystallographic ligand.
"""

from __future__ import annotations

import argparse
import csv
from itertools import product
from pathlib import Path
from typing import Iterable

from rdkit import Chem, RDLogger
from rdkit.Chem import rdFMCS, rdMolAlign


def load_sdf(path: Path) -> list[Chem.Mol]:
    """Load an SDF, falling back to relaxed parsing for PDB-derived files."""
    supplier = Chem.SDMolSupplier(str(path), sanitize=True, removeHs=False)
    molecules = [mol for mol in supplier if mol is not None]
    if molecules:
        return molecules

    supplier = Chem.SDMolSupplier(
        str(path),
        sanitize=False,
        removeHs=False,
        strictParsing=False,
    )
    molecules = [mol for mol in supplier if mol is not None]
    if not molecules:
        raise RuntimeError(f"Could not read any molecule from: {path}")
    return molecules


def prepare_heavy_atom_molecule(mol: Chem.Mol) -> Chem.Mol:
    """Remove explicit H atoms and initialize the minimal RDKit caches needed."""
    editable = Chem.RWMol(mol)
    hydrogen_indices = [
        atom.GetIdx() for atom in editable.GetAtoms() if atom.GetAtomicNum() == 1
    ]
    for atom_index in reversed(hydrogen_indices):
        editable.RemoveAtom(atom_index)

    result = editable.GetMol()
    result.UpdatePropertyCache(strict=False)
    Chem.FastFindRings(result)
    return result


def generate_symmetry_maps(
    probe: Chem.Mol,
    reference: Chem.Mol,
    max_matches: int = 1000,
) -> tuple[list[list[tuple[int, int]]], int]:
    """Enumerate atom mappings, including equivalent/symmetric atom assignments."""
    mcs = rdFMCS.FindMCS(
        [probe, reference],
        atomCompare=rdFMCS.AtomCompare.CompareElements,
        bondCompare=rdFMCS.BondCompare.CompareAny,
        ringMatchesRingOnly=False,
        completeRingsOnly=False,
        timeout=30,
    )
    if mcs.canceled:
        raise RuntimeError("MCS search timed out")
    if mcs.numAtoms == 0:
        raise RuntimeError("No common heavy-atom structure found")

    query = Chem.MolFromSmarts(mcs.smartsString)
    if query is None:
        raise RuntimeError("Could not construct an MCS query")

    probe_matches = probe.GetSubstructMatches(
        query, uniquify=False, maxMatches=max_matches
    )
    reference_matches = reference.GetSubstructMatches(
        query, uniquify=False, maxMatches=max_matches
    )
    if not probe_matches or not reference_matches:
        raise RuntimeError("Could not enumerate atom mappings")

    unique_maps: dict[tuple[tuple[int, int], ...], None] = {}
    for probe_match, reference_match in product(probe_matches, reference_matches):
        mapping = tuple(zip(probe_match, reference_match))
        unique_maps[mapping] = None

    return [list(mapping) for mapping in unique_maps], mcs.numAtoms


def get_score(mol: Chem.Mol) -> str:
    for key in (
        "minimizedAffinity",
        "affinity",
        "vina_affinity",
        "RFScore",
    ):
        if mol.HasProp(key):
            return mol.GetProp(key)
    return ""


def calculate(
    crystal_file: Path,
    docked_file: Path,
    output_csv: Path,
) -> None:
    crystal_mols = load_sdf(crystal_file)
    docked_mols = load_sdf(docked_file)

    crystal = prepare_heavy_atom_molecule(crystal_mols[0])
    crystal_heavy_atoms = crystal.GetNumAtoms()

    rows: list[dict[str, object]] = []
    print("Pose\tSymmetry_RMSD_A\tAtoms\tCandidate_maps\tScore")
    print("----------------------------------------------------------------")

    for pose_number, original_pose in enumerate(docked_mols, start=1):
        pose = prepare_heavy_atom_molecule(original_pose)
        atom_maps, matched_atoms = generate_symmetry_maps(pose, crystal)

        # CalcRMS compares current coordinates and does not align/superpose the probe.
        rmsd = rdMolAlign.CalcRMS(
            pose,
            crystal,
            map=atom_maps,
            symmetrizeConjugatedTerminalGroups=True,
        )

        score = get_score(original_pose)
        full_match = matched_atoms == crystal_heavy_atoms == pose.GetNumAtoms()
        rows.append(
            {
                "pose": pose_number,
                "symmetry_rmsd_A": f"{rmsd:.3f}",
                "matched_atoms": matched_atoms,
                "crystal_heavy_atoms": crystal_heavy_atoms,
                "candidate_maps": len(atom_maps),
                "full_heavy_atom_match": full_match,
                "score": score,
            }
        )
        print(
            f"{pose_number}\t{rmsd:.3f}\t\t{matched_atoms}\t"
            f"{len(atom_maps)}\t\t{score}"
        )

    with output_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    best = min(rows, key=lambda row: float(row["symmetry_rmsd_A"]))
    print("----------------------------------------------------------------")
    print(f"Calculated: {len(rows)}/{len(docked_mols)} poses")
    print(f"Crystal heavy atoms: {crystal_heavy_atoms}")
    print(
        f"Best pose: {best['pose']} "
        f"(RMSD = {best['symmetry_rmsd_A']} A; "
        f"candidate maps = {best['candidate_maps']})"
    )
    print(f"CSV written to: {output_csv}")

    if float(best["symmetry_rmsd_A"]) > 10.0:
        print(
            "WARNING: all RMSDs are very large. Confirm that crystal and docked "
            "ligands are expressed in the same receptor coordinate frame."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--crystal",
        type=Path,
        default=Path("4DFR_MTX_A_crystal.sdf"),
        help="Crystallographic ligand SDF",
    )
    parser.add_argument(
        "--docked",
        type=Path,
        default=Path("MTX_redocked.sdf"),
        help="Multi-pose docking SDF",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=Path("symmetry_rmsd_results.csv"),
        help="Output CSV path",
    )
    parser.add_argument(
        "--quiet-rdkit",
        action="store_true",
        help="Suppress RDKit warnings (not recommended while debugging)",
    )
    args = parser.parse_args()

    if args.quiet_rdkit:
        RDLogger.DisableLog("rdApp.warning")

    for path in (args.crystal, args.docked):
        if not path.exists():
            raise FileNotFoundError(path)

    calculate(args.crystal, args.docked, args.csv)


if __name__ == "__main__":
    main()
