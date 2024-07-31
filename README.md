# Smart-AIoT-Devices-for-Entrance-People-Counting


# 人流計數與分類

此專案設計用於通過視頻流計數和分類人流。該程式使用 OpenCV 進行圖像處理，使用質心追蹤器追蹤人流，並使用 MQTT 客戶端進行通信。

## 目錄

- [安裝](#安裝)
- [使用方法](#使用方法)
- [功能](#功能)
- [配置](#配置)
- [相依性](#相依性)
- [許可](#許可)

## 安裝

進入專案目錄：
```bash
cd people_counting
```

安裝所需的 Python 套件：
```bash
pip install -r requirements.txt
```

確保你已經在專案目錄中擁有必要的模型文件 (`yolov4-tiny.cfg`, `yolov4-tiny.weights`, `coco.names`)。

## 使用方法

在程式中設置你的視頻捕捉源：
```python
cap = cv2.VideoCapture('path_to_your_video.mp4')
```

運行程式：
```bash
python people_count_1122.py
```

## 功能

- 實時人流計數
- MQTT 客戶端通信
- 自動備份數據和每日重置
- 可自定義的檢測區域

## 配置

### 環境變量

在專案目錄中創建 `.env` 文件並設置以下變量：
```makefile
broker=<MQTT_BROKER>
port=<MQTT_PORT>
mail=<EMAIL>
username1=<MQTT_USERNAME>
password=<MQTT_PASSWORD>
subtopic1=<MQTT_SUBSCRIBE_TOPIC>
sensor_id=<SENSOR_ID>
```

### 參數

根據需要調整程式中的參數：
```python
input_size = 320
confThreshold = 0.01
nmsThreshold = 0.2
vertical_middle_line_position = 240
horizontal_middle_line_position = 120
```

## 相依性

- OpenCV
- NumPy
- paho-mqtt
- python-dotenv

你可以使用 `requirements.txt` 文件安裝這些相依性：
```bash
pip install -r requirements.txt
```

## 許可

此專案是基於 MIT 許可的。詳見 [LICENSE](LICENSE) 文件。
