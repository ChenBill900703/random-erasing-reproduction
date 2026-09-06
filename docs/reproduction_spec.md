# 復現規格與證據帳本

## 證據標籤

- **[PAPER]**：直接來自本地 `1708.04896v2.pdf`，並以頁面渲染核對。
- **[AUTHOR_CODE]**：直接來自作者公開倉庫。
- **[PROJECT]**：本專案為可執行、可追蹤或現代相容性而做的明示選擇。
- **[UNKNOWN]**：論文與作者程式碼都沒有足夠資訊；禁止自行補成論文事實。

## 來源鎖定

- **[PAPER]** arXiv:1708.04896v2，PDF 共 10 頁，檔案日期 2017-11-17。
- **[AUTHOR_CODE]** `https://github.com/zhunzhong07/Random-Erasing`。
- **[AUTHOR_CODE]** 論文 v2 發布前可見的程式 commit：`ddae4ed1eeaa5cf234e6deef9c9a2531464516dd`（2017-09-25）。本地比對用 checkout 固定在此 commit；GitHub Repo 只記錄 commit 與現代移植，不重複納入上游 checkout。
- **[AUTHOR_CODE]** 此歷史版本使用 Python 2 式整數除法語意（例如 `(depth-2)/6`），不能原封不動在現代 Python 3 執行；本專案已對 ResNet-20/32 做等價現代移植，並以輸出 shape 與參數數量測試鎖定。
- **[PROJECT]** 現代環境固定為 Python 3.12、PyTorch 2.12.1、torchvision 0.27.1、CUDA 12.6 wheel。這不是 2017 原始環境。

## 方法

- **[PAPER]** 對每張訓練影像，以機率 `p` 做 Random Erasing，否則保持不變。
- **[PAPER]** 影像面積 `S=W×H`；擦除面積 `S_e ~ Uniform(s_l, s_h)×S`。
- **[PAPER]** 長寬比 `r_e ~ Uniform(r_1, r_2)`；`H_e=sqrt(S_e×r_e)`、`W_e=sqrt(S_e/r_e)`。
- **[PAPER]** 隨機取左上角；矩形完整落在影像內才接受，否則重抽。
- **[PAPER]** Algorithm 1 將擦除區域賦予 `Rand(0,255)`；正文說區域中每個像素分別取隨機值。
- **[AUTHOR_CODE]** 2017 commit 最多重抽 100 次，幾何條件使用 `<=`，比例由 Python `random.uniform(r1, 1/r1)` 線性均勻抽樣。

## 第一階段：影像分類

### 資料與評估

- **[PAPER]** CIFAR-10 / CIFAR-100：50,000 張訓練影像、10,000 張測試影像、32×32 彩色影像，分別為 10 / 100 類。
- **[PAPER]** Fashion-MNIST：60,000 張訓練影像、10,000 張測試影像、28×28 灰階影像、10 類。
- **[PAPER]** 指標為 top-1 test error，報告 5 runs 的 `mean ± std`。
- **[UNKNOWN]** 論文沒有公開五個 run 的 seed，也沒有說明 std 使用母體或樣本公式。
- **[UNKNOWN]** 論文沒有明說表 1 使用最後一個 epoch 還是整段訓練中的最佳 test error；本專案同時保存 best 與 final，未查證前不混用。
- **[AUTHOR_CODE]** README 警告新版 Fashion-MNIST 的 baseline 與 RE 表現會略低於論文，因此該資料集須另做版本調查。

### 訓練設定

- **[PAPER]** 架構：ResNet、pre-activation ResNet、ResNeXt-29-8×64、WRN-28-10。論文表 1 寫作 `ResNeXt-8-64`，正文寫 `ResNeXt-29-8×64`，此命名差異需保留。
- **[PAPER]** 初始 learning rate 0.1；第 150、225 epoch 各除以 10；第 300 epoch 結束。
- **[PAPER]** 訓練增強：水平翻轉；每側 padding 4 後，CIFAR 隨機裁 32×32、Fashion-MNIST 隨機裁 28×28。
- **[PAPER]** 分類 RE：`p=0.5, s_l=0.02, s_h=0.4, r_1=1/r_2=0.3`，即比例範圍約 `[0.3, 3.3333]`。
- **[AUTHOR_CODE]** batch size 128、test batch size 100、SGD momentum 0.9、weight decay 5e-4。
- **[AUTHOR_CODE]** CIFAR 正規化 mean `(0.4914,0.4822,0.4465)`、std `(0.2023,0.1994,0.2010)`。
- **[PROJECT]** 第一個里程碑先完成 CIFAR-10 / ResNet-20；後續已擴充並驗證 ResNet-32，以及 CIFAR-100、Fashion-MNIST。

### 關鍵衝突：擦除填充值

- **[PAPER]** 表 2 定義 RE-R（每個像素獨立取 `[0,255]`）、RE-M（固定 ImageNet mean `[125,122,114]`）、RE-0、RE-255；並說未另行指定時，後續實驗使用 RE-R。
- **[AUTHOR_CODE]** 2017 `transforms.py` 在 `Normalize` 之後，對整個矩形各通道填固定常數 `[0.4914,0.4822,0.4465]`；Fashion-MNIST 填 `[0.4914]`。
- **結論**：論文與作者程式碼不一致。`paper_random` 與 `author_constant` 必須分開跑、分開命名，不得把任一結果冒稱另一種設定。
- **[PROJECT]** `paper_random` 在 `[0,1]` tensor 上產生逐元素均勻亂數後再 Normalize，對應原始像素 `[0,255]` 的論文描述。
- **[PROJECT]** `author_constant` 在 Normalize 後填固定值，逐行對應 2017 作者程式順序。

### 表 1 第一個驗收目標

| 資料集 | 模型 | 條件 | 論文 test error |
|---|---|---|---:|
| CIFAR-10 | ResNet-20 | Baseline | 7.21 ± 0.17 |
| CIFAR-10 | ResNet-20 | Random Erasing | 6.73 ± 0.09 |

完整已抽取列存於 `data_reference/paper_table1.csv`；檔內數字全是 paper target，不是本專案實驗輸出。正式結果位於 `runs/`，15 組聚合摘要另存於 `data_reference/reproduction_summary.csv`。

## 尚未涵蓋的後續任務

### Object detection

- **[PAPER]** PASCAL VOC 2007；trainval 訓練、test 測試；Fast R-CNN + VGG16；ImageNet 初始化；SGD 80K iterations；lr 0.001，60K 後降到 0.0001；selective search proposals。
- **[PAPER]** detection RE：`p=0.5, s_l=0.02, s_h=0.2, r_1=1/r_2=0.3`。
- **[PAPER]** 三種方案：IRE、ORE、I+ORE；表 5 同時報 VOC07 與 VOC07+12 trainval。

### Person re-identification

- **[PAPER]** Market-1501、DukeMTMC-reID、CUHK03；rank-1 與 mAP。
- **[PAPER]** IDE、TriNet、SVDNet；輸入 256×128；ImageNet 預訓練；隨機裁切與水平翻轉。
- **[PAPER]** re-ID RE：`p=0.5, s_l=0.02, s_h=0.2, r_1=1/r_2=0.3`。
- **[PAPER]** IDE：Pool5 後接 128-unit FC、BN、ReLU、Dropout(0.5)；SGD；lr 0.01；每 40 epochs 除以 10；共 100 epochs。
- **[UNKNOWN]** 這三個 baseline 的全部細節分散在被引用論文／程式碼中，未查證前不可自行填補。

## 驗收規則

1. 每個輸出必須帶 config、seed、軟硬體版本及 `is_paper_result=false`。
2. 煙霧測試只驗證程式管線，不能當成準確率復現。
3. 正式結果至少 5 runs；同時列出每次結果、mean、population std、sample std。
4. 與 paper target 比較時報絕對差（percentage points），不只寫「接近」。
5. 若結果不同，先檢查資料版本、增強順序、模型實作、初始化、optimizer、scheduler 與框架非確定性；禁止修改 target 或挑 seed 來迎合論文。
