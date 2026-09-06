# 防幻覺復現提示詞

以下提示詞可直接交給後續 AI／Coding Agent。它們要求先查證再動手，並把不知道的地方明示為不知道。

## 0. 每一輪都要附上的主提示詞

```text
你正在協助復現論文 Random Erasing Data Augmentation（arXiv:1708.04896v2）。

證據優先級：
1. 本地原始 PDF：1708.04896v2.pdf。
2. 作者公開倉庫在論文 v2 前的 commit：ddae4ed1eeaa5cf234e6deef9c9a2531464516dd。
3. 被論文直接引用的資料集、模型或評估 protocol 原始來源。
4. 本專案 docs/reproduction_spec.md。

硬性規則：
- 不得把推測、現代套件預設或自己的常識寫成論文設定。
- 每一個數值都標記來源為 [PAPER]、[AUTHOR_CODE]、[PROJECT] 或 [UNKNOWN]。
- 若 PDF 與作者程式碼衝突，並列兩者，不得自行選一個後宣稱是唯一真相。
- 沒有來源時寫 [UNKNOWN]，說明需要哪個證據才能解決。
- 不得把 paper target 複製成新實驗結果；新結果必須由實際 log 計算。
- 煙霧測試、單次 run、五次正式實驗必須清楚區分。
- 執行前先輸出將使用的 config、seed、資料版本、程式 commit 與軟硬體版本。
- 改碼後執行測試；回報實際命令、exit code、輸出路徑與任何失敗。
```

## 1. 論文事實稽核提示詞

```text
先不要寫程式。逐頁檢查 1708.04896v2.pdf 中與目前實驗相關的段落、公式、表格標題、註腳與樣本數。輸出一張證據表：欄位為「主張、精確值、PDF 頁面/表格、證據標籤、是否仍有歧義」。只收錄文件明示內容；看不清的公式要用頁面影像核對，不可依 OCR 猜測。再對照作者 commit ddae4ed，將所有衝突單列。
```

## 2. 實作檢查提示詞

```text
只處理 CIFAR-10 / ResNet-20 的第一階段。閱讀 configs、src、tests 與作者 commit ddae4ed。逐項核對：資料切分、crop/flip/ToTensor/RandomErasing/Normalize 的順序、RE 幾何分布、填充值、模型層數與初始化、SGD、learning-rate milestones、評估指標。不要改 paper target。若需要修改程式，先指出它違反哪一條 [PAPER] 或 [AUTHOR_CODE] 證據，再做最小修正並跑測試。
```

## 3. 煙霧測試提示詞

```text
使用 --smoke 與合成資料驗證 baseline、paper_random、author_constant 三條管線各能完成 1 epoch。這一步只驗證：shape、forward/backward、checkpoint、metrics.csv、metadata.json、summary.json。不得討論是否重現論文準確率。若 GPU 不可用，可使用 CPU；完整記錄環境與命令。
```

## 4. 正式 5-run 提示詞

```text
在煙霧測試全部通過後，依 configs 中的 1001–1005 五個 [PROJECT] seeds 依序執行 CIFAR-10 / ResNet-20 baseline 與 paper_random。不得平行塞滿同一張 GPU。每次完成後驗證 log 與 checkpoint，再開始下一次。最後從實際 summary.json 計算 mean、population std、sample std，與論文 target 7.21±0.17、6.73±0.09 比較並報 percentage-point 差。明示這些 seeds 不是論文原始 seeds。
```

## 5. 差異診斷提示詞

```text
若五次結果與論文不同，不要調 seed 或改 target。按順序稽核：資料檔與版本、train/test split、增強順序、擦除填充值模式、RE 取樣分布、ResNet-20 實作與初始化、batch size、optimizer、LR scheduler epoch 邊界、best-vs-final metric、PyTorch/CUDA/cuDNN 非確定性。每個假說都要附可驗證測試；沒有證據就標 [UNKNOWN]。
```

