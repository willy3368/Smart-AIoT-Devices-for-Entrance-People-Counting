import subprocess
import time
import os
import urllib.request

app_path = 'people_count_1122.py'
qr_code_path = 'qr_code.py'  # 替換成 qr_code.py 的路徑
timeout = 60  # 超時時間，單位為秒
sleep_interval = 10  # 檢查間隔時間，單位為秒
qr_timeout = 180  # qr_code.py 的運行超時時間，單位為秒 (3分鐘)

def check_internet_connection():
    """檢查網路連接狀態"""
    try:
        urllib.request.urlopen('http://www.google.com', timeout=1)
        return True
    except urllib.request.URLError:
        return False

def check_process(proc):
    """檢查進程是否仍在運行"""
    if proc.poll() == 0:
        #print(proc.poll())
        return False

    else:
        return True

def run_program():
    # 在此指定要執行的程序的路徑和指令
    subprocess.call(['python3', app_path]) 

def restart_nvargus_daemon():
    # 执行重启 nvargus-daemon 命令
    password = "77137713"
    command = 'echo {} | sudo -S service nvargus-daemon restart'.format(password)
    subprocess.call(command, shell=True)

def restart_system():
    # 執行重新啟動系統的命令
    password = "77137713"  # 輸入你的 sudo 密碼
    command = 'echo {} | sudo -S reboot'.format(password)
    os.system(command)

# 檢查網路連接狀態
if not check_internet_connection():
    print('No internet connection, starting qr_code.py...')
    qr_proc = subprocess.Popen(['python3', qr_code_path])
    qr_start_time = time.time()  # 紀錄 qr_code.py 開始運行的時間
    
    # 循环检查 qr_code.py 进程是否仍在运行
    while True:
        if not check_process(qr_proc):
            print('qr_code.py has finished. Starting process...')
            #main_proc = subprocess.Popen(['python3', app_path])
            break
        #如果Qrqr_code.py運行超過3分鐘
        elif time.time() - qr_start_time > qr_timeout:
            print('qr_code.py has timed out. Restarting system...')
            restart_system()  # 重新啟動系統
        time.sleep(sleep_interval)
else:
    print('Internet connection available, starting process...')
    #main_proc = subprocess.Popen(['python3', app_path])

# 循環檢查主要程式是否仍在運行
while True: 
        try: 
            #啟動第一個進程 
            print('Starting process...') 
            restart_nvargus_daemon()
            time.sleep(5) 
            run_program() 
        except Exception as e: 
            print ('程序發生錯誤:', str(e)) 
            time.sleep(5) # 等候5秒後重新啟動程序
            print('Restarting process...')

