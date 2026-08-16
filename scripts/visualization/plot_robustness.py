import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


parser = argparse.ArgumentParser(description="Plot the 4DFR robustness summary.")
parser.add_argument(
    "--input",
    type=Path,
    default=Path("work/4dfr/robustness_4DFR/robustness_results.csv"),
)
parser.add_argument(
    "--output-dir",
    type=Path,
    default=Path("work/4dfr/robustness_4DFR/figures"),
)
args = parser.parse_args()
args.output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(args.input)

# 1. Pose 1 RMSDのヒストグラム
plt.figure(figsize=(8, 5))
plt.hist(df["pose1_rmsd"], bins=15)
plt.axvline(2.0, linestyle="--", label="Success threshold: 2 Å")
plt.xlabel("Pose 1 symmetry-aware RMSD (Å)")
plt.ylabel("Count")
plt.title("Distribution of Pose 1 RMSD")
plt.legend()
plt.tight_layout()
plt.savefig(args.output_dir / "pose1_rmsd_histogram.png", dpi=200)
plt.close()

# 2. Exhaustiveness別の箱ひげ図
groups = [
    group["pose1_rmsd"].to_numpy()
    for _, group in df.groupby("exhaustiveness")
]
labels = [
    str(value)
    for value in sorted(df["exhaustiveness"].unique())
]

plt.figure(figsize=(8, 5))
plt.boxplot(groups, tick_labels=labels)
plt.axhline(2.0, linestyle="--", label="Success threshold: 2 Å")
plt.xlabel("Exhaustiveness")
plt.ylabel("Pose 1 symmetry-aware RMSD (Å)")
plt.title("Pose 1 RMSD by Exhaustiveness")
plt.legend()
plt.tight_layout()
plt.savefig(args.output_dir / "pose1_rmsd_by_exhaustiveness.png", dpi=200)
plt.close()

# 3. Affinity対RMSD
valid = df.dropna(subset=["pose1_affinity"])

plt.figure(figsize=(8, 5))
plt.scatter(valid["pose1_affinity"], valid["pose1_rmsd"])
plt.axhline(2.0, linestyle="--", label="Success threshold: 2 Å")
plt.xlabel("Pose 1 affinity (kcal/mol)")
plt.ylabel("Pose 1 symmetry-aware RMSD (Å)")
plt.title("Affinity versus Pose 1 RMSD")
plt.legend()
plt.tight_layout()
plt.savefig(args.output_dir / "affinity_vs_pose1_rmsd.png", dpi=200)
plt.close()

# 4. Exhaustiveness別成功率
summary = (
    df.groupby("exhaustiveness")
    .agg(
        top1_success_rate=("top1_success", "mean"),
        topn_success_rate=("topn_success", "mean"),
    )
    .reset_index()
)

summary["top1_success_rate"] *= 100
summary["topn_success_rate"] *= 100

x = range(len(summary))

plt.figure(figsize=(8, 5))
plt.bar(
    [value - 0.2 for value in x],
    summary["top1_success_rate"],
    width=0.4,
    label="Top 1",
)
plt.bar(
    [value + 0.2 for value in x],
    summary["topn_success_rate"],
    width=0.4,
    label="Top N",
)
plt.xticks(x, summary["exhaustiveness"].astype(str))
plt.ylim(0, 100)
plt.xlabel("Exhaustiveness")
plt.ylabel("Success rate (%)")
plt.title("Redocking Success Rate")
plt.legend()
plt.tight_layout()
plt.savefig(args.output_dir / "success_rate_by_exhaustiveness.png", dpi=200)
plt.close()

print(summary.to_string(index=False))
print()
print("PNGファイルを4枚作成しました")
