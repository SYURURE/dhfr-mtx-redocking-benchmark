# GitHub登録手順（初回向け）

このパッケージは、公開用に整理・検査したDHFR–MTX再ドッキングのポートフォリオです。元の巨大な作業フォルダではなく、このフォルダだけをGitHubへ登録します。

## 1. ZIPを展開する

`dhfr-mtx-redocking-benchmark_github-ready_20260816.zip`を右クリックし、Windowsの「すべて展開」を選びます。

ZIPそのものをGitHubへアップロードするのではなく、展開後の`dhfr-mtx-redocking-benchmark`フォルダの**中身**を登録します。GitHubの最上位に`README.md`が見える状態が正解です。

## 2. 空のリポジトリを作る

GitHubのDashboardで「Create repository」を選び、次を入力します。

- Repository name: `dhfr-mtx-redocking-benchmark`
- Description: `Reproducible SMINA redocking, robustness analysis, and GNINA CNN rescoring of DHFR–methotrexate complexes.`
- Visibility: 最初の確認中は`Private`を推奨。公開内容を確認した後に`Public`へ変更できます。
- `Add a README file`: オフ
- `.gitignore`: None
- License: None

README、`.gitignore`、公開準備用ライセンス通知は、このパッケージにすでに入っています。

## 3. 展開したファイルをアップロードする

空のリポジトリ画面で「uploading an existing file」を選びます。展開した`dhfr-mtx-redocking-benchmark`フォルダを開き、その**中にあるファイルとフォルダをすべて**アップロード欄へドラッグします。

コミットメッセージの例:

```text
Add DHFR-MTX redocking benchmark portfolio
```

「Commit changes」を選び、登録を完了します。

## 4. 登録後に確認する

リポジトリのトップ画面で、次を確認します。

- `README.md`の本文と図が表示される
- `environment/`、`scripts/`、`results/`、`docs/`が見える
- ZIP、実行ファイル、秘密鍵、APIキー、個人PCの絶対パスが含まれていない
- 「Actions」タブの`Verify public package`が緑色のチェックで終了する

Actionsが緑になれば、保存済みSDFとCSVの主要値、画像、Markdownリンク、一般的な個人パス・秘密情報パターン、およびPython/Bash構文の検査が通っています。これはSMINA、GNINA、RDKitによる科学計算そのものの再実行ではありません。

## 5. Publicへ切り替える前の最終確認

次を目視してから公開します。

- GitHubプロフィールで公開してよいユーザー名・表示名になっている
- `README.md`の説明とAI支援の記載に納得している
- 結果が教育用ベンチマークであり、薬効や結合自由エネルギーを証明しないことが明記されている
- 再利用ライセンスをまだ決めていないことを理解している

公開する場合は、リポジトリの「Settings」からvisibilityを`Public`へ変更します。公開後はURLをポートフォリオへ掲載できます。

## 迷ったときの判断

- ZIPだけが見える: ZIPを展開せずアップロードしています。展開後の中身を登録し直します。
- READMEが表示されない: `README.md`がGitHubの最上位ではなく、一段深いフォルダ内に入っています。
- Actionsが赤い: 失敗したステップ名とログを確認し、公開前に修正します。
- ライセンスを決めたい: 現在の`LICENSE.md`は「再利用許諾なし」です。MITなどへ変更する前に、コードや図の再利用範囲を決めます。
