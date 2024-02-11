import numpy as np
import cv2
import time
import RPi.GPIO as GPIO

#モータードライバー関連は右リンク参照 https://creators-small-room.hatenablog.com/entry/motor-driver

#ピン番号の割り当て方式を「コネクタのピン番号」に設定
GPIO.setmode(GPIO.BOARD)

#使用するピン番号を代入
AIN1 = 8
AIN2 = 10
PWMA = 12

BIN1 = 22
BIN2 = 24
PWMB = 26

#各ピンを出力ピンに設定
GPIO.setup(AIN1, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(AIN2, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(PWMA, GPIO.OUT, initial = GPIO.LOW)

GPIO.setup(BIN1, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(BIN2, GPIO.OUT, initial = GPIO.LOW)
GPIO.setup(PWMB, GPIO.OUT, initial = GPIO.LOW)

#PWMオブジェクトのインスタンスを作成
#出力ピン：12,26  周波数：100Hz
p_a = GPIO.PWM(PWMA,100)
p_b = GPIO.PWM(PWMB,100)

#PWM信号を出力
p_a.start(0)
p_b.start(0)

#デューティを設定(0~100の範囲で指定)
#速度は80%で走行する。
val = 80

#デューティ比を設定
p_a.ChangeDutyCycle(val)
p_b.ChangeDutyCycle(val)

#ブレーキする関数
def func_brake():
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.HIGH)


#前進する関数
def func_forward():
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)


#後進する関数
def func_back():
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)


#右回転する関数
def func_right():
    GPIO.output(AIN1, GPIO.LOW)
    GPIO.output(AIN2, GPIO.HIGH)
    GPIO.output(BIN1, GPIO.HIGH)
    GPIO.output(BIN2, GPIO.LOW)


#左回転する関数
def func_left():
    GPIO.output(AIN1, GPIO.HIGH)
    GPIO.output(AIN2, GPIO.LOW)
    GPIO.output(BIN1, GPIO.LOW)
    GPIO.output(BIN2, GPIO.HIGH)


# カメラの初期化
camera = cv2.VideoCapture("/dev/video0")
face_cascade = cv2.CascadeClassifier('/home/username/project/haarcascades/haarcascade_upperbody.xml') # '/usr/local/share/opencv4/haarcascade_upperbody.xml'

try:
    while True:
        # カメラからフレームを取得
        ret, frame = camera.read()

        if frame is not None:
            try:
                # グレースケールに変換
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # 以下のコード...
            except Exception as e:
                print("エラーが発生しました: ", e)
                # 必要に応じてさらなるエラーハンドリングを行う
        else:
            print("Failed to read frame from camera")

        # グレースケールに変換
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        #人間の検出
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # フレームの幅を3つに分割
        width = frame.shape[1]
        left = width // 3
        center = (width // 3) * 2

        # リアルタイム表示の前準備 枠表示
        for (x,y,w,h) in faces:
            frame = cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]
            face_center = x + w // 2 #face_centerは顔の中心のx座標、しかしfor文内でしか定義できない なぜ？
            
            if face_center < left:
                position = '左'
            elif face_center < center:
                position = '中央'
            else:
                position = '右'

        # リアルタイム表示
        cv2.imshow("frame",frame)

        if len(faces) > 0 & position == '中央':
            # 真っ直ぐ進むプログラム
            func_forward()
            time.sleep(0.5)

        elif len(faces) > 0 & position == '左':
            # 右に旋回するプログラム
            func_right()
            time.sleep(0.5)
            
        elif len(faces) > 0 & position == '右':
            # 左に旋回するプログラム
            func_left()
            time.sleep(0.5)
        else:
            # 右に旋回し続けるプログラム
            func_brake()
            time.sleep(0.5)
            func_right()
            time.sleep(3.0)
            
        
        k =  cv2.waitKey(1) & 0xFF # キー操作取得。64ビットマシンの場合,& 0xFFが必要
        prop_val = cv2.getWindowProperty("frame", cv2.WND_PROP_ASPECT_RATIO) # ウィンドウが閉じられたかを検知する用

        # qが押されるか、ウィンドウが閉じられたら終了
        if k == ord("q") or (prop_val < 0):
            break

        # 1秒待機
        time.sleep(0.5)

except KeyboardInterrupt:
    # プログラム終了時にカメラを解放    
    camera.release()
    cv2.destroyAllWindows()

    #PWM信号を停止
    p_a.stop()
    p_b.stop()

    #GPIOを開放
    GPIO.cleanup()

