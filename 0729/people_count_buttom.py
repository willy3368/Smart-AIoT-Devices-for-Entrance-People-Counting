# TechVidvan Vehicle counting and Classification
# Import necessary packages
import cv2
import csv
import collections
import os
import numpy as np
#from tracker import *
from utils.centroidtracker import CentroidTracker
from utils.trackableobject import TrackableObject

import time
import threading
import json
import datetime
#from datetime import datetime
import Attendance
from paho.mqtt import client as mqtt_client
from dotenv import load_dotenv
from threading import Thread
import publish
import logging
import random
import RS485_warn
import shutil
# Initialize Tracker
#tracker = EuclideanDistTracker()

ct = CentroidTracker(maxDisappeared=20, maxDistance=80)
# Initialize the videocapture object
GSTREAMER_PIPELINE = 'nvarguscamerasrc ! video/x-raw(memory:NVMM), width=480, height=270,format=(string)NV12,framerate=30/1 ! nvvidconv flip-method=2 ! video/x-raw, width=480, height=270, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'
#cap = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
#cap = cv2.VideoCapture(1)
cap = cv2.VideoCapture('C:/Users/willy/案子/people_counting/test video/building02.mp4')
#cap = cv2.VideoCapture('C:/Users/willy/案子/people_counting/test video/tracker.avi')
#cap = cv2.VideoCapture('/home/user/people_counting/test video/record_Trim2.mp4')
#cap = cv2.VideoCapture('C:/Users/willy/Desktop/測試影片/錄影/record.avi')

#設置log檔格式
logging.basicConfig(filename = "mylog.log",level = logging.INFO, format = "%(asctime)s %(levelname)s: %(message)s")

input_size = 320

# Detection confidence threshold
confThreshold =0.01
nmsThreshold= 0.2

yellow = (0,255,255)
font_color = (0, 0, 255)
font_size = 0.5
font_thickness = 2

# Middle cross line position
#middle_line_position = 240  #130
#up_line_position = middle_line_position - 90  #30
#down_line_position = middle_line_position + 90  #30


#設置垂直中線位置
vertical_middle_line_position = 240
left_line_position = vertical_middle_line_position - 100  
right_line_position = vertical_middle_line_position + 100  
#設置水平中線位置
horizontal_middle_line_position = 120 #120
up_line_position = horizontal_middle_line_position - 25 #30
down_line_position = horizontal_middle_line_position + 25 #30
#輸入1為水平其他則為垂直
#input = int(input('input 1 with horizontal:'))
input = 1

# Store Coco Names in a list
classesFile = "coco.names"
classNames = open(classesFile).read().strip().split('\n')
#print(classNames)
#print(len(classNames))

# class index for our required detection classes
required_class_index = [0]

detected_classNames = []

## Model Files
modelConfiguration = 'yolov4-tiny.cfg'
modelWeigheights = 'yolov4-tiny.weights'

# configure the network model
net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeigheights)

# Configure the network backend

net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)

# Define random colour for each class
np.random.seed(42)
colors = np.random.randint(0, 255, size=(len(classNames), 3), dtype='uint8')

load_dotenv()   #載入.env

# 設定MQTT參數
broker = os.getenv("broker")
port = int(os.getenv("port"))
mail = os.getenv("mail")
username = os.getenv("username1")
pw = os.getenv("password")
topic = os.getenv("subtopic1")  #設定訂閱主題
client_id = os.getenv("sensor_id") + f"-{random.randint(0, 1000)}"


# Function for finding the center of a rectangle
def find_center(x, y, w, h):
    x1=int(w/2)
    y1=int(h/2)
    cx = x+x1
    cy=y+y1
    return cx, cy
    
# List for store vehicle count information
temp_up_list = []
temp_down_list = []
up_list = [0]
down_list = [0]
build_list = [0]
#build_list[0] = build_list[0] +8
people_number=1
num = 0
camerainitia = 0    #初始化參數
count = 0 #計算進出



#初始歸0
def initialization():
    global up_list
    global down_list
    global pepeople_number
    global build_list
    global count
    temp_up_list.clear
    temp_down_list.clear
    up_list = [0]
    down_list = [0]
    build_list = [0]
    #people_number=1          #進出編號
    #count = 0                #屋頂人數計數


#每天凌晨3點初始化list
def resetlist():
    global up_list
    global down_list
    global pepeople_number
    global build_list
    global count
    # 取得現在時間
    # Wed May 18 16:24:48 2022
    now = time.asctime( time.localtime(time.time()))
    # 取得小時
    #hour = now.split(" ")[3].split(":")[0]
    hour = time.strftime('%H:%M:%S',time.localtime())
    # 今天的日期
    today_date = time.strftime('%Y-%m-%d',time.localtime())
    #print(hour)
    if hour == "23:59:00": #"03:00:00"
        #備份座標檔案
        buttom_id_data_backup()
        #每日備份
        # Data to be written
        dictionary = {
                "date": today_date,
                "In": up_list[0],
                "Out": down_list[0],
                "Net": build_list[0]
        }

        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        # Writing to sample.json
        with open("Pedestrian_flow.json", "a") as outfile:
                outfile.write(json_object)
                print("Data has been stored")

    if hour == "03:00:00":
        #刷新資料
        temp_up_list.clear
        temp_down_list.clear
        up_list[0] = 0
        down_list[0] = 0
        build_list[0]= 0
        people_number=1          #進出編號
        count = 0                #屋頂人數計數
        #print('refresh data')
        print(f"Time:{ now }\n Reset temp List")
        #重開機
        #os.system("reboot")
        #logging.info("reboot")   #紀錄log


def buttom_id_data_backup():
    # 今天的日期
    today_date = time.strftime('%Y-%m-%d',time.localtime())
    # 資料夾名稱
    folder_name = 'buttom_id_data'
    
    # 確認資料夾存在，不存在則建立
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    # 原始檔案和備份檔案的路徑
    original_file = 'buttom_id_data.txt'
    backup_file =  os.path.join(folder_name, f'buttom_id_data_{today_date}.txt')

    # 關閉原始文件，備份文件並清空原始文件內容
    with open(original_file, 'r') as file:
        file_content = file.read()
    shutil.copy(original_file, backup_file)
    with open(original_file, 'w') as file:
        file.write('')
    print(f"File '{original_file}' has been backed up as '{backup_file}' and cleared.")


#連線MQTT
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(topic)
            print("Subscribed to topic:",topic)
        else:
            print(f"Failed to connect, return code {rc}\n")

    client = mqtt_client.Client(client_id,clean_session=False)
    client.on_connect = on_connect
    client.username_pw_set(username=username,password=pw)
    client.connect(broker, port, keepalive=36000)
    client.loop_start()  # 將此行移至此處以確保僅在初始化時啟動循環
    return client

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code "+str(rc))
    time.sleep(5)  # 等待5秒鐘再重新連線
    client.reconnect()


def client_mqtt():
    client = connect_mqtt()
    #client.on_connect = on_connect
    #client.on_disconnect = on_disconnect
    client.subscribe(topic)
    client.loop_start()

class client(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        client = connect_mqtt()
        client.on_disconnect = on_disconnect  # 設置斷線處理
        # while True:
        #     client_mqtt()
        #     time.sleep(1200)


class mqtt(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            send_quantity()    #回傳MQTT
            time.sleep(1200)


class regular_storage(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            time.sleep(1200)
            save_json()

buttom_id =[]
buffer = []  #佔存座標資料

class coordinate(Thread):  #儲存座標
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global num
        global buffer  # 引入 buffer 变量

        while True:
            if num > 0:  # 有偵測到人就開始儲存座標
               print("buttom_id:",buttom_id)
               if buttom_id != []:
                    buffer.append(buttom_id)  # 将数据暂存至 buffer 列表中
                    print("Buffered:", buffer)  # 可选：打印获取到的值用于检查

            time.sleep(1)

            # 每隔一段时间（例如每 10 秒）将 buffer 中的数据写入文件
            if len(buffer) >= 5:  # 在这里设置每隔 10 次存储才写入一次文件，可以根据需求调整
                with open('buttom_id_data.txt', 'a') as file:

                    flattened_data = ','.join(map(str, buffer))  # 将数据转换为逗号分隔的字符串格式
                    file.write(flattened_data + '\n')
                    file.flush()  # 刷新文件以确保数据被及时写入
                    print("Flushed data to file.")
                buffer = []  # 清空 buffer
                print("buffer:",buffer)

def buttom(rects):
          
	#inputCentroids = np.zeros((len(rects), 2), dtype="int")

	# initialize an array of input centroids for the current frame
	# 初始化 inputCentroids 陣列
	inputbuttom = []
	#loop over the bounding box rectangles
	for (i, (startX, startY, endX, endY)) in enumerate(rects):
		# use the bounding box coordinates to derive the centroid
		cX = int((startX + endX) / 2.0)
		cY = int((endY))
		# 將座標以特定格式添加到 inputCentroids 陣列中
		inputbuttom.append((cX, cY))
	return inputbuttom

class reset(Thread):    #監測是否凌晨3點
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            resetlist()
            time.sleep(1)

class send_message(Thread):
    global num
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        global num
        num = int(num)
        a = int(build_list[0])
        while True:
            #print('num=',num)
            
            if a != int(build_list[0]):   #偵測人數有沒有變動
                time.sleep(3)                  
                #print(build_list[0])
                send_quantity()    #回傳MQTT
                a = int(build_list[0])
            time.sleep(1)

#回傳MQTT大樓人數
switch = 0
def send_quantity():
    global switch
    if  switch == 0:
        #switch =1 
        publish.jetson_publish(up_list[0],down_list[0],build_list[0])
        #initialization()
        #time.sleep(5)
        #switch =0


def repeat(x):
    #createTimer()
    global people_number
    if x == 0:
        path = 'InOutTime'
        f = open(path, 'a')
        print(people_number , ':' , time.strftime('%m/%d-%H:%M:%S-In',time.localtime()),file=f)
        f.close()
        #print(people_number,':', time.strftime('%m/%d-%H:%M:%S-In',time.localtime()))    #回傳當下人經過時間
        result = time.strftime("%m/%d-%H:%M:%S-In",time.localtime())
        print(people_number,':',result)
    if x == 1:
        path = 'InOutTime'
        f = open(path, 'a')
        print(people_number ,':' , time.strftime('%m/%d-%H:%M:%S-Out',time.localtime()),file=f)
        f.close()
        #print(people_number,':', time.strftime('%m/%d-%H:%M:%S-Out',time.localtime()))    #回傳當下人經過時間
        result = time.strftime('%m/%d-%H:%M:%S-Out',time.localtime())
        print(people_number,':',result)
    #print(people_number,':', datetime.utcnow().strftime('%d_%H_%M_%S.%f')[:-2])
    people_number += 1




#截圖
def screen(box_id,img):

    now = datetime.now()
    #水平
    cv2.line(img, ( 0,horizontal_middle_line_position), ( 480,horizontal_middle_line_position), (255, 0, 255), 2)
    cv2.line(img, ( 0,up_line_position), ( 480,up_line_position), (0, 0, 255), 2)
    cv2.line(img, ( 0,down_line_position), ( 480,down_line_position), (0, 0, 255), 2)
#水平
     # Draw counting texts in the frame
    cv2.putText(img, "In", (110, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
    cv2.putText(img,"Out", (170, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
    cv2.putText(img, "Building", (210, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
    cv2.putText(img, "Person:     "+str(up_list[0])+"     "+ str(down_list[0])+"       "+ str(build_list[0]), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
    filetime = time.strftime('%m-%d-%H_%M_%S',time.localtime(time.time()))     #檔名為時間
    #filetime = datetime.utcnow().strftime('%d_%H_%M_%S.%f')[:-2]

    cv2.imwrite('/home/user/people_counting/0729/InOut/' + filetime +'.jpg', img)            #存入截圖到資料夾



    #cv2.imshow("Out",imgS)


# Function for count vehicle
def count_vehicle(box_id, img):

    #print(box_id)
    id,cen = box_id
    ix,iy = cen[0],cen[1]
    global count
    # global px,py
    # detection = []
    # detection.append([x, y, w, h, index])
    # # Find the center of the rectangle for detection
    # center = find_center(x, y, w, h)
    # ix, iy = center
    index=0
    if input==1:
        #水平中線位置
        # Find the current position of the vehicle
        if (iy > up_line_position) and (iy < horizontal_middle_line_position):

            if id not in temp_up_list:
                temp_up_list.append(id)
                #print(id)
                #print(temp_up_list)

        elif iy < down_line_position and iy > horizontal_middle_line_position:
            if id not in temp_down_list:
                temp_down_list.append(id)
                #print(id)
                #print(temp_down_list)

        elif iy < up_line_position:#In
            #if py > up_line_position:
            if id in temp_down_list:
                temp_down_list.remove(id)
                up_list[index] = up_list[index]+1
                build_list[index] = build_list[index] +1
                #if build_list[index] < 0:          #防止人數-1情況
                    #build_list[index] = 0
                #RS485_warn.count(up_list[index],0)
                repeat(0)
                #screen(box_id,img)
                #send_quantity()    #回傳MQTT
                #initialization()   #歸0
                #publish.jetson_publish(up_list[index],down_list[index],build_list[index])
                #print(x,y,w,h)

        elif iy > down_line_position:#Out
            #if py < down_line_position:
            if id in temp_up_list:
                temp_up_list.remove(id)
                down_list[index] = down_list[index] + 1
                build_list[index] = build_list[index] -1
                #if build_list[index] < 0:          #防止人數-1情況
                    #build_list[index] = 0
                #RS485_warn.count(down_list[index],1)
                repeat(1)
                #screen(box_id,img)
                #send_quantity()        #回傳MQTT
                #initialization()       #歸0
                #publish.jetson_publish(up_list[index],down_list[index],build_list[index])
                #print(x,y,w,h)
        
        #py = iy

    else:
        #垂直中線位置
        # Find the current position of the vehicle
        if (ix > left_line_position) and (ix < vertical_middle_line_position):

            if id not in temp_up_list:
                temp_up_list.append(id)
                #print("OK1")

        elif ix < right_line_position and ix > vertical_middle_line_position:
            if id not in temp_down_list:
                temp_down_list.append(id)
                #print("OK2")

        elif ix < left_line_position:#Out
            if id in temp_down_list:
                temp_down_list.remove(id)
                up_list[index] = up_list[index]+1
                build_list[index] = build_list[index] -1

                repeat(0)
                screen(box_id,img)
                #print(x,y,w,h)

        elif ix > right_line_position:#In
            if id in temp_up_list:
                temp_up_list.remove(id)
                down_list[index] = down_list[index] + 1
                build_list[index] = build_list[index] +1
                repeat(1)
                screen(box_id,img)

    # Draw circle in the middle of the rectangle
    #cv2.circle(img, center, 2, (0, 0, 255), -1)  # end here
    cv2.putText(img, str(id), (ix, iy+5), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0,255,255), font_thickness)
    #print(id)
    # print(up_list, down_list)





# Function for finding the detected objects from the network output
area = 0
def postProcess(outputs,img):
    global detected_classNames 
    global num
    global camerainitia
    global area
    global buttom_id
    height, width = img.shape[:2]
    boxes = []
    classIds = []
    confidence_scores = []
    detection = []
    rects = []
    for output in outputs:
        for det in output:
            scores = det[5:]
            classId = np.argmax(scores)
            confidence = scores[classId]
            if classId in required_class_index:
                if confidence > confThreshold:
                    #print(classId)
                    w,h = int(det[2]*width) , int(det[3]*height)
                    x,y = int((det[0]*width)-w/2) , int((det[1]*height)-h/2)
                    boxes.append([x,y,w,h])
                    classIds.append(classId)
                    confidence_scores.append(float(confidence))

    # Apply Non-Max Suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidence_scores, confThreshold, nmsThreshold)
    # print(classIds)
    if len(indices) > 0:
      for i in indices.flatten():
        x, y, w, h = boxes[i][0], boxes[i][1], boxes[i][2], boxes[i][3]
        # print(x,y,w,h)

        color = [int(c) for c in colors[classIds[i]]]
        name = classNames[classIds[i]]
        detected_classNames.append(name)
        # Draw classname and confidence score 
        #cv2.putText(img,f'{name.upper()} {int(confidence_scores[i]*100)}%',
                  #(x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

        # Draw bounding rectangle
        #h=int(h/3)
        #cv2.rectangle(img, (x, y), (x + w, y + h), color, 1)
        #print('w*h=' + str(w*h))
        if camerainitia < 10:
             area += w*h
             camerainitia += 1
        if camerainitia == 10:
             area = area/10
             BoundingboxSize(area)    #初始化設定
             camerainitia += 1
        #detection.append([x, y, w, h, required_class_index.index(classIds[i])])
        rects.append((x, y, x+w, y+h))
        #print(detection)
        #print(format(len(detection)))      #回傳畫面偵測到的物件數量
        num = format(len(rects))
        num = int(num)
        #print('num=',num)
        print("rects:",rects)
    # Update the tracker for each object
    #boxes_ids = tracker.update(detection)
    boxes_ids = ct.update(rects, False)
    buttom_id = buttom(rects)
    #print(buttom_id)
    #print(boxes_ids)
    for box_id in boxes_ids.items():
        count_vehicle(box_id, img)

#框框大小判斷tracker參數設定
def BoundingboxSize(area):
         #w = 300
         #h = 300
         if area < 1000:
                 ct = CentroidTracker(maxDisappeared=20, maxDistance=25)
                 print('The distance is set to 25')
         elif area >1000 and area <3000:
                 ct = CentroidTracker(maxDisappeared=20, maxDistance=80)
                 print('The distance is set to 80')
         elif area > 3000:
                 ct = CentroidTracker(maxDisappeared=20, maxDistance=100)
                 print('The distance is set to 100')


def save_json():
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Data to be written
        dictionary = {
                "time": now,
                "In": up_list[0],
                "Out": down_list[0],
                "Net": build_list[0]
        }

        # Serializing json
        json_object = json.dumps(dictionary, indent=4)

        # Writing to sample.json
        with open("record.json", "w") as outfile:
                outfile.write(json_object)
                print("Data has been stored")


def read_json():
        # Opening JSON file
        with open('record.json', 'r') as openfile:
            # Reading from json file
            json_object = json.load(openfile)
            saved_time_str = json_object['time']
            In = json_object['In']
            Out = json_object['Out']
            Net = json_object['Net']

        saved_time = datetime.datetime.strptime(saved_time_str, '%Y-%m-%d %H:%M:%S')
        # 计算时间差
        time_difference = datetime.datetime.now() - saved_time
        #print(json_object)
        # 判断时间差是否超过12小时
        if time_difference < datetime.timedelta(hours=12):
                up_list[0] = In
                down_list[0] = Out
                build_list[0] = Net
                #RS485_warn.count(In,0)
                #RS485_warn.count(Out,1)
                print("Apply backup data")

# 設定擷取影像的尺寸大小
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# 使用 XVID 編碼
#fourcc = cv2.VideoWriter_fourcc(*'mp4v')

# 建立 VideoWriter 物件，輸出影片至 Video.mp4
# FPS 值為 20.0，解析度為 640x480
#out = cv2.VideoWriter("Video.mp4", fourcc, 30.0, (480, 270))
def realTime():
    count = 0

    #RS485_warn.count(0,0)
    #RS485_warn.count(0,1)
    #print("12345")
    read_json()

    while True:
        success, img = cap.read()
        img = cv2.resize(img,(480,270),None,0.5,0.5)
        ih, iw, channels = img.shape
        fps = cap.get(cv2.CAP_PROP_FPS)
        if count % 1 == 0:
                blob = cv2.dnn.blobFromImage(img, 1 / 255, (input_size, input_size), [0, 0, 0], 1, crop=False)

                # Set the input of the network
                net.setInput(blob)
                layersNames = net.getLayerNames()
                #outputNames = [(layersNames[i[0]- 1]) for i in net.getUnconnectedOutLayers()]
                outputNames = [(layersNames[i- 1]) for i in net.getUnconnectedOutLayers()]
        	# Feed data to the network
                outputs = net.forward(outputNames)
    
        	# Find the objects from the network output
                postProcess(outputs,img)

                localtime = time.localtime()
                timetext = time.strftime(" %I:%M:%S %p",localtime)
        	# Draw the crossing lines
                if input==1:
                    #水平
                    cv2.line(img, ( 0,horizontal_middle_line_position), ( iw,horizontal_middle_line_position), (255, 0, 255), 2)
                    cv2.line(img, ( 0,up_line_position), ( iw,up_line_position), (0, 0, 255), 2)
                    cv2.line(img, ( 0,down_line_position), ( iw,down_line_position), (0, 0, 255), 2)

                else:
                    #垂直
                    cv2.line(img, ( vertical_middle_line_position,0), ( vertical_middle_line_position, ih), (255, 0, 255), 2)
                    cv2.line(img, ( left_line_position,0), ( left_line_position, ih), (0, 0, 255), 2)
                    cv2.line(img, ( right_line_position,0), ( right_line_position, ih), (0, 0, 255), 2)

                if input==1:
                    #水平
                    # Draw counting texts in the frame
                    cv2.putText(img, "In", (110, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, yellow, font_thickness)
                    cv2.putText(img,"Out", (170, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, yellow, font_thickness)
                    cv2.putText(img, "net", (230, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, yellow, font_thickness)
                    cv2.putText(img, "Person:     "+str(up_list[0])+"     "+ str(down_list[0])+"       "+ str(build_list[0]), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, font_size, yellow, font_thickness)
                    #cv2.putText(img, timetext, (350, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, yellow, font_thickness)
                    #cv2.putText(img, str(fps), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
        # Show the frames

                else:
                    #垂直
                    # Draw counting texts in the frame
                    cv2.putText(img, "Left", (100, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
                    cv2.putText(img,"Right", (170, 20), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)
                    cv2.putText(img, "Person:   "+str(up_list[0])+"       "+ str(down_list[0]), (20, 40), cv2.FONT_HERSHEY_SIMPLEX, font_size, font_color, font_thickness)

                count = 1
        else:
                count += 1
                continue
        # 寫入影格
        #out.write(img)
        cv2.imshow('Output', img)
        #resetlist()
        if cv2.waitKey(1) == ord('q'):
            print('(IN:',up_list,',OUT:',down_list,')')
            break

    # Write the vehicle counting information in a file and save it

    with open("data.csv", 'w') as f1:
        cwriter = csv.writer(f1)
        cwriter.writerow(['Direction','Person'])
        up_list.insert(0, "Out")
        down_list.insert(0, "In")
        cwriter.writerow(up_list)
        cwriter.writerow(down_list)
    
    
    f1.close()
    # print("Data saved at 'data.csv'")
    # Finally realese the capture object and destroy all active windows
    cap.release()
    #out.release()
    cv2.destroyAllWindows()
    #resetlist()





if __name__ == '__main__':
    #connect_mqtt()
    regular_storage()
    #client()
    #client_mqtt()
    #mqtt()
    reset()
    #send_message()
    coordinate()
    realTime()
    #from_static_image(image_file)

