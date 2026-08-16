# Limitations and claim boundaries

## Receptor preparation

- 4DFR Chain Aには欠損側鎖原子やalternate locationに関する注意がある。
- 受容体のプロトン化、部分電荷、欠損原子、結晶水を体系的に比較していない。
- 1U72ではNADPHをPDB表現のまま保持し、厳密な化学状態を検証していない。
- 受容体は基本的に剛体として扱った。

## Ligand preparation

- MTXはOpen Babelによる単一の教育用pH 7.4処理を用いた。
- 複数のプロトン化状態、互変異性体、部分電荷モデルを比較していない。
- 結合前の配座集団と配座歪みエネルギーを評価していない。

## Scoring and RMSD

- SMINA affinityは実測結合自由エネルギーではない。
- RMSD ≤ 2 Åはredockingの教育的な目安で、結合能や薬効を保証しない。
- 同一標的・同一リガンド内の相関は、独立な化合物間の予測性能ではない。

## Comparisons

- 1U72と4DFRは生物種、補因子、構造、前処理、seed、exhaustiveness、modesが異なる。
- したがって、今回の結果だけでヒトと*E. coli*の本質的なドッキング容易性を比較できない。
- 公平な種差比較には、同一プロトコルと複数seedによる再計算が必要。

## GNINA proof of concept

- GNINA再スコアリングは1 PDB、1 ligand、1 run、9 posesの結果。
- CNNがこの1 runを救済したことは示せるが、一般的な優越性は示せない。
- 次段階では複数seedの全ポーズへ展開し、run単位のTop 1救済率を推定する必要がある。

## Computational reproducibility

- 4DFRと1U72の保存済みSMINA SDFは、Linux x86-64/WSL2、固定入力、固定seed、CPU 2 threads、公開Conda buildでSHA-256完全一致を確認した。
- 別OS、別CPU architecture、別compiler/build、別thread数でもビット単位で一致するとは限らない。
- GNINA POCは入力と全raw出力を保存しているが、異なるBLAS/CUDA/cuDNN/CPU buildで再採点した場合のテキスト完全一致は保証しない。
- PNGはmatplotlibやfont buildでバイト列が変わるため、画像hashではなく元CSV、軸、ラベル、主要統計を再現性の中心とする。

## Appropriate claims

このプロジェクトから主張できるのは次の範囲です。

- 保存した条件下でSMINAがnative-like poseを生成した。
- 4DFR robustness studyではTop N探索成功とTop 1順位付け失敗を分離できた。
- 単一4DFR runではGNINA CNN再スコアリングがRMSD最良ポーズを1位へ選んだ。

次は主張できません。

- 新しい薬候補を発見した。
- ドッキングスコアから実測活性や選択性を予測できた。
- GNINAが常にSMINAより優れる。
- ヒトDHFRの方が*E. coli* DHFRより本質的にドッキングしやすい。
