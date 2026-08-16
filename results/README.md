# Results directory

このディレクトリには、実習時に保存された生成物と、その生成物から作成した要約を収録しています。

## `poses/`

- `4dfr_mtx_redocked_historical.sdf`: 4DFRの初回探索で得た5ポーズ。初回コマンドではseedを明示指定していませんが、SMINAログには実行時seedが記録されています。
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

60 runs分の全SDF・ログとGNINAの全raw logは、公開ZIPを読みやすく保つため収録していません。再計算スクリプトと集計CSVは収録しています。元のraw archiveはローカルで保管されています。
