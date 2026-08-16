from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regenerate single-run 4DFR and 1U72 figures from summary CSVs."
    )
    parser.add_argument(
        "--four-dfr",
        type=Path,
        default=Path("results/summary/4dfr_single_run_rmsd.csv"),
    )
    parser.add_argument(
        "--human",
        type=Path,
        default=Path("results/summary/human_1u72_rmsd.csv"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("results/figures"),
    )
    return parser.parse_args()


def save_rmsd_bar(dataframe: pd.DataFrame, title: str, output: Path) -> None:
    colors = [
        "#2ca02c" if value <= 2.0 else "#4c78a8"
        for value in dataframe["symmetry_rmsd_A"]
    ]
    plt.figure(figsize=(8, 5))
    plt.bar(dataframe["pose"], dataframe["symmetry_rmsd_A"], color=colors)
    plt.axhline(2.0, color="#d62728", linestyle="--", label="Native-like threshold: 2 Å")
    plt.xticks(dataframe["pose"])
    plt.xlabel("Pose")
    plt.ylabel("Fixed-coordinate symmetry-aware RMSD (Å)")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output, dpi=200)
    plt.close()


def main() -> None:
    args = parse_args()
    four_dfr = pd.read_csv(args.four_dfr)
    human = pd.read_csv(args.human)

    save_rmsd_bar(
        four_dfr,
        "4DFR Redocking RMSD by Pose",
        args.output_root / "4dfr" / "4dfr_rmsd_by_pose.png",
    )
    save_rmsd_bar(
        human,
        "Human 1U72 Redocking RMSD by Pose",
        args.output_root / "human_1u72" / "human_1u72_rmsd_by_pose.png",
    )

    colors = [
        "#2ca02c" if value <= 2.0 else "#4c78a8"
        for value in human["symmetry_rmsd_A"]
    ]
    plt.figure(figsize=(8, 5))
    plt.scatter(
        human["smina_affinity_kcal_mol"],
        human["symmetry_rmsd_A"],
        c=colors,
        s=55,
    )
    for _, row in human.iterrows():
        plt.annotate(
            f"P{int(row['pose'])}",
            (row["smina_affinity_kcal_mol"], row["symmetry_rmsd_A"]),
            xytext=(4, 4),
            textcoords="offset points",
        )
    plt.axhline(2.0, color="#d62728", linestyle="--", label="Native-like threshold: 2 Å")
    plt.xlabel("SMINA affinity (kcal/mol)")
    plt.ylabel("Fixed-coordinate symmetry-aware RMSD (Å)")
    plt.title("Human 1U72 Affinity versus RMSD")
    plt.legend()
    plt.tight_layout()
    affinity_output = (
        args.output_root / "human_1u72" / "human_1u72_affinity_vs_rmsd.png"
    )
    affinity_output.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(affinity_output, dpi=200)
    plt.close()

    top1 = pd.DataFrame(
        {
            "system": ["E. coli 4DFR", "Human 1U72"],
            "rmsd": [
                float(four_dfr.iloc[0]["symmetry_rmsd_A"]),
                float(human.iloc[0]["symmetry_rmsd_A"]),
            ],
        }
    )
    colors = ["#d62728" if value > 2.0 else "#2ca02c" for value in top1["rmsd"]]
    plt.figure(figsize=(7, 5))
    bars = plt.bar(top1["system"], top1["rmsd"], color=colors)
    plt.axhline(2.0, color="#333333", linestyle="--", label="Native-like threshold: 2 Å")
    plt.bar_label(bars, fmt="%.3f Å", padding=3)
    plt.ylabel("Top-1 fixed-coordinate symmetry-aware RMSD (Å)")
    plt.title("Top-1 Redocking Comparison")
    plt.legend()
    plt.tight_layout()
    plt.savefig(
        args.output_root / "human_1u72" / "human_vs_ecoli_top1_comparison.png",
        dpi=200,
    )
    plt.close()

    print("PNG files regenerated: 4")


if __name__ == "__main__":
    main()
