# AI-assisted reproducibility review

## Review identification

- Review date: 2026-08-16（Asia/Tokyo）
- Reviewer: OpenAI Codex（AI coding agent）
- Review type: ユーザーの依頼と承認に基づく、ローカル作業環境でのAI支援技術検証
- Reviewed artifact: `dhfr-mtx-redocking-benchmark` 公開用パッケージ

本ファイルは、AIがこのパッケージの再現可能性をどの範囲まで実際に検証したかを、公開時に追跡できるよう記録するものです。単に文書を読んだだけではなく、保存データの再解析、主要計算の再実行、ハッシュ照合、公開パッケージの再展開後検査を行いました。

## Performed checks

### 1. Package integrity and public-release checks

- 必須ファイル、Markdownリンク、PNG、CSV、SDFレコード数を検査
- 固定入力のSHA-256、raw archiveの構造、保存summaryの不変条件を検査
- APIキー、秘密鍵、一般的な個人PC絶対パスなどの公開不適切パターンを検査
- PythonおよびBashスクリプトの構文を検査
- `MANIFEST.sha256`を再生成し、収録ファイルと照合
- 作成したZIPを別ディレクトリへ展開し、展開物に対して同じ検査を再実行

### 2. Core SMINA redocking

固定入力、固定seed、CPU 2 threads、記録された環境で4DFRと1U72の単発ドッキングを再実行し、保存SDFとバイト単位で照合しました。

| System | Recomputed/preserved SDF SHA-256 | Result |
|---|---|---|
| 4DFR historical | `0400881cbd88cd714848e05aee634af6d45073536bc58215ae0f383777558f2f` | Exact |
| Human 1U72 | `50fa9f6d6fa8d390db7e3bc22e2948282737e084acdd0180c4497dbfd7d2ea2c` | Exact |

### 3. RMSD calculations

- 4DFRと1U72の保存ポーズをRDKitで再解析
- 1U72について、4通りの等価原子mappingから最小RMSDを採るpolicyへ、コード・CSV・README・Results・図を統一
- 4DFRの`candidate_maps`を、公開コードが実際に返す8へ修正
- 修正後の科学計算回帰テストが合格することを確認

この検査により、旧Human 1U72表示値と公開計算policyの不整合が見つかり、公開版で修正されました。

### 4. Robustness study

60 runs分のraw SDF/log archiveを展開し、全runを再解析しました。再生成したsummary CSVは保存値とSHA-256完全一致しました。

```text
cf56e480dd905edffb398eb5f684ffbd49a0d256591689dad8020bdc63c27ed3
```

### 5. GNINA proof of concept

GNINA 1.3.3、固定runtime、CPU 6 threadsで9ポーズを再採点しました。

- 採点済みSDF: 9/9件が保存raw outputとSHA-256完全一致
- 再生成した`gnina_rescoring_comparison.csv`のSHA-256:
  `3ffd4454a92dac07e73da4fac86a9934037a052800183043e208b3663dd2267`
- CNNscore、CNNaffinity、RMSD順位の3 summary CSVが保存値と一致

## Review outcome

公開版について、次を確認しました。

- 主要な4DFR・1U72 SMINA出力は、検証環境で保存物と完全一致した
- robustnessとGNINAの保存raw evidenceから、公開summaryを再生成できた
- RMSDの計算policy、表示値、図、説明を相互に整合させた
- 軽量検査と科学計算回帰テストが合格した
- ZIPを再展開した状態でも、同じ検査が合格した

詳細な環境、検査方法、残る境界は[Independent reproducibility validation](docs/VALIDATION.md)を参照してください。再実行方法は[Reproducibility](docs/REPRODUCIBILITY.md)、修正内容は[Changelog](CHANGELOG.md)に記載しています。

## Disclosure and limitations

この記録は、AIが実際に実行した技術検証の透明性を高めるためのものです。**人間の査読、独立した第三者監査、規制上のvalidation、品質認証を意味しません。** AIは誤りを起こす可能性があり、検証結果は記載したファイル、環境、条件、検査範囲に限定されます。

本プロジェクトは教育用redocking benchmarkです。創薬上の意思決定、結合自由エネルギー、実測活性、選択性、薬効の証明には使用できません。高い信頼性が必要な用途では、利用者がコード、入力、ログ、出力、科学的解釈を独立に確認してください。

ユーザーとAIの役割分担については[AI_ASSISTANCE.md](AI_ASSISTANCE.md)を参照してください。
