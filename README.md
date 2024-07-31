# Smart-AIoT-Devices-for-Entrance-People-Counting


# 人流計數系統 (People Counting System)

## 介紹
這是一個人流計數的程式，旨在計算特定區域內進出人數。此系統設計可運行於邊緣運算裝置如 NVIDIA Jetson Nano 上，利用 OpenCV 進行影像處理，並使用深度學習模型 YOLOv4-tiny 來偵測和追蹤物件。此系統還結合了 MQTT 通訊協定，用於數據傳輸和遠端監控。

## 系統架構
整個系統包含兩個主要部分：
1. **物件追蹤模組** (`centroidtracker.py`): 這個模組負責追蹤偵測到的物件，並根據物件的消失時間與距離來判斷是否要移除該物件。
2. **人流計數模組** (`people_count.py`): 這個模組處理影像輸入、進行物件偵測、計算進出人數，並將資料回傳至 MQTT 伺服器。

## 前置準備
在開始使用系統前，請確保已安裝以下必要的 Python 套件：
```
pip install numpy opencv-python paho-mqtt python-dotenv
```
並準備好 YOLOv4-tiny 的模型檔案：
- `yolov4-tiny.cfg`
- `yolov4-tiny.weights`

同時，準備一個包含物件分類名稱的 `coco.names` 檔案。

## 使用方法
### 設定 MQTT
在專案目錄下，創建一個 `.env` 檔案並填入 MQTT 相關設定：
```
broker=<your_broker>
port=<your_port>
mail=<your_mail>
username1=<your_username>
password=<your_password>
subtopic1=<your_subtopic>
sensor_id=<your_sensor_id>
```

### 運行程式
執行 `people_count.py` 主程式：
```
python people_count.py
```

## 程式調整參數
### `centroidtracker.py`
- `maxDisappeared`: 物件被標記為消失前允許的最大連續幀數。
- `maxDistance`: 物件中心之間的最大距離，超過此距離將被標記為消失。

### `people_count.py`
- `GSTREAMER_PIPELINE`、`cap`: 設定影像輸入來源，可以是 USB 攝影機或是影片檔案。
- `confThreshold`: 物件偵測信心門檻值。
- `nmsThreshold`: Non-Max Suppression 門檻值，用於濾除重疊的邊界框。
- `vertical_middle_line_position`、`horizontal_middle_line_position`: 垂直與水平中線的位置，用於計算進出人數。

## 核心功能
### `CentroidTracker`
負責物件的追蹤、註冊與取消註冊。其核心方法包括：
- `register(self, centroid)`: 註冊新的物件。
- `deregister(self, objectID)`: 移除消失的物件。
- `update(self, rects, buttom)`: 更新物件的位置，並進行註冊或移除。

範例:
```python
from centroidtracker import CentroidTracker

# 初始化追蹤器
ct = CentroidTracker(maxDisappeared=20, maxDistance=80)

# 假設 rects 為偵測到的邊界框列表
rects = [(50, 50, 100, 100), (150, 150, 200, 200)]

# 更新追蹤器
objects = ct.update(rects, False)
print(objects)
```

### `people_count.py`
- 影像擷取與前處理。
- 物件偵測與後處理。
- 計數邏輯與資料儲存。
- MQTT 連線與資料回傳。

## 注意事項
- 確保攝影機或影片來源的解析度與設定相符，以獲得最佳效果。
- 定期檢查並清理備份檔案以節省儲存空間。
