import random
import pymysql
from paho.mqtt import client as mqtt_client
import mysql.connector,pymysql
from dotenv import load_dotenv
import os
import json  
import datetime 
import time


import mysql.connector
from mysql.connector import Error


client_id = 'python-mqtt-{}'.format(random.randint(0, 100))

load_dotenv()   #載入.env

# 設定MQTT參數
broker = os.getenv("broker")
port = int(os.getenv("port"))
mail = os.getenv("mail")
username = os.getenv("username1")
pw = os.getenv("password")
client_id = '87878'
topic = os.getenv("subtopic1")  #設定訂閱主題

date = []
time = []
sensor_id = []
P_in = []
P_out = []
net = []


# 連接 MySQL/MariaDB 資料庫
connection = mysql.connector.connect(
#host='120.110.20.197',          # 主機名稱
host='localhost',
database='people_counting', # 資料庫名稱
user='CYUT',        # 帳號
password='77137713')  # 密碼

# if connection.is_connected():

#     # 顯示資料庫版本
#     db_Info = connection.get_server_info()
#     print("資料庫版本：", db_Info)

#     # 顯示目前使用的資料庫
#     cursor = connection.cursor()
#     cursor.execute("SELECT DATABASE();")
#     record = cursor.fetchone()
#     print("目前使用的資料庫：", record)

# except Error as e:
#     print("資料庫連接失敗：", e)
    
# finally:
#     if connection.is_connected():
#         cursor.close()
#         connection.close()
#         print("資料庫連線已關閉")


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
    def on_message(client, userdata, msg):
        # global date
        # global time
        # global sensor_id
        # global P_in
        # global P_out
        # global net
        data = msg.payload.decode()
        print('訂閱【{}】的消息為：{}'.format(msg.topic, data))
        data_dic = json.loads(data)
        date = data_dic['Date']
        time = data_dic['Time']
        sensor_id = data_dic['Sensor_id']
        P_in = data_dic['In']
        P_out = data_dic['Out']
        net = data_dic['Net']

        # 新增資料
        sql = "INSERT INTO people_counting (date, time, sensor_id, P_in, P_out, net) VALUES (%s, %s, %s, %s, %s, %s);"
        new_data = ( date, time, sensor_id, P_in, P_out, net)
        cursor = connection.cursor()
        cursor.execute(sql, new_data)

        # 確認資料有存入資料庫
        connection.commit()

    client.subscribe(topic)
    client.on_message = on_message





def run():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


if __name__ == '__main__':
    connect_mqtt()
    run()
