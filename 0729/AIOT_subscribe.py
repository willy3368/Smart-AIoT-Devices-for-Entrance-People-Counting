import random
from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
import os
import json  
import datetime 
import time
import subprocess
#from mysql.connector import Error


#client_id = 'python-mqtt-{}'.format(random.randint(0, 100))

load_dotenv()   #載入.env

# 設定MQTT參數
broker = os.getenv("broker")
port = int(os.getenv("port"))
mail = os.getenv("mail")
username = os.getenv("username1")
pw = os.getenv("password")
client_id = 'server3'
topic = os.getenv("subtopic1")  #設定訂閱主題

#人流
date = []
time = []
sensor_id = []
P_in = []
P_out = []
net = []

#停車場
ParkingSpace = []
InMin =[]
OutMax= []

#體育館
status = []
start_time = []
use_time = []



#連線MQTT
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}\n")

    client = mqtt_client.Client(client_id,clean_session=False)
    client.on_connect = on_connect
    client.username_pw_set(username=username,password=pw)
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):

    def callback(client, userdata, message):
        # 檢查訊息是否為空
        if not message.payload:
            print("收到空的訊息，忽略該筆訊息")
            return
        # 不是空的訊息，繼續處理
        on_message(client, userdata, message)

    def on_message(client, userdata, msg):

        # 判斷主題結尾並將訊息存入相應的資料庫
        #設定檔
        if msg.topic.endswith("/Setting"):

            data = msg.payload.decode()
            #with open('/home/seafoodlab/log/MQTT_log.txt',"a") as f:
            #   f.write('訂閱【{}】的消息為：{}\n'.format(msg.topic, data))
            #print('訂閱【{}】的消息為：{}'.format(msg.topic, data))
            print('【{}】調整程式參數:{}'.format(msg.topic,data))
            # Writing to sample.json
            with open("setting.json", "w") as outfile:
                outfile.write(data)
                print("Data has been stored")
                #mqtt_client.publish()
            # kill掉主程式
            #subprocess.run(['pkill', '-f', people_count_1122.py])

        elif msg.topic.endswith("/Count"):

            data = msg.payload.decode()
            #with open('/home/seafoodlab/log/MQTT_log.txt',"a") as f:
            #   f.write('訂閱【{}】的消息為：{}\n'.format(msg.topic, data))
            #print('訂閱【{}】的消息為：{}'.format(msg.topic, data))
            print('【{}】修改計數資料:{}'.format(msg.topic,data))
            with open("record.json", "w") as outfile:
                outfile.write(data)
                print("Data has been stored")
            # kill掉主程式
            #subprocess.run(['pkill', '-f', people_count_1122.py])

        #更新主程式程式碼    
        elif msg.topic.endswith("/Update"):
            data = msg.payload.decode("utf-8")
            print('訂閱【{}】的消息為：{}'.format(msg.topic, data))
            with open("people_counting_test.py", "w") as outfile:
                outfile.write(data)
                print("Data has been stored")

        # else:
        #     data = msg.payload.decode("utf-8")
        #     print('訂閱【{}】的消息為：{}'.format(msg.topic, data))

        # if data != "" and not data_dic:
        #     data = ""
        #     data_dic.clear()
        #elif msg.topic.endswith("/"):

    client.subscribe(topic)
    client.on_message = on_message

def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()

if __name__ == '__main__':
    run()
