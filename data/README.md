# Reproducibility data

このディレクトリには、公表値を第三者が入力から再計算できるように固定した入力とraw evidenceを収録しています。

## `reference/`

単発4DFR・1U72ドッキングとRMSD解析で使用した固定入力です。`SHA256SUMS`で取得物とhistorical変換物を検証できます。実行スクリプトは既定でこのディレクトリを使うため、ネットワークアクセスによる入力変化を避けられます。

- `4DFR.pdb`, `1U72.pdb`, `MTX_ideal.sdf`: RCSB PDBから取得した固定snapshot
- `4DFR_MTX_A_crystal_historical.sdf`: historical 4DFR RMSDで使った結晶MTX。PDB座標からOpen Babelで生成された保存物
- `1U72_MTX_crystal_historical.sdf`: Human 1U72 RMSDで使う固定結晶MTX

RCSB PDB archive dataとprogrammatic API dataはCC0 1.0です。帰属情報と構造DOIは[`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md)に記載しています。

## `raw/robustness/`

`4DFR_robustness_results.tar.gz`には、60 runsすべてのSDF、SMINAログ、run summaryが含まれます。

- archive SHA-256: `a5ab4135fff9b6b1984fa59881e3d4e1d0b412fb309b7194be0fe40c1a1e146f`
- 20 seeds × exhaustiveness 8/16/32 = 60 runs
- このarchiveと固定4DFR結晶SDFから、`results/summary/4dfr_robustness_results.csv`を完全再生成できます。

## `raw/gnina_poc/`

GNINA proof of conceptで実際に使った入力と全出力です。

- `input/smina_poses_original.sdf`: 元の9-pose SMINA SDF
- `input/poses/`: 個別に分割した9ポーズ
- `input/4DFR_chainA_raw.pdb`: GNINA受容体
- `input/4DFR_MTX_A_crystal.sdf`: RMSD参照
- `output/poses/`: GNINA 1.3.3の採点済みSDF
- `output/logs/`: 全GNINAログ
- `output/*.csv`: run summaryと再解析出力

固定GNINA 1.3.3 binary、CPU 6 threads、収録runtime lockでの再実行では、9個の採点済みSDFが保存raw出力とSHA-256完全一致しました。

主なSHA-256:

```text
154a2babf6f4e20dd4e8c9c547ba8a5f6260ba68337b55967e4cbd22e9c28899  input/smina_poses_original.sdf
ce63df81992a752971b4f7b6b002b3c7784779dd5d89e05c4d2fa25340594edb  input/4DFR_chainA_raw.pdb
33bd1b7e3ec42f988025766fc2392d511a6983937f5361983c6444790e40af24  input/4DFR_MTX_A_crystal.sdf
3ffd445419a8051b66a6e54146bec2256ccef7c68dcddba931bea15ac13f2267  output/gnina_rescoring_comparison.csv
```

SMINA・GNINA・RDKit・Open Babelなどの実行バイナリは同梱していません。
