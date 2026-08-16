# Results directory

このディレクトリには、実習時に保存された生成物と、その生成物から作成した要約を収録しています。

## `poses/`

- `4dfr_mtx_redocked_historical.sdf`: 4DFRの初回探索で得た5ポーズ。SMINAログから復元したseed `-1408967744`を公開スクリプトの既定値として固定しています。
- `1u72_mtx_redocked.sdf`: seed `20260719`、exhaustiveness `16`、最大9ポーズで得たヒトDHFR 1U72の結果。

## `logs/`

上記2回のSMINAログです。SMINAログ内の `rmsd l.b.` / `rmsd u.b.` は結晶MTXに対するRMSDではなく、同一run内のbest modeに対するモード間距離です。

## `summary/`

- `4dfr_single_run_rmsd.csv`: 初回4DFRの5ポーズを結晶MTXと比較した固定座標・対称性考慮重原子RMSD。
- `human_1u72_rmsd.csv`: 1U72の9ポーズを結晶MTXと比較した結果。
- `4dfr_robustness_results.csv`: seed 1–20 × exhaustiveness 8/16/32の60 runs集計。
- `gnina_rescoring_comparison.csv`: 1つの4DFR runに含まれる9ポーズをGNINAで固定ポーズ再スコアリングした比較。
- `gnina_ranked_by_*.csv`: GNINA指標別の順位表。

## `figures/`

上記CSVまたは保存済み報告書の表から生成された代表図です。スクリーンショットではなく、比較に必要なグラフを優先しています。

## Raw data policy

60 runs分の全SDF・ログは`data/raw/robustness/4DFR_robustness_results.tar.gz`に収録しています。GNINA POCの正確な9-pose入力、分割入力、採点済みSDF、全ログは`data/raw/gnina_poc/`に収録しています。内容とSHA-256は[`data/README.md`](../data/README.md)を参照してください。
