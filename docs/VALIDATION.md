# Independent reproducibility validation

## Validation date and platform

- Date: 2026-08-16（Asia/Tokyo）
- Platform: WSL2 Ubuntu 26.04, Linux x86-64
- Conda: 26.3.2
- Python: 3.11.15
- SMINA: 2020.12.10
- Open Babel package: 3.1.1（runtime表示 3.1.0）
- RDKit: 2023.09.6
- GNINA evidence version: 1.3.3, `master:6fe1ce2`, built 2026-06-30

## Validated outcomes

### Core docking

固定入力、固定seed、CPU 2 threadsで単発ドッキングを独立再実行しました。

| System | Preserved SDF SHA-256 | Recomputed SDF SHA-256 | Result |
|---|---|---|---|
| 4DFR historical | `0400881cbd88cd714848e05aee634af6d45073536bc58215ae0f383777558f2f` | `0400881cbd88cd714848e05aee634af6d45073536bc58215ae0f383777558f2f` | Exact |
| Human 1U72 | `50fa9f6d6fa8d390db7e3bc22e2948282737e084acdd0180c4497dbfd7d2ea2c` | `50fa9f6d6fa8d390db7e3bc22e2948282737e084acdd0180c4497dbfd7d2ea2c` | Exact |

### RMSD analysis

- 4DFR historical結晶SDFを固定し、保存5ポーズのRMSDと一致
- 1U72は4通りの等価原子mappingを列挙し、最小RMSDを採るpolicyへ統一
- 保存CSVのcandidate mapsを4DFR=8、1U72=4へ修正
- Human CSV、README、Results、図を同じpolicyから再生成

### Robustness study

60 runsのraw archiveを展開し、全SDFから再解析しました。再生成CSVは保存summaryとSHA-256完全一致しました。

```text
cf56e480dd905edffb398eb5f684ffbd49a0d256591689dad8020bdc63c27ed3
```

### GNINA proof of concept

正確な9-pose入力をGNINA 1.3.3、binary SHA-256 `3340c1f49cd3c7c84d8699182a1c6af13c7fa2a22448d1204640446106f72172`、CPU 6 threads、固定runtimeで再採点しました。9個すべての採点済みSDFが保存raw出力とSHA-256完全一致し、再解析した次の3 CSVも保存summaryと完全一致しました。

- `gnina_rescoring_comparison.csv`
- `gnina_ranked_by_cnnscore.csv`
- `gnina_ranked_by_cnnaffinity.csv`

## Automated checks

通常のpush/pull requestでは次を自動実行します。

1. manifest、固定入力hash、raw archive構造、保存CSV、PNG、links、privacy、Python/Bash構文
2. RDKitによる4DFR・1U72 RMSDの再計算
3. raw 60-run archiveからrobustness CSVの再生成
4. raw GNINA入出力から3 CSVの再生成

手動workflow `Reproduce core docking`では4DFR・1U72のSMINAドッキングを再実行し、生成SDFを保存物とSHA-256およびbyte comparisonで照合します。

## Remaining boundaries

- ビット単位のSMINA一致は上記Linux x86-64環境で確認した結果であり、別OS、CPU architecture、compiler、thread数での完全一致を保証しない。
- GNINA binary自体はライセンス・容量・実行環境依存性のため同梱していない。正確な入力、全raw出力、実習時binary SHA-256、CUDA/cuDNN runtime YAMLとLinux x86-64完全lockを保存している。
- 上記固定環境ではGNINA出力の完全一致を確認したが、別GNINA build、CUDA/cuDNN、CPU architectureでの完全一致までは保証しない。
- PNGはfont/matplotlib buildでbyte列が変わり得るため、元CSVと図の意味内容を回帰対象とする。
- 本研究は教育用redocking benchmarkであり、結合自由エネルギー、実測活性、薬効を証明しない。
