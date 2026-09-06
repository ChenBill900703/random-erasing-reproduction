# Random Erasing Data Augmentation 核心復現報告

> 狀態：核心範圍已完成。此文件只列入已完成的正式 run；smoke test 與中止的校準 run 不計入統計。

## 範圍

- CIFAR-10 / ResNet-20 baseline：5 runs。
- 論文描述的 `paper_random` Random Erasing：5 runs。
- 2017 作者程式碼的 `author_constant` Random Erasing：5 runs。
- 每組同時報告 best 與 final test error，因論文未說明表 1 使用哪一種。
- 標準差同時報告 population 與 sample 版本，因論文未公開其慣例。

完整的證據分類、超參數與論文／程式碼差異見 `docs/reproduction_spec.md`。

## 已完成結果

### Baseline（5/5）

各 seed 的 test error（%）：

| Seed | Best | Final |
|---:|---:|---:|
| 1001 | 7.12 | 7.38 |
| 1002 | 6.81 | 7.01 |
| 1003 | 7.14 | 7.35 |
| 1004 | 7.03 | 7.22 |
| 1005 | 7.01 | 7.49 |

| 統計口徑 | 本次復現 mean ± population std | 本次復現 mean ± sample std | 論文表 1 | Mean 絕對差 |
|---|---:|---:|---:|---:|
| Best test error | 7.022 ± 0.117 | 7.022 ± 0.131 | 7.21 ± 0.17 | 0.188 pp |
| Final test error | 7.290 ± 0.164 | 7.290 ± 0.184 | 7.21 ± 0.17 | 0.080 pp |

目前 baseline 結果與論文數值接近；final 口徑的 mean 與 population std 尤其接近。不過，論文未公開 best-vs-final 與 std 公式，因此不能據此斷言論文採用 final 或 population std。

機器可讀聚合結果：`runs/cifar10_resnet20_baseline_aggregate.json`。

### Paper Random Erasing（5/5）

各 seed 的 test error（%）：

| Seed | Best | Final |
|---:|---:|---:|
| 1001 | 6.42 | 6.87 |
| 1002 | 6.72 | 7.23 |
| 1003 | 6.55 | 6.55 |
| 1004 | 6.94 | 7.18 |
| 1005 | 6.76 | 6.84 |

| 統計口徑 | 本次復現 mean ± population std | 本次復現 mean ± sample std | 論文表 1 | Mean 絕對差 |
|---|---:|---:|---:|---:|
| Best test error | 6.678 ± 0.179 | 6.678 ± 0.200 | 6.73 ± 0.09 | 0.052 pp |
| Final test error | 6.934 ± 0.248 | 6.934 ± 0.278 | 6.73 ± 0.09 | 0.204 pp |

以 best 口徑比較，Random Erasing 相對本次 baseline 改善 0.344 pp；論文表 1 的改善幅度是 0.48 pp。以 final 口徑比較，本次改善 0.356 pp。復現 mean 很接近論文，但 run-to-run 標準差較論文大；目前沒有證據可將差異歸因於單一因素。

機器可讀聚合結果：`runs/cifar10_resnet20_re_paper_aggregate.json`。

### Author-code Random Erasing（5/5）

各 seed 的 test error（%）：

| Seed | Best | Final |
|---:|---:|---:|
| 1001 | 6.70 | 6.73 |
| 1002 | 6.85 | 6.99 |
| 1003 | 6.83 | 7.18 |
| 1004 | 6.43 | 6.89 |
| 1005 | 6.91 | 6.98 |

| 統計口徑 | 本次復現 mean ± population std | 本次復現 mean ± sample std | 論文表 1 | Mean 絕對差 |
|---|---:|---:|---:|---:|
| Best test error | 6.744 ± 0.171 | 6.744 ± 0.192 | 6.73 ± 0.09 | 0.014 pp |
| Final test error | 6.954 ± 0.147 | 6.954 ± 0.164 | 6.73 ± 0.09 | 0.224 pp |

以 best 口徑比較，作者程式碼版相對本次 baseline 改善 0.278 pp；以 final 口徑比較則改善 0.336 pp。機器可讀聚合結果：`runs/cifar10_resnet20_re_author_code_aggregate.json`。

## 三組結果總覽

以下以 population std 為主要展示口徑；sample std 已完整保留於前述各表與 JSON。

| 實驗 | Best error | Final error | 對論文目標的 best mean 差 |
|---|---:|---:|---:|
| Baseline | 7.022 ± 0.117 | 7.290 ± 0.164 | −0.188 pp（目標 7.21） |
| Paper Random Erasing | 6.678 ± 0.179 | 6.934 ± 0.248 | −0.052 pp（目標 6.73） |
| Author-code Random Erasing | 6.744 ± 0.171 | 6.954 ± 0.147 | +0.014 pp（目標 6.73） |

論文版與作者程式碼版的 best mean 相差 0.066 pp，final mean 相差 0.020 pp；在本次五個 seed 的變異尺度下，不應把這個小差距解讀成其中一種填值方法必然較優。

## 表 1 擴充復現

### CIFAR-100 / ResNet-20（完整配對）

| 條件 | Seed 1001 | 1002 | 1003 | 1004 | 1005 | Best mean ± population std | Best mean ± sample std | 論文表 1 | Mean 絕對差 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 30.66 | 30.25 | 30.85 | 30.61 | 30.89 | 30.652 ± 0.228 | 30.652 ± 0.255 | 30.84 ± 0.19 | 0.188 pp |
| Paper Random Erasing | 30.29 | 29.36 | 29.85 | 30.14 | 29.74 | 29.876 ± 0.325 | 29.876 ± 0.363 | 29.97 ± 0.11 | 0.094 pp |
| Author-code Random Erasing | 29.89 | 29.77 | 29.88 | 30.06 | 30.61 | 30.042 ± 0.299 | 30.042 ± 0.334 | 29.97 ± 0.11（RE 參考） | 0.072 pp |

以 best test error 比較，本次論文版 Random Erasing 相對 baseline 改善 0.776 pp，作者程式碼版改善 0.610 pp；論文表 1 的改善幅度為 0.87 pp。論文版與作者版的 best mean 相差 0.166 pp，兩者都接近論文目標，但 run-to-run 標準差高於論文。Final error 的 baseline 為 31.718 ± 0.317、論文版為 30.346 ± 0.381、作者版為 30.728 ± 0.291（population std）；完整數值保存在對應 aggregate JSON。

### Fashion-MNIST / ResNet-20（完整配對）

| 條件 | Seed 1001 | 1002 | 1003 | 1004 | 1005 | Best mean ± population std | Best mean ± sample std | 論文表 1 | Mean 絕對差 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 4.83 | 4.85 | 4.69 | 4.79 | 4.76 | 4.784 ± 0.056 | 4.784 ± 0.063 | 4.39 ± 0.08 | 0.394 pp |
| Paper Random Erasing | 4.60 | 4.68 | 4.50 | 4.58 | 4.57 | 4.586 ± 0.058 | 4.586 ± 0.065 | 4.02 ± 0.07 | 0.566 pp |
| Author-code Random Erasing | 4.52 | 4.56 | 4.67 | 4.66 | 4.65 | 4.612 ± 0.060 | 4.612 ± 0.068 | 4.02 ± 0.07（RE 參考） | 0.592 pp |

以 best test error 比較，本次論文版 Random Erasing 相對 baseline 改善 0.198 pp，作者程式碼版改善 0.172 pp；論文表 1 的改善幅度為 0.37 pp。論文版與作者版相差 0.026 pp，改善方向均成功重現，但所有本次絕對錯誤率都高於論文，不能稱為數值復現。Final error 的 baseline 為 5.042 ± 0.134、論文版為 4.812 ± 0.088、作者版為 4.784 ± 0.069（population std）。作者倉庫後續說明曾警告新版 Fashion-MNIST 的 baseline 與 RE 表現會略低於論文，因此資料版本是後續調查項，而不是用來事後修改本次結果的理由。

### CIFAR-10 / ResNet-32（完整配對）

| 條件 | Seed 1001 | 1002 | 1003 | 1004 | 1005 | Best mean ± population std | Best mean ± sample std | 論文表 1 | Mean 絕對差 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 6.35 | 6.32 | 6.16 | 6.11 | 6.40 | 6.268 ± 0.113 | 6.268 ± 0.126 | 6.41 ± 0.06 | 0.142 pp |
| Paper Random Erasing | 5.68 | 5.75 | 5.55 | 5.63 | 5.90 | 5.702 ± 0.119 | 5.702 ± 0.133 | 5.66 ± 0.10 | 0.042 pp |

以 best test error 比較，本次論文版 Random Erasing 相對 baseline 改善 0.566 pp；論文表 1 的改善幅度為 0.75 pp。Final error 的 baseline 為 6.386 ± 0.061、Random Erasing 為 5.908 ± 0.111（population std）。

### CIFAR-100 / ResNet-32（完整配對）

| 條件 | Seed 1001 | 1002 | 1003 | 1004 | 1005 | Best mean ± population std | Best mean ± sample std | 論文表 1 | Mean 絕對差 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 28.90 | 29.69 | 29.02 | 28.36 | 29.19 | 29.032 ± 0.431 | 29.032 ± 0.481 | 28.50 ± 0.37 | 0.532 pp |
| Paper Random Erasing | 27.35 | 27.67 | 27.03 | 27.19 | 27.87 | 27.422 ± 0.308 | 27.422 ± 0.345 | 27.18 ± 0.32 | 0.242 pp |

以 best test error 比較，本次論文版 Random Erasing 相對 baseline 改善 1.610 pp；論文表 1 的改善幅度為 1.32 pp。改善方向與幅度均重現，但 baseline 與 Random Erasing 的 mean 分別比論文高 0.532 pp 與 0.242 pp。Final error 的 baseline 為 30.160 ± 0.381、Random Erasing 為 28.272 ± 0.170（population std）。

### Fashion-MNIST / ResNet-32（完整配對）

| 條件 | Seed 1001 | 1002 | 1003 | 1004 | 1005 | Best mean ± population std | Best mean ± sample std | 論文表 1 | Mean 絕對差 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 4.80 | 4.78 | 4.90 | 4.72 | 4.88 | 4.816 ± 0.066 | 4.816 ± 0.074 | 4.16 ± 0.13 | 0.656 pp |
| Paper Random Erasing | 4.51 | 4.68 | 4.48 | 4.53 | 4.66 | 4.572 ± 0.082 | 4.572 ± 0.091 | 3.80 ± 0.05 | 0.772 pp |

以 best test error 比較，本次論文版 Random Erasing 相對 baseline 改善 0.244 pp；論文表 1 的改善幅度為 0.36 pp。改善方向成功重現，但兩個絕對錯誤率仍高於論文，不能稱為數值復現。Final error 的 baseline 為 5.110 ± 0.130、Random Erasing 為 4.766 ± 0.169（population std）。

## 論文與作者程式碼不一致分析

1. **擦除值不同。** 論文 Algorithm 1 使用 `Rand(0,255)`，正文及表 2 將預設方法描述為擦除區域內每個像素獨立隨機取值（RE-R）。2017 作者程式碼則在整個矩形內，每個通道填入固定常數 `[0.4914, 0.4822, 0.4465]`。
2. **操作順序不同。** 本專案的論文版在 `[0,1]` tensor 上逐元素取均勻亂數，再執行 Normalize；作者版依原始 pipeline 在 Normalize 之後寫入上述固定常數。因此作者版常數是正規化後 tensor 的值，不能解讀成「填入資料集平均後會得到零」。
3. **公開資訊不足。** 論文只說結果為五次的 mean ± std，未公開 seeds、std 公式，也未明說表 1 採用最佳 epoch 或最後 epoch。本專案固定 seeds `[1001,1002,1003,1004,1005]`，同時保留 best/final 與兩種 std，避免倒推或挑選口徑迎合目標。
4. **現代環境差異。** 本次使用 Python 3.12、PyTorch 2.12.1、torchvision 0.27.1 與 CUDA 12.6；作者 2017 程式含 Python 2 整數除法語意。本專案完成 ResNet-20/32 的等價現代移植，並以各資料集的輸出 shape 與參數量測試鎖定。

## 可重跑性與產物

- 十五份已完成實驗的完整設定位於 `configs/`；五個明示 seeds、300 epochs、optimizer、scheduler、資料增強與 Random Erasing 參數均寫在設定檔。
- `scripts/setup_windows.ps1` 建立固定版本環境；`scripts/start_full_batch.ps1`、`scripts/start_phase2_batch.ps1` 與 `scripts/start_author_extension_batch.ps1` 分別啟動可重入的核心、表 1 擴充及作者程式碼延伸批次。
- 每個正式 run 在 `runs/<experiment>_seed<seed>/` 保存 `metadata.json`、300-epoch `metrics.csv`、`best.pt` 與 `summary.json`。
- `runs/batch_stdout.log`、`runs/batch_stderr.log` 與 `runs/batch_status.json` 保存整批紀錄及完成狀態。
- 作者倉庫固定在 `third_party/Random-Erasing` 的 commit `ddae4ed1eeaa5cf234e6deef9c9a2531464516dd`。
- 第一階段正式批次由 2026-09-02 14:34:07 UTC 跑至 2026-09-02 22:41:09 UTC，約 8 小時 7 分；第二階段 50 runs 由 2026-09-03 04:30:16 UTC 跑至 2026-09-04 17:30:26 UTC，約 37 小時；作者程式碼延伸 10 runs 由 2026-09-04 17:54:07 UTC 跑至 2026-09-04 23:38:40 UTC，約 5 小時 45 分。
- 最終驗收確認十五組、共 75 個正式 run 各有 300 筆 epoch metrics 與四項必要產物，15 份 aggregate 各含五個值，三個批次狀態均為 completed；完整檢查為 0 issues，測試結果為 6 passed。第二階段 stderr 僅含資料下載進度，其餘批次 stderr 為空，沒有例外。

## 結論

本次核心與表 1 擴充復現均支持論文的主要結論：在已完成的五個資料集／架構配對中，加入 Random Erasing 後的五次平均 best test error 都低於相同訓練設定的 baseline。CIFAR 結果較接近論文；Fashion-MNIST 雖重現改善方向，但絕對數值仍有明顯差距。論文版與作者程式碼版在填值與操作順序上的衝突不因結果接近而消失，兩者必須繼續分開命名與報告。
