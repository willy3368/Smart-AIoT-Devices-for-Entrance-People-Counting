import cv2
from pyzbar.pyzbar import decode
import subprocess
import re
import time
import os

#開始時間
start_time = time.time()

#使用CSI cam
GSTREAMER_PIPELINE = "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720,format=(string)NV12, framerate=(fraction)60/1 ! nvvidconv flip-method=2 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink"
#if len(sys.argv) < 2:
cap = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)
#else:
#    cap = cv2.VideoCapture(sys.argv[1])
#cap = cv2.VideoCapture(0)

while True:

    # 2; 當前時間
    current_time = time.time()
    # 計算程式運行時間
    elapsed_time = current_time - start_time

    # 超過三分鐘，重啟系統
    if elapsed_time > 180:
        print("the program runs for more than 3 minutes，restart system...")
        os.system("sudo reboot")

    ret, frame = cap.read()
    frame = cv2.resize(frame,(480,480),None,1,1)
    if not ret:
        continue

    # 解析QRCode
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        if obj.type == 'QRCODE':
            wifi_info = obj.data.decode('utf-8')
            print("WiFi Info:", wifi_info)

            # 解析WiFi信息並連接
            ssid = ""
            password = ""
            for param in wifi_info.split(';'):
                match = re.match(r'(\w+):(.+)',param)
                if match:
                    key = match.group(1)
                    value = match.group(2)
                    if key == "S":
                        ssid = value
                    elif key == "P":
                        password = value

            if ssid and password:
                cmd = f"nmcli device wifi connect '{ssid}' password '{password}'"
                subprocess.run(cmd, shell=True)
                print(f"connet '{ssid}' '{password}'")
                
                 # 檢查網路連線
                connected = subprocess.run("ping -c 1 google.com", shell=True)
                if connected.returncode == 0:
                    print("Connected to the internet.")
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()
                else:
                    print("Failed to connect to the internet.")

    cv2.imshow('QRCode Scanner', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
