# Changelog

## Reproducibility-fixed revision — 2026-08-16

### Scientific consistency

- Human 1U72 RMSDを、4通りの等価原子mappingから最小値を採る公開policyへ統一
- Human RMSD CSV、README、Results、図を同じpolicyから再生成
- 4DFR `candidate_maps`を公開コードが返す8へ修正
- 4DFR、1U72、robustness、GNINA解析のmapping重複除去実装を統一

### Fixed inputs and raw evidence

- 4DFR、1U72、MTX ideal、historical結晶MTXを`data/reference/`へ固定
- reference inputの`SHA256SUMS`を追加
- robustness 60 runsの全SDF・全ログarchiveを追加
- GNINA POCの正確な9-pose入力、分割入力、全採点済みSDF、全ログを追加

### Environment and execution metadata

- SMINA、Open Babel、RDKit、NumPy、pandas、SciPy、matplotlibなどをversion固定
- docking環境のLinux x86-64 explicit lockを追加
- GNINA CUDA/cuDNN runtime YAMLとLinux x86-64 explicit lockを追加
- 4DFR historical seed `-1408967744`とCPU 2 threadsを既定化
- GNINA POCのCPU 6 threadsを既定化
- single run、robustness、GNINA scriptsへOS、parameters、tool versions、binary/input hashesの記録を追加

### Verification

- 4DFRと1U72の保存SDFを独立再実行し、SHA-256完全一致を確認
- GNINA 9 output SDFを再採点し、全9件SHA-256完全一致を確認
- raw robustness archiveとraw GNINA出力から公開CSVの完全再生成を確認
- GitHub ActionsへRDKit/RMSD・robustness・GNINAの科学計算回帰テストを追加
- 手動起動のcore SMINA再現workflowを追加
- package manifest、privacy、raw archive構造、固定入力hashの検査を強化
- AIが実行した再現性検証の範囲、結果、限界を`AI_REPRODUCIBILITY_REVIEW.md`として公開記録
- `AI_ASSISTANCE.md`のユーザー・AI役割分担を、実際の監査作業に合わせて更新
