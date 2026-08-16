# Methods

## Study design

本プロジェクトは4つの段階から構成されます。

1. *E. coli* DHFR–MTX（4DFR）の単発再ドッキング
2. ヒトDHFR–NADPH–MTX（1U72）の再ドッキングと4DFRとの記述的比較
3. 4DFRにおけるrandom seedとexhaustivenessの頑健性評価
4. 4DFRの固定ポーズに対するGNINA CNN再スコアリング

## Structural inputs

構造はRCSB PDBから取得します。

- `4DFR`: *E. coli* DHFR–MTX
- `1U72`: human DHFR–NADPH–MTX
- `MTX`: RCSB Chemical Componentのideal SDFおよび各PDB entryのinstance SDF

Raw PDB/SDFはリポジトリに固定保存せず、実行スクリプトが公式URLから取得します。

## Receptor preparation

### 4DFR

- Chain Aの`ATOM`レコードを抽出
- MTX、水、その他HETATMは受容体から除外
- 教育用の簡易経路として、テスト済みconda-forge版SMINAではPDBを直接入力
- 別buildがPDBを拒否する場合は、Open Babelでrigid PDBQTを作成するfallbackを用意

### Human 1U72

- Chain Aのタンパク質を使用
- NADPHに対応するPDB residue name `NDP`を受容体へ保持
- MTXと46個の結晶水は除外
- NADPHの厳密なプロトン化・部分電荷は再評価していない

## Ligand preparation

RCSBのMTX ideal SDFをOpen Babelへ入力し、`-p 7.4 --gen3d`で教育用の3D入力を生成しました。単一の簡易状態であり、MTXの複数プロトン化・互変異性状態を網羅していません。

## Docking parameters

### 4DFR exploratory run

- autobox: crystallographic MTX
- `autobox_add`: 5 Å
- exhaustiveness: 8
- modes: 5
- 初回コマンドではseedを事前固定せず、実行時seedをログに保存

### Human 1U72

- autobox: crystallographic MTX
- `autobox_add`: 4 Å
- exhaustiveness: 16
- modes: 9
- seed: 20260719
- receptor: human DHFR Chain A + NADPH (`NDP`)

### 4DFR robustness study

- random seed: 1–20
- exhaustiveness: 8, 16, 32
- modes: 9
- `autobox_add`: 4 Å
- total: 60 runs、最大540ポーズ

## Fixed-coordinate symmetry-aware RMSD

Redocking評価では、予測リガンドを結晶リガンドへ再アラインしてから比較すると、受容体座標系における位置・向きの誤差が消えてしまいます。このためRDKit `CalcRMS`を使用し、座標を動かさずに比較しました。

手順は次のとおりです。

1. 明示的水素を除去
2. 分子キャッシュと環情報を初期化
3. 最大共通部分構造から原子対応候補を列挙
4. カルボキシラートなどの等価原子を考慮
5. 固定座標の重原子RMSDを計算
6. 33重原子すべてが対応していることを確認

判定目安はRMSD ≤ 2.0 Åとしました。

## Robustness metrics

- Top 1 success: Pose 1 RMSD ≤ 2.0 Å
- Top N success: そのrunの最大9ポーズ中、最小RMSD ≤ 2.0 Å
- Pose 1 affinity
- Pose 1 RMSD
- best RMSD
- best pose rank
- elapsed time

## GNINA rescoring

SMINA生成済みの9ポーズを個別SDFへ分割し、座標を動かさずにGNINAへ入力しました。

```text
--score_only
--cnn_scoring rescore
--no_gpu
```

比較した指標はSMINA affinity、GNINA empirical score、CNNscore、CNNaffinity、CNNvariance、結晶MTXとのRMSDです。CNNscore/CNNaffinityは大きい方、affinity/RMSDは小さい方を上位としました。

