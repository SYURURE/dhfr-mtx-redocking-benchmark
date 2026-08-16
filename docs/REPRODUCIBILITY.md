# Reproducibility guide

## What is preserved

- Conda環境YAML
- 4DFRと1U72の入力取得・前処理・SMINA実行スクリプト
- seed、exhaustiveness、num_modes、autobox設定
- 保存済みSMINAポーズとログ
- 固定座標・対称性考慮RMSDコード
- 60 runsの一括実行・解析・可視化コード
- GNINA固定ポーズ再スコアリングコード
- 集計CSVと代表図

## What is intentionally not bundled

- RCSB PDBのraw構造ファイル
- SMINA、GNINA、RDKit、Open Babel、PyMOLのバイナリ
- Conda環境そのもの
- 60 runs分の全SDF・全log
- GNINAの全raw出力
- AWSやローカルPCの認証情報、ユーザー名、絶対パス

## Environment setup

```bash
mamba env create -f environment/environment_docking.yml
mamba env create -f environment/environment_analysis.yml
mamba env create -f environment/environment_pymol.yml
```

## 4DFR

```bash
conda activate docking
bash scripts/docking/run_4dfr_redocking.sh
```

デフォルト出力は`work/4dfr`です。公開済みのhistorical 5-pose runは初回コマンドでseedを事前固定していません。ログにはSMINAが選んだseedが残っていますが、公開スクリプトは将来の再実行用に`20260718`を固定しています。したがって、新しいrunのPose番号がhistorical結果と一致するとは限りません。

## Human 1U72

```bash
conda activate docking
bash scripts/docking/run_human_1u72_redocking.sh
```

デフォルトはseed `20260719`、exhaustiveness `16`、9 posesです。

## RMSD analysis

```bash
conda activate analysis
python scripts/analysis/calculate_symmetry_rmsd.py \
  --crystal work/human_1u72/ligand/1U72_MTX_crystal.sdf \
  --docked work/human_1u72/results/1U72_MTX_redocked.sdf \
  --csv work/human_1u72/results/1U72_symmetry_rmsd.csv
```

`matched_atoms`、`crystal_heavy_atoms`、`full_heavy_atom_match`を確認し、部分構造だけのRMSDを採用しないでください。

## 4DFR robustness workflow

`run_4dfr_redocking.sh`で作った作業ディレクトリを基準に、次の入力を同一作業ディレクトリ内へ配置します。

```text
receptor/4DFR_chainA_raw.pdb
ligand/MTX_pH7_4.sdf
ligand/4DFR_MTX_A_crystal.sdf
```

次に一括実行します。

```bash
bash scripts/docking/run_4dfr_robustness.sh
```

既定では`work/4dfr`を入力兼出力の基準ディレクトリとして使用します。別の場所を使う場合は、そのパスを第1引数に指定します。

```bash
bash scripts/docking/run_4dfr_robustness.sh path/to/prepared_4dfr
```

本番前にseed範囲とexhaustivenessを縮小した2-run smoke testを行い、SDF数、CSV行、終了statusを確認してください。以前の出力が混入しないよう、再実行前に別の新規出力ディレクトリを使うことを推奨します。

解析コードは次の既定構造を想定します。

```text
work/4dfr/
├─ ligand/4DFR_MTX_A_crystal.sdf
└─ robustness_4DFR/
   ├─ aws_run_summary.csv
   └─ runs/*.sdf
```

```bash
python scripts/analysis/analyze_robustness.py
python scripts/visualization/plot_robustness.py
```

入力や出力が既定位置と異なる場合は、解析の`--crystal`、`--run-dir`、`--run-summary`、`--output`と、描画の`--input`、`--output-dir`を指定できます。

## GNINA rescoring workflow

GNINA 1.3.3の実行可能ファイルを別途用意します。SMINAの元ポーズ、4DFR受容体、結晶MTXを次の構造へ配置します。

```text
input/
├─ smina_poses_original.sdf
├─ 4DFR_chainA_raw.pdb
└─ 4DFR_MTX_A_crystal.sdf
```

```bash
python scripts/docking/prepare_smina_poses.py
CPU_THREADS=4 bash scripts/docking/run_gnina_rescoring.sh
python scripts/analysis/analyze_gnina_rescoring.py
python scripts/visualization/plot_gnina_rescoring.py
```

元SMINA座標を固定し、GNINAでは`--score_only`を使用します。

## Offline package verification

```bash
python scripts/verify_portfolio.py
```

この検査は、公開パッケージの内部整合性を確認します。科学計算の再実行とは別です。
