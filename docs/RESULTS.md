# Results

## 4DFR exploratory redocking

| Pose | SMINA affinity (kcal/mol) | RMSD (Å) | Native-like at 2 Å |
|---:|---:|---:|:---:|
| 1 | −9.3 | 6.100 | No |
| 2 | −9.1 | 5.708 | No |
| 3 | −8.9 | 1.516 | Yes |
| 4 | −8.7 | 2.231 | No |
| 5 | −8.5 | 3.022 | No |

SMINAはnative-likeなPose 3を候補内へ生成しましたが、Pose 1としては選択しませんでした。

## Human 1U72 redocking

| Pose | SMINA affinity (kcal/mol) | RMSD (Å) | Native-like at 2 Å |
|---:|---:|---:|:---:|
| 1 | −11.5 | 1.092 | Yes |
| 2 | −11.3 | 1.158 | Yes |
| 3 | −10.5 | 2.303 | No |
| 4 | −9.9 | 1.853 | Yes |
| 5 | −9.7 | 2.508 | No |
| 6 | −9.4 | 9.728 | No |
| 7 | −9.3 | 3.377 | No |
| 8 | −9.0 | 9.189 | No |
| 9 | −8.7 | 9.388 | No |

Pose 1はスコア1位と対称性考慮RMSD最小が一致しました。RMSDは4通りの等価原子mappingから最小値を採用しています。ただし、4DFRとの条件差があるため種差の結論には使いません。

## 4DFR robustness analysis

| Exhaustiveness | Runs | Top 1 | Top N | Pose 1 RMSD (Å) | Best RMSD (Å) | Mean time (s) |
|---:|---:|---:|---:|---:|---:|---:|
| 8 | 20 | 0.0% | 100.0% | 6.000 ± 0.038 | 1.482 ± 0.192 | 34.65 ± 0.75 |
| 16 | 20 | 0.0% | 100.0% | 5.987 ± 0.026 | 1.498 ± 0.128 | 68.10 ± 0.91 |
| 32 | 20 | 0.0% | 100.0% | 5.984 ± 0.018 | 1.525 ± 0.168 | 134.80 ± 1.24 |

全60 runsでnative-like poseが候補内に存在しましたが、Top 1には一度もなりませんでした。Exhaustiveness 32は8の約3.89倍の時間を要し、Top 1改善はありませんでした。

### Best pose rank

| Rank | Runs | Share |
|---:|---:|---:|
| 2 | 25 | 41.7% |
| 3 | 17 | 28.3% |
| 4 | 12 | 20.0% |
| 5 | 3 | 5.0% |
| 6 | 1 | 1.7% |
| 7 | 1 | 1.7% |
| 8 | 1 | 1.7% |

## GNINA rescoring proof of concept

対象runでは、SMINA Pose 1がRMSD 6.0785 Å、Pose 2が1.4219 Åでした。

| Ranking method | Top pose | Top RMSD (Å) | Native-like |
|---|---:|---:|:---:|
| SMINA affinity | 1 | 6.079 | No |
| GNINA empirical score | 1 | 6.079 | No |
| GNINA CNNscore | 2 | 1.422 | Yes |
| GNINA CNNaffinity | 2 | 1.422 | Yes |

- Pose 2 CNNscore: 0.9343
- Pose 2 CNNaffinity: 6.9280
- CNNscore–RMSD Spearman ρ: −0.8167（n=9）
- CNNaffinity–RMSD Spearman ρ: −0.7333（n=9）

GNINA CNNはこの1 runでnative-like poseを1位へ救済しました。9ポーズは同一run内の関連候補であり、相関とp値は記述的な補助結果として扱います。
