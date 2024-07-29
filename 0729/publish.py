import paho.mqtt.client as mqtt
import random
import json  
import datetime 
import time
from dotenv import load_dotenv
import os


load_dotenv()   #載入.env

# 設定MQTT參數
broker = os.getenv("broker")
port = int(os.getenv("port"))
username = os.getenv("username1")
pw = os.getenv("password")
client_id = os.getenv("sensor_id") + f"-{random.randint(0, 1000)}"
topic = os.getenv("subtopic1")  #設定訂閱主題
sensor_id = os.getenv("sensor_id")

# 設置日期時間的格式
ISOTIMEFORMAT = '%m/%d %H:%M:%S'

# 連線設定
# 初始化地端程式
client = mqtt.Client()

# 設定登入帳號密碼
client.username_pw_set(username=username,password=pw)

# 設定連線資訊(IP, Port, 連線時間)
client.connect(broker, port, keepalive=36000)

#while True:
def jetson_publish(In,Out,Net):
    t0 = random.randint(0,30)
    today = datetime.date.today()
    #t = datetime.datetime.now().strftime(ISOTIMEFORMAT)
    d = time.strftime('%y/%m/%d')
    t = time.strftime("%H:%M:%S",time.localtime())
    payload = {'Date' : d , 'Time' : t , 'Sensor_id' : sensor_id , 'In' : In , 'Out' : Out , 'Net' : Net}
    #print ('發布的消息為：',json.dumps(payload))
    #要發布的主題和內容
    client.publish(topic, json.dumps(payload))
    #time.sleep(5)


#發布Qos2品質的訊息，如果沒有回傳到就將主程式kill掉重啟
def jetson_publish_qos2(In, Out, Net):
    t0 = random.randint(0,30)
    today = datetime.date.today()
    d = time.strftime('%y/%m/%d')
    t = time.strftime("%H:%M:%S", time.localtime())
    payload = {'Date': d, 'Time': t, 'Sensor_id': sensor_id, 'In': In, 'Out': Out, 'Net': Net}

    # 發布Qos2的消息
    info = client.publish(topic, json.dumps(payload), qos=2)
    info.wait_for_publish()

    # 檢查是否有收到訊息
    if info.rc != mqtt.MQTT_ERR_SUCCESS:
        print("Message publish failed. Restarting...")
        # 重啟程式
        os.system("pkill -f people_count_1122.py")