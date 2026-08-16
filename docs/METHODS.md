# Methods

## Study design

本プロジェクトは4つの段階から構成されます。

1. *E. coli* DHFR–MTX（4DFR）の単発再ドッキング
2. ヒトDHFR–NADPH–MTX（1U72）の再ドッキングと4DFRとの記述的比較
3. 4DFRにおけるrandom seedとexhaustivenessの頑健性評価
4. 4DFRの固定ポーズに対するGNINA CNN再スコアリング

## Structural inputs

構造はRCSB PDBから取得し、再現性監査時に使用したsnapshotを`data/reference/`へhash固定して収録しています。

- `4DFR`: *E. coli* DHFR–MTX
- `1U72`: human DHFR–NADPH–MTX
- `MTX`: RCSB Chemical Componentのideal SDFおよび各PDB entryのinstance SDF

実行スクリプトは既定で固定snapshotを使います。`INPUT_MODE=download`を指定した場合のみ公式URLから現在の入力を取得します。固定入力のSHA-256は`data/reference/SHA256SUMS`に記録しています。

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
- historical実行時seed: `-1408967744`（保存ログから復元し、公開スクリプトの既定値として固定）
- 再現用既定CPU threads: 2

### Human 1U72

- autobox: crystallographic MTX
- `autobox_add`: 4 Å
- exhaustiveness: 16
- modes: 9
- seed: 20260719
- 再現用既定CPU threads: 2
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
3. 最大共通部分構造から、重複を除いた原子対応候補を列挙
4. カルボキシラートなどの等価原子mappingをすべてRDKit `CalcRMS`へ渡す
5. 候補mapping間の最小固定座標重原子RMSDを採用
6. 33重原子すべてが対応していることを確認

このmapping policyを4DFR、1U72、robustness、GNINA POCで統一しています。保存CSVの`candidate_maps`は公開コードが実際に評価した重複除去後のmapping数です。

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
