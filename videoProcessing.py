import cv2
from win10toast import ToastNotifier
import time
import dlib
import numpy as np

def cameraOpen(idx=0):
    cap = cv2.VideoCapture(idx)
    return cap

def bufFrame(frame):
    cols = frame.shape[0]
    rows = frame.shape[1]
    buf1 = cv2.flip(frame, 0)
    buf = buf1.tostring()
    return {"rows": rows, "cols": cols, "buf": buf}

def ecoFrame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return gray

haarModel = cv2.CascadeClassifier('res/haarcascade_frontalface_default.xml')

hogModel = dlib.get_frontal_face_detector()

lbpModel = ""

f_txt = "res/opencv_face_detector.pbtxt"
f_pb = "res/opencv_face_detector_uint8.pb"
deepModel = cv2.dnn.readNetFromTensorflow(f_pb, f_txt)

processingTime = lambda x: (cv2.getTickCount() - x) / cv2.getTickFrequency() * 1000

def dnnPredict(img, model):
    rows = img.shape[0]
    cols = img.shape[1]

    model.setInput(cv2.dnn.blobFromImage(img, size=(300, 300), swapRB=True, crop=False))
    face_Out = model.forward()
    # face = []
    for detection in face_Out[0, 0, :, :]:
        score = float(detection[2])
        if score < 0.6:
            continue
        box = detection[3:7] * np.array([cols, rows, cols, rows])
        return box


toaster = ToastNotifier()

class CalculationTime:

    def __init__(self):
        self.frame = ''
        self.face = ''
        self.status = ''
        self.startFace = time.time()
        self.startNoFace = time.time()
        self.lookCom = 0
        self.noLookCom = 0
        self.rateReset = 3
        self.breakMin = 20
        self.breakHour = 2
        self.timeLook = ""
        self.popUpStatus = ""
        self.statusRisk = True
        self.titlePopup = "EYE RISK"
        self.msgPopup = "Your gaze at the screen for"
        self.statusNormal = "NORMAL"
        self.popProtect = ""
        self.turnOn = ""
        self.model = ""
        self.processing_time = 0
        self.lookSecond = 0
        self.eyeBreakSec = 0
        self.eco = False
        self.total = 0
        self.numberBreak = 0
        self.a = 0
        self.go = False


    def callFrame(self, frame, turnOn, modelActive, limit, eco):
        self.frame = frame
        self.turnOn = turnOn
        self.modelActive = modelActive
        self.eyeBreakSec = limit
        self.eco = eco

        if self.turnOn:
            self.facedDetect()
            self.drawFace()
            self.statusFace()
        else:
            self.resetValue()
            self.processing_time = 0


    def facedDetect(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.predictStart = cv2.getTickCount()

        if self.modelActive == 0:  # haar model

            self.face = haarModel.detectMultiScale(gray, 1.3, 5)

        elif self.modelActive == 1:  # hog model
            self.face = hogModel(gray, 0)

        elif self.modelActive == 2:  # deep model
            self.face = dnnPredict(self.frame, deepModel)
            if self.face is None:
                self.face = ()

        self.predictEnd = cv2.getTickCount()
        self.processing_time = ((self.predictEnd - self.predictStart) / cv2.getTickFrequency())

    def timeProcessing(self):
        return self.processing_time

    def drawFace(self):
        if not self.eco:
            color = (255, 0, 106)
        else:
            color = (0, 0, 0)

        if self.modelActive == 0:
            for x, y, w, h in self.face:
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), color, 2)

        elif self.modelActive == 1:
            for det in self.face:
                xy = det.left(), det.top()
                wh = det.right(), det.bottom()
                cv2.rectangle(self.frame, xy, wh, color, 2)

        elif self.modelActive == 2:
            if self.face != ():
                (left, top, right, bottom) = self.face.astype("int")

                origin_w_h = bottom - top
                top = int(top + (origin_w_h) * 0.15)
                bottom = int(bottom - (origin_w_h) * 0.05)
                margin = ((bottom - top) - (right - left)) // 2
                left = left - margin if (bottom - top - right + left) % 2 == 0 else left - margin - 1
                right = right + margin

                cv2.rectangle(self.frame, (left, top), (right, bottom), color, 2)


    def statusFace(self):
        # if self.face != ():  # พบใบหน้า
        #     self.status = True
        #     self.lookCom = time.time() - self.startFace  # จับเวลามองจอ
        #     self.noLookCom = 0  # reset เวลาไม่มองจอ
        #     self.startNoFace = time.time()  # reset การเริ่มไม่มองจอ
        #
        # else:
        #     self.status = False
        #     self.noLookCom = time.time() - self.startNoFace  # จับไม่เวลามองจอ
        #
        #     if self.noLookCom > self.rateReset:  # ถ้าเวลาไม่มองจอมากกว่าเวลา reset
        #         self.lookCom = 0  # reset เวลาไมองจอ
        #         self.startFace = time.time()  # reset การเริ่มมองจอ
        #     else:  # ถ้าเวลาไม่มองจอยังไม่ถึงเวลา reset ก็ยังจับเวลามองจอต่อไป
        #         self.lookCom = time.time() - self.startFace

        # if self.lookCom > self.eyeBreakSec and self.noLookCom > self.rateReset:
        #     self.x += 1
        #
        # print(f"{self.lookCom} > {self.eyeBreakSec} and {self.noLookCom} > {self.rateReset}")

        if self.numberBreak > 5:
            self.numberBreak = 0

        if self.face != ():  # พบใบหน้า
            self.status = True
            self.lookCom = time.time() - self.startFace  # จับเวลามองจอ
            self.noLookCom = 0  # reset เวลาไม่มองจอ
            self.startNoFace = time.time()  # reset การเริ่มไม่มองจอ

        else:
            self.status = False
            self.noLookCom = time.time() - self.startNoFace  # จับไม่เวลามองจอ

            if self.noLookCom > self.rateReset:  # ถ้าเวลาไม่มองจอมากกว่าเวลา reset

                if self.lookCom > self.eyeBreakSec:
                    self.numberBreak += 1

                self.lookCom = 0  # reset เวลาไมองจอ
                self.startFace = time.time()  # reset การเริ่มมองจอ
            else:  # ถ้าเวลาไม่มองจอยังไม่ถึงเวลา reset ก็ยังจับเวลามองจอต่อไป
                self.lookCom = time.time() - self.startFace

        if self.numberBreak > 5 and self.lookCom > self.eyeBreakSec:
            self.numberBreak = 0

        print(self.numberBreak)

        self.timeLook = time.strftime("%H:%M:%S", time.gmtime(self.lookCom))
        self.timeNotLook = time.strftime("%H:%M:%S", time.gmtime(self.noLookCom))

        self.lookHour, self.lookMin, self.lookSecond = time.gmtime(self.lookCom)[3:6]


        # print(self.timeLook, self.timeNotLook)

        if self.numberBreak > 5:
            print("Your look at com for 2 hour.")

        if self.lookCom > self.eyeBreakSec:
            toaster.show_toast(title=f"{self.titlePopup} !!!",
                               msg=f"{self.msgPopup} {self.timeLook} .\n"
                                   f"So you should take a 20 second break\n"
                                   f"to view something 20 feet for 20 sec.",
                               icon_path="graphic/icon.ico",
                               duration=5,
                               threaded=True)

            self.popUpStatus = self.titlePopup
            self.popProtect = "So you should rest your eyes for 15 seconds..."
            self.statusRisk = False
        else:
            self.popUpStatus = self.statusNormal
            self.popProtect = ""
            self.statusRisk = True

    def resetValue(self):
        self.lookCom = 0
        self.noLookCom = 0
        self.startNoFace = time.time()
        self.startFace = time.time()
        self.timeLook = ""
        self.popUpStatus = ""
        self.popProtect = ""
        self.status = ""

    def getTimeLook(self):
        return self.timeLook

    def getStatusText(self):
        return self.popUpStatus, self.popProtect

    def getStatusFace(self):
        return self.status

    def getLookSecond(self):
        return self.lookCom
