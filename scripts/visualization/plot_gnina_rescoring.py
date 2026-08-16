from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


INPUT_FILE = Path(
    "output/gnina_rescoring_comparison.csv"
)

PLOT_DIRECTORY = Path("plots")
PLOT_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)

dataframe = pd.read_csv(INPUT_FILE)


# CNNscore vs RMSD
valid = dataframe.dropna(
    subset=["cnnscore", "rmsd"]
)

plt.figure(figsize=(8, 5))
plt.scatter(
    valid["cnnscore"],
    valid["rmsd"],
)

for _, row in valid.iterrows():
    plt.annotate(
        f"P{int(row['original_pose'])}",
        (
            row["cnnscore"],
            row["rmsd"],
        ),
    )

plt.axhline(
    2.0,
    linestyle="--",
    label="Native-like threshold: 2 Å",
)

plt.xlabel("GNINA CNNscore")
plt.ylabel("Symmetry-aware RMSD (Å)")
plt.title("CNNscore versus RMSD")
plt.legend()
plt.tight_layout()
plt.savefig(
    PLOT_DIRECTORY
    / "cnnscore_vs_rmsd.png",
    dpi=200,
)
plt.close()


# CNNaffinity vs RMSD
valid = dataframe.dropna(
    subset=["cnnaffinity", "rmsd"]
)

plt.figure(figsize=(8, 5))
plt.scatter(
    valid["cnnaffinity"],
    valid["rmsd"],
)

for _, row in valid.iterrows():
    plt.annotate(
        f"P{int(row['original_pose'])}",
        (
            row["cnnaffinity"],
            row["rmsd"],
        ),
    )

plt.axhline(
    2.0,
    linestyle="--",
    label="Native-like threshold: 2 Å",
)

plt.xlabel("GNINA CNNaffinity")
plt.ylabel("Symmetry-aware RMSD (Å)")
plt.title("CNNaffinity versus RMSD")
plt.legend()
plt.tight_layout()
plt.savefig(
    PLOT_DIRECTORY
    / "cnnaffinity_vs_rmsd.png",
    dpi=200,
)
plt.close()


# 順位比較
rank_columns = [
    "smina_rank",
    "cnnscore_rank",
    "cnnaffinity_rank",
    "rmsd_rank",
]

plt.figure(figsize=(9, 5))

for column in rank_columns:
    plt.plot(
        dataframe["original_pose"],
        dataframe[column],
        marker="o",
        label=column,
    )

plt.gca().invert_yaxis()
plt.xticks(
    dataframe["original_pose"]
)
plt.xlabel("Original SMINA Pose")
plt.ylabel("Rank (1 is best)")
plt.title("SMINA, GNINA and RMSD Rank Comparison")
plt.legend()
plt.tight_layout()
plt.savefig(
    PLOT_DIRECTORY
    / "rank_comparison.png",
    dpi=200,
)
plt.close()

print("PNGファイルを3枚作成しました")
