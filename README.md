# Random Erasing Data Augmentation：可重跑復現專案

> 以現代 PyTorch 重現 Zhong 等人的 **Random Erasing Data Augmentation**，完整保留設定、75 次正式訓練、逐 epoch 紀錄、模型權重、統計報告與教授簡報。

![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.12.1-EE4C2C?logo=pytorch&logoColor=white)
![Runs](https://img.shields.io/badge/formal%20runs-75%2F75-success)
![Tests](https://img.shields.io/badge/tests-6%20passed-success)

## 一句話結論

在本專案完成的 **6 組 baseline／論文版 Random Erasing 配對**中，Random Erasing 的五次平均測試錯誤率全部下降，重現了論文的核心主張。CIFAR 數據很接近論文；Fashion-MNIST 也重現改善方向，但絕對錯誤率仍明顯高於論文，不能宣稱完全數值復現。

## 專案成果總覽

| 項目 | 完成結果 |
|---|---:|
| 正式訓練 | 75 runs，全部完成 |
| 實驗群組 | 15 組，每組 5 seeds |
| 每次訓練長度 | 300 epochs |
| 逐 epoch 紀錄 | 22,500 筆 |
| Baseline／論文版 RE 配對 | 6 / 6 組均改善 |
| 平均改善幅度 | 論文 0.692 pp；本次 0.623 pp |
| 論文改善幅度重現比例 | 約 90.1% |
| CIFAR 絕對數值 | 8 個 mean 中 7 個與論文相差不超過 0.25 pp |
| Fashion-MNIST 絕對數值 | 平均與論文相差 0.597 pp，仍需資料版本調查 |
| 完整性檢查 | 0 issues |
| 自動測試 | 6 passed |

`pp` 是 percentage point（百分點），不是相對百分比。例如錯誤率由 7.21% 降至 6.73%，改善是 0.48 pp。

## Random Erasing 在做什麼？

Random Erasing 是一種不需要額外學習參數的資料增強方法。訓練時，以機率 `p` 在影像中隨機選一個矩形，將矩形內的像素替換掉，讓模型在訓練期間看到不同程度的遮擋，降低只記住局部特徵的風險。

本次分類實驗沿用論文明示參數：

| 參數 | 數值 | 白話解釋 |
|---|---:|---|
| `p` | 0.5 | 每張訓練影像有 50% 機率擦除 |
| `s_l` | 0.02 | 最小擦除面積為影像的 2% |
| `s_h` | 0.4 | 最大擦除面積為影像的 40% |
| 長寬比 | 0.3–3.3333 | 允許扁長或接近方形的遮擋區域 |
| 嘗試次數 | 最多 100 次 | 找不到合法矩形就保留原影像 |

## 最重要的復現結果

以下採用 **5 runs 的 best test error，mean ± population std**。論文沒有說明使用最佳 epoch 或最後 epoch，也沒有公開 std 公式，因此本專案同時保存 best、final、population std 與 sample std；此表只選一個固定口徑方便閱讀。

| 資料集／模型 | 論文 Baseline | 本次 Baseline | 論文 RE | 本次論文版 RE | 論文改善 | 本次改善 |
|---|---:|---:|---:|---:|---:|---:|
| CIFAR-10 / ResNet-20 | 7.21 ± 0.17 | **7.022 ± 0.117** | 6.73 ± 0.09 | **6.678 ± 0.179** | 0.480 | 0.344 |
| CIFAR-100 / ResNet-20 | 30.84 ± 0.19 | **30.652 ± 0.228** | 29.97 ± 0.11 | **29.876 ± 0.325** | 0.870 | 0.776 |
| Fashion-MNIST / ResNet-20 | 4.39 ± 0.08 | **4.784 ± 0.056** | 4.02 ± 0.07 | **4.586 ± 0.058** | 0.370 | 0.198 |
| CIFAR-10 / ResNet-32 | 6.41 ± 0.06 | **6.268 ± 0.113** | 5.66 ± 0.10 | **5.702 ± 0.119** | 0.750 | 0.566 |
| CIFAR-100 / ResNet-32 | 28.50 ± 0.37 | **29.032 ± 0.431** | 27.18 ± 0.32 | **27.422 ± 0.308** | 1.320 | 1.610 |
| Fashion-MNIST / ResNet-32 | 4.16 ± 0.13 | **4.816 ± 0.066** | 3.80 ± 0.05 | **4.572 ± 0.082** | 0.360 | 0.244 |

完整的每個 seed、best/final、兩種 std 與差距分析請看 [核心復現報告](docs/reproduction_report.md)，機器可讀總表在 [reproduction_summary.csv](data_reference/reproduction_summary.csv)。

### 怎麼解讀？

- **核心主旨有重現：** 6 組配對全部是 RE 優於相同設定的 baseline。
- **CIFAR 接近原文：** 8 個 baseline/RE mean 的平均絕對差為 0.185 pp，其中 7 個在 0.25 pp 內。
- **Fashion-MNIST 尚未數值對齊：** 4 個 mean 的差距為 0.394–0.772 pp。作者 README 也提醒新版 Fashion-MNIST 的結果會比論文略差，但這只能視為合理調查方向，不能拿來消除本次差距。
- **不能只挑好看的口徑：** 論文未交代 best 或 final，本專案兩者都保存並明示比較口徑。

## 論文版與作者程式碼版為什麼要分開？

論文文字與 2017 年作者程式碼對「擦除後填什麼值」的做法不同。本專案沒有把其中一個偷偷當成另一個，而是各自實作、分開命名、分開跑。

| 比較項目 | 論文描述版 `paper_random` | 作者程式碼版 `author_constant` |
|---|---|---|
| 擦除內容 | 矩形內每個像素獨立取隨機值 | 整個矩形按通道填固定常數 |
| 操作位置 | `[0,1]` tensor 上擦除，再 Normalize | Normalize 後填值 |
| 目的 | 對應論文 Algorithm 1 與 RE-R 描述 | 對應 2017 `transforms.py` 行為 |
| 報告方式 | 與論文表 1 正式比較 | 當成程式碼差異實驗，不冒稱論文版 |

作者程式碼版 ResNet-20 的五次平均 best error：

| 資料集 | 論文版 RE | 作者程式碼版 | 兩者差距 |
|---|---:|---:|---:|
| CIFAR-10 | 6.678 ± 0.179 | 6.744 ± 0.171 | 0.066 pp |
| CIFAR-100 | 29.876 ± 0.325 | 30.042 ± 0.299 | 0.166 pp |
| Fashion-MNIST | 4.586 ± 0.058 | 4.612 ± 0.060 | 0.026 pp |

三個資料集都是論文版略低，但差距不大；只有各 5 runs，不能據此斷言某種填值法必然較好。

## 實驗範圍

已完成：

- CIFAR-10、CIFAR-100、Fashion-MNIST。
- ResNet-20、ResNet-32。
- 6 組 baseline／論文版 Random Erasing 配對，各 5 runs。
- ResNet-20 在三個資料集的作者程式碼版延伸，各 5 runs。
- 共 15 個實驗群組、75 個正式 runs。

尚未涵蓋：

- 論文表 1 的 ResNet-44/56/110、PreAct ResNet、WRN、ResNeXt。
- 表 2–4 與圖 4–5 的消融及遮擋實驗。
- PASCAL VOC 物件偵測，以及 Market-1501、DukeMTMC-reID、CUHK03 人員再識別。

因此，本專案是對**論文核心影像分類主張的部分復現**，不是整篇論文所有表格的完整重製。

## 訓練設定

| 類別 | 設定 |
|---|---|
| Epochs | 300 |
| Seeds | 1001、1002、1003、1004、1005 |
| Optimizer | SGD，momentum 0.9，weight decay 5e-4 |
| Learning rate | 0.1；第 150、225 epoch 各乘 0.1 |
| Batch size | train 128；test 100 |
| 一般增強 | padding 4、random crop、horizontal flip |
| 執行模式 | deterministic |
| 實驗環境 | Python 3.12、PyTorch 2.12.1+cu126、torchvision 0.27.1+cu126 |
| GPU | NVIDIA GeForce RTX 3070 Ti |

論文沒有公開五個 seeds，本專案的 seeds 是為了可重跑而新增的控制變數，不能稱為「論文原始 seeds」。各組完整設定都在 [`configs/`](configs/)。

## 快速開始（Windows / PowerShell）

### 1. 建立環境

先安裝 Python 3.12 與 NVIDIA 驅動，再執行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
& .\scripts\setup_windows.ps1
```

若電腦沒有 `py` launcher，可以指定 Python：

```powershell
& .\scripts\setup_windows.ps1 -PythonCommand "C:\path\to\python.exe"
```

### 2. 驗證程式

```powershell
& .\.venv\Scripts\python.exe -m pytest
```

### 3. 先做 1-epoch smoke test

```powershell
& .\.venv\Scripts\python.exe -m random_erasing_repro.train `
  --config configs/cifar10_resnet20_re_paper.toml `
  --seed 1001 `
  --smoke
```

Smoke test 只確認資料、模型與訓練流程能跑，**不能當成論文復現結果**。

### 4. 跑單次正式實驗

```powershell
# Baseline
& .\.venv\Scripts\python.exe -m random_erasing_repro.train `
  --config configs/cifar10_resnet20_baseline.toml `
  --seed 1001

# 論文描述版 Random Erasing
& .\.venv\Scripts\python.exe -m random_erasing_repro.train `
  --config configs/cifar10_resnet20_re_paper.toml `
  --seed 1001
```

### 5. 一次跑五個 seeds

```powershell
& .\scripts\run_five.ps1 -Config configs/cifar10_resnet20_baseline.toml
```

批次入口：

| 腳本 | 工作內容 |
|---|---|
| `start_full_batch.ps1` | CIFAR-10 / ResNet-20：baseline、論文版、作者版 |
| `start_phase2_batch.ps1` | 三資料集、ResNet-20/32 的 baseline／論文版擴充 |
| `start_author_extension_batch.ps1` | CIFAR-100、Fashion-MNIST / ResNet-20 作者版 |

## 結果檔案怎麼看？

每個正式 run 位於 `runs/<experiment>_seed<seed>/`：

| 檔案 | 內容 |
|---|---|
| `metadata.json` | 完整 config、seed、套件版本、GPU 與執行環境 |
| `metrics.csv` | 300 個 epoch 的 train/test loss、accuracy、learning rate |
| `summary.json` | best/final accuracy、error 與執行時間 |
| `best.pt` | 該 run 的最佳模型權重 |

每個實驗群組另有 `runs/<experiment>_aggregate.json`，保存 5 runs 的個別值、mean、population std 與 sample std。三個批次的狀態與 console log 也保留在 `runs/` 根目錄。

## 專案結構

```text
configs/          15 組已完成實驗的 TOML 設定
data_reference/   論文表 1 與本次復現的機器可讀總表
docs/             規格、完整報告、防幻覺提示詞
output/           最終教授版 PPTX 與 PDF
runs/             75 次正式訓練、15 份聚合統計、批次紀錄
scripts/          環境建立與批次執行入口
src/              Random Erasing、ResNet、訓練與彙整程式
tests/            Random Erasing 與模型結構測試
```

未上傳的內容包括 `.venv/`、下載後的資料集、smoke runs、中止的校準 run、暫存檔與原始論文 PDF。這些不是正式結果，或可由公開來源重新下載；論文請直接由 [arXiv:1708.04896](https://arxiv.org/abs/1708.04896) 取得。

## 報告與簡報

- [完整復現報告](docs/reproduction_report.md)：每個 seed、mean ± std、best/final 與差異分析。
- [復現規格與證據帳本](docs/reproduction_spec.md)：哪些資訊來自論文、作者程式碼、本專案或仍未知。
- [防幻覺提示詞](docs/prompts.md)：後續使用 AI 時，要求區分來源並禁止補造論文未提供的設定。
- [教授版 PowerPoint](output/pptx/random_erasing_reproduction_professor_v3.pptx)
- [教授版 PDF](output/pdf/random_erasing_reproduction_professor_v3.pdf)

## 可重跑性與品質控制

- 每個正式結果都標記 `is_paper_result=false`，避免把本次結果誤認為論文原始數字。
- 所有正式群組固定五個明示 seeds；不靠挑 seed 迎合論文。
- 完整性稽核確認 75 個正式 run 都有四項必要產物，且每份 `metrics.csv` 都有 300 筆 epoch。
- 15 份 aggregate JSON 都含五個結果；三個批次狀態皆為 `completed`。
- 自動測試共 6 項，涵蓋擦除行為、輸出 shape 與 ResNet 參數量。
- 正式 checkpoint 共約 109 MB；最大單檔約 1.96 MB，直接使用一般 Git 保存，不依賴 Git LFS。

## 已知限制

1. 本次使用 2026 年現代軟體環境，不是 2017 年原始 Python/PyTorch/CUDA 組合。
2. 論文沒有公開 seeds、std 公式及 best-vs-final 口徑，因此無法逐位元或逐 run 對齊。
3. GPU 與框架版本差異可能造成小幅非確定性；目前沒有證據能把差距歸因於單一因素。
4. Fashion-MNIST 的絕對數值尚未重現，應優先調查資料版本與歷史 preprocessing，而不是修改目標或挑選結果。
5. 第三方作者倉庫沒有直接納入本 Repo；本專案記錄其固定 commit，現代移植程式位於 `src/`，上游程式與授權請以作者 Repo 為準。

## 原始來源與引用

- 論文：[Random Erasing Data Augmentation（arXiv:1708.04896）](https://arxiv.org/abs/1708.04896)
- 作者程式碼：[zhunzhong07/Random-Erasing](https://github.com/zhunzhong07/Random-Erasing)
- 本專案比對的歷史 commit：`ddae4ed1eeaa5cf234e6deef9c9a2531464516dd`

```bibtex
@inproceedings{zhong2020random,
  title={Random Erasing Data Augmentation},
  author={Zhong, Zhun and Zheng, Liang and Kang, Guoliang and Li, Shaozi and Yang, Yi},
  booktitle={Proceedings of the AAAI Conference on Artificial Intelligence},
  year={2020}
}
```

## 授權說明

上游作者倉庫目前標示為 Apache-2.0；本 Repo 未另外加入專案授權。論文、資料集與第三方程式的權利仍屬各自作者或發布者。
