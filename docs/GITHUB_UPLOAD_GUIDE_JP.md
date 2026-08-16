# GitHub登録・修正版反映手順

このパッケージは、公開用に整理・検査したDHFR–MTX再ドッキングのポートフォリオです。元の巨大な作業フォルダではなく、配布ZIPを展開して現れる`dhfr-mtx-redocking-benchmark`フォルダの**中身**だけをGitHubへ登録します。

## 今回の推奨方法: GitHub Desktopで既存レポジトリを更新する

今回のパッケージは100ファイルを超え、同名ファイルの差し替えと新規ファイルの追加が混在します。ブラウザ版GitHubは一度にアップロードできるファイル数に制限があるため、GitHub Desktopの利用を推奨します。

### 1. 新しいZIPを展開する

`dhfr-mtx-redocking-benchmark_AI-reviewed_20260816.zip`を右クリックし、Windowsの「すべて展開」を選びます。

ZIPそのものはGitHubへ登録しません。展開後のフォルダを開き、最上位に`README.md`、`AI_REPRODUCIBILITY_REVIEW.md`、`data`、`scripts`などが見えることを確認します。

### 2. GitHub Desktopで現在のレポジトリを複製する

1. GitHub Desktopを開き、GitHubアカウントへサインインします。
2. `File` → `Clone repository...`を選びます。
3. `GitHub.com`タブで`SYURURE/dhfr-mtx-redocking-benchmark`を選びます。
4. `Local path`は、たとえば`Documents\GitHub`のような分かりやすい場所を選びます。
5. `Clone`を押します。

これで、GitHubに現在登録されている内容の作業用コピーがPCに作られます。

### 3. 修正版の中身を作業用コピーへ上書きする

1. GitHub Desktopで`Repository` → `Show in Explorer`を選びます。
2. 表示された作業用コピーのフォルダは、そのまま開いておきます。
3. 別のExplorerで、手順1で展開した`dhfr-mtx-redocking-benchmark`フォルダを開きます。
4. 展開フォルダの**中身をすべて**選び、作業用コピーへコピーします。
5. Windowsから確認されたら、`ファイルを置き換える`を選びます。

外側の`dhfr-mtx-redocking-benchmark`フォルダごと入れるのではなく、その**中身**をコピーします。作業用コピーの最上位に`README.md`がある状態が正解です。

### 4. 変更内容をGitHubへ送る

1. GitHub Desktopへ戻り、左側の`Changes`に変更・追加ファイルが並ぶことを確認します。
2. `.github`、`data`、`environment`、`results`、`scripts`、`README.md`、`AI_REPRODUCIBILITY_REVIEW.md`が反映対象になっていることを確認します。
3. 左下の`Summary`へ次を入力します。

```text
Apply reproducibility fixes and add AI validation record
```

4. `Commit to main`を押します。
5. 画面上部の`Push origin`を押します。

`Commit`はPC内で変更をひとまとめにする操作、`Push origin`はその変更をGitHubへ送る操作です。両方を行って初めてGitHub画面へ反映されます。

### 5. GitHub上で自動検査を確認する

ブラウザでレポジトリを開き、次を確認します。

- トップ画面に`AI_REPRODUCIBILITY_REVIEW.md`がある
- README冒頭からAI検証記録へ移動できる
- 最新commitの右側に緑色のチェックが付く
- `Actions`タブの`Verify public package`で、`lightweight-verification`と`scientific-regression`が緑になる

通常の自動検査では、package整合性に加え、RDKitによる4DFR・1U72 RMSD、raw 60-run archiveからのrobustness CSV、raw GNINA入出力からの比較CSVを再計算します。SMINA単発ドッキングの完全再実行は、計算時間を抑えるため手動workflow `Reproduce core docking`に分離しています。

## ブラウザだけで更新する場合

GitHub Desktopを使わない場合は、レポジトリのトップ画面で`Add file` → `Upload files`を選び、展開フォルダの中身を複数回に分けてアップロードします。

注意点:

- ブラウザ版は一度に100ファイルまでなので、100件以下の複数回に分ける
- 各回で同名ファイルをアップロードし、変更をcommitする
- `.github`はWindowsで隠れて見えることがあるため、必ず別途確認する
- ブラウザアップロードでは`.gitattributes`が無視される場合があるため、GitHub Desktopを優先する
- ZIPそのものではなく、展開した中身をアップロードする
- 最後に`Actions`の2つの自動検査が緑になるまで確認する

## まだレポジトリを作っていない場合

GitHubのDashboardで`Create repository`を選び、次を入力します。

- Repository name: `dhfr-mtx-redocking-benchmark`
- Description: `Reproducible SMINA redocking, robustness analysis, and GNINA CNN rescoring of DHFR–methotrexate complexes.`
- Visibility: 最初の確認中は`Private`を推奨
- `Add a README file`: オフ
- `.gitignore`: None
- License: None

README、`.gitignore`、公開準備用ライセンス通知は、このパッケージにすでに入っています。作成後は、GitHub Desktopでその空レポジトリをcloneし、上記と同じ方法でパッケージの中身をコピーしてcommit・pushします。

## Publicへ切り替える前の最終確認

- GitHubプロフィールで公開してよいユーザー名・表示名になっている
- READMEと`AI_REPRODUCIBILITY_REVIEW.md`の説明に納得している
- AI検証が人間の査読、第三者認証、規制上のvalidationではないことを理解している
- 結果が教育用ベンチマークであり、薬効や結合自由エネルギーを証明しないことが明記されている
- APIキー、パスワード、秘密鍵、個人情報が含まれていない
- 再利用ライセンスをまだ決めていないことを理解している
- 最新commitとActionsが緑になっている

確認後、リポジトリの`Settings`からvisibilityを`Public`へ変更できます。

## 迷ったときの判断

- GitHubに変更が出ない: GitHub Desktopで開いている作業用コピーとは別の場所へコピーしている可能性があります。`Repository` → `Show in Explorer`から開いた場所へコピーします。
- `Commit to main`の後もGitHub画面が変わらない: `Push origin`がまだです。
- ZIPだけが見える: ZIPを展開せず登録しています。ZIPを削除し、展開後の中身を登録します。
- READMEが表示されない: `README.md`がGitHubの最上位ではなく、一段深いフォルダ内にあります。
- Actionsが赤い: 失敗したjobとstepのログを確認し、公開前に修正します。
- ライセンスを決めたい: 現在の`LICENSE.md`は「再利用許諾なし」です。MITなどへ変更する前に、コードや図の再利用範囲を決めます。
