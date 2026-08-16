# Reproducibility guide

## Reproducibility contract

このリポジトリは次を固定しています。

- 4DFR、1U72、MTX ideal、historical結晶MTXの入力snapshotとSHA-256
- 4DFR historical seed `-1408967744`
- 1U72 seed `20260719`
- exhaustiveness、num_modes、autobox、再現用CPU threads
- SMINA、Open Babel、RDKitなどのversionとLinux x86-64 package build
- 保存済みSMINAポーズとログ
- 重複除去した全等価原子mappingから最小値を採るRMSD policy
- 60-run robustnessの全SDF・全ログ
- GNINA proof of conceptの正確な9-pose入力・全出力・全ログ
- 集計CSVと図の生成コード

SMINA、GNINA、RDKit、Open Babel、PyMOL、Condaなどの実行バイナリとConda環境本体は収録していません。

## Environment setup

通常の固定YAML:

```bash
mamba env create -f environment/environment_docking.yml
mamba env create -f environment/environment_analysis.yml
mamba env create -f environment/environment_pymol.yml
mamba env create -f environment/environment_gnina_runtime.yml
```

Linux x86-64で監査時と同一のpackage URL/buildを使う完全lock:

```bash
conda create --name docking-locked --file environment/docking-linux-64-explicit.txt
conda activate docking-locked
```

固定YAMLは可読性と移植性を優先し、完全lockはLinux x86-64での厳密な再現を優先します。

## Reference input verification

```bash
cd data/reference
sha256sum -c SHA256SUMS
cd ../..
```

ドッキングスクリプトも、既定の`INPUT_MODE=bundled`では実行前に同じ検査を行います。

## 4DFR historical single run

```bash
conda activate docking
bash scripts/docking/run_4dfr_redocking.sh
```

既定条件:

- input: `data/reference/`
- output: `work/4dfr`
- seed: `-1408967744`
- CPU: 2
- exhaustiveness: 8
- modes: 5
- autobox_add: 5 Å

期待されるSDF:

```text
0400881cbd88cd714848e05aee634af6d45073536bc58215ae0f383777558f2f  work/4dfr/results/MTX_redocked.sdf
```

保存済み`results/poses/4dfr_mtx_redocked_historical.sdf`と同じSHA-256です。

現在のRCSBサービスから入力を再取得して比較する場合は次を使います。

```bash
INPUT_MODE=download SEED=20260718 bash scripts/docking/run_4dfr_redocking.sh work/4dfr_downloaded
```

RCSBのinstance SDF表現がhistorical変換物と異なる場合、historical RMSDの完全一致は保証されません。

## Human 1U72 single run

```bash
conda activate docking
bash scripts/docking/run_human_1u72_redocking.sh
```

既定条件:

- input: `data/reference/`
- output: `work/human_1u72`
- seed: `20260719`
- CPU: 2
- exhaustiveness: 16
- modes: 9
- autobox_add: 4 Å

期待されるSDF:

```text
50fa9f6d6fa8d390db7e3bc22e2948282737e084acdd0180c4497dbfd7d2ea2c  work/human_1u72/results/1U72_MTX_redocked.sdf
```

保存済み`results/poses/1u72_mtx_redocked.sdf`と同じSHA-256です。

## RMSD policy and analysis

公開コードは次のpolicyを4DFRと1U72の両方に適用します。

1. 明示的水素を除去
2. 33重原子の最大共通部分構造を構築
3. 重複を除いた全等価原子mappingを列挙
4. 座標を再アラインせず、全mappingをRDKit `CalcRMS`へ渡す
5. mapping間の最小RMSDを採用

4DFR:

```bash
conda activate analysis
python scripts/analysis/calculate_symmetry_rmsd.py \
  --crystal data/reference/4DFR_MTX_A_crystal_historical.sdf \
  --docked results/poses/4dfr_mtx_redocked_historical.sdf \
  --csv work/4dfr_historical_rmsd.csv
```

1U72:

```bash
python scripts/analysis/calculate_symmetry_rmsd.py \
  --crystal data/reference/1U72_MTX_crystal_historical.sdf \
  --docked results/poses/1u72_mtx_redocked.sdf \
  --csv work/human_1u72_rmsd.csv
```

`matched_atoms`、`crystal_heavy_atoms`、`full_heavy_atom_match`を確認し、部分構造だけのRMSDを採用しないでください。保存summaryでは、4DFRのcandidate mapsは8、1U72は4です。

## Reanalyze the preserved 60-run robustness study

raw archive SHA-256:

```text
a5ab4135fff9b6b1984fa59881e3d4e1d0b412fb309b7194be0fe40c1a1e146f  data/raw/robustness/4DFR_robustness_results.tar.gz
```

新しい作業ディレクトリへ展開して再解析します。

```bash
mkdir -p work/robustness_replay
tar -xzf data/raw/robustness/4DFR_robustness_results.tar.gz \
  -C work/robustness_replay

python scripts/analysis/analyze_robustness.py \
  --crystal data/reference/4DFR_MTX_A_crystal_historical.sdf \
  --run-dir work/robustness_replay/robustness_4DFR/runs \
  --run-summary work/robustness_replay/robustness_4DFR/aws_run_summary.csv \
  --output work/robustness_replay/robustness_recomputed.csv
```

期待される出力SHA-256:

```text
cf56e480dd905edffb398eb5f684ffbd49a0d256591689dad8020bdc63c27ed3  work/robustness_replay/robustness_recomputed.csv
```

この値は`results/summary/4dfr_robustness_results.csv`と完全一致します。

図を再生成します。

```bash
python scripts/visualization/plot_robustness.py \
  --input work/robustness_replay/robustness_recomputed.csv \
  --output-dir work/robustness_replay/figures
```

60 runs自体を新規に実行する場合は、まず4DFR single runで入力を準備し、次を実行します。

```bash
bash scripts/docking/run_4dfr_redocking.sh
CPU=2 bash scripts/docking/run_4dfr_robustness.sh work/4dfr
```

本番前には`SEED_END=2 EXHAUSTIVENESS_VALUES="8"`などでsmoke testしてください。以前の出力が混入しないよう、新しい`OUTPUT_ROOT`を指定することを推奨します。

## Reanalyze the preserved GNINA proof of concept

`data/raw/gnina_poc/`には、実際に使用した入力と全出力があります。解析コードは`input/`と`output/`を相対参照するため、新しい作業コピーで実行します。

```bash
mkdir -p work/gnina_poc_replay
cp -a data/raw/gnina_poc/input work/gnina_poc_replay/
cp -a data/raw/gnina_poc/output work/gnina_poc_replay/

cd work/gnina_poc_replay
python ../../scripts/analysis/analyze_gnina_rescoring.py
python ../../scripts/visualization/plot_gnina_rescoring.py
cd ../..
```

再生成される3 CSVは`results/summary/`の対応ファイルと完全一致します。

GNINA 1.3.3で再採点まで行う場合は、作業コピー内で次を実行します。

GNINA v1.3.3 binaryを公式releaseから別途取得し、SHA-256を確認します。CUDA 12.8/cuDNN 9 runtimeが必要なbinaryでは、`environment/environment_gnina_runtime.yml`またはLinux x86-64完全lock `environment/gnina-runtime-linux-64-explicit.txt`を使用できます。

```bash
cd work/gnina_poc_replay
sha256sum /path/to/gnina
GNINA_BIN=/path/to/gnina CPU_THREADS=6 \
  bash ../../scripts/docking/run_gnina_rescoring.sh
python ../../scripts/analysis/analyze_gnina_rescoring.py
cd ../..
```

実習時GNINA binaryのSHA-256:

```text
3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172
```

GNINA実行環境やCPU library差により、出力テキストの完全一致が保証されない場合があります。保存raw出力からの解析CSV再生成は回帰テストで確認します。

## Verification levels

### Lightweight package verification

Python標準ライブラリだけを使用します。

```bash
python scripts/verify_portfolio.py
```

必須ファイル、manifest、raw archive構造、SDF件数、保存CSV、PNG、Markdown links、一般的な秘密情報・個人パスを確認します。

### Scientific regression

RDKit環境で実計算します。

```bash
conda activate analysis
python scripts/tests/test_scientific_regression.py
```

次を入力から再計算して保存値と照合します。

- 4DFR historical RMSD
- Human 1U72 symmetry-aware RMSD
- raw 60-run archiveからrobustness summary
- raw GNINA入出力からcomparison/ranking CSV

GitHub Actionsの通常push/PRでもlightweight検査とscientific regressionの両方を実行します。

### Full single-run docking workflow

`.github/workflows/reproduce-core.yml`は手動起動用です。固定入力と固定Conda環境を使って4DFR・1U72を再ドッキングし、保存SDFのSHA-256と照合します。計算時間を要するため、通常pushごとには実行しません。
