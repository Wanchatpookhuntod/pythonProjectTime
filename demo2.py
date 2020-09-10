from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.lang.builder import Builder
from kivy.uix.popup import Popup
from kivy.config import Config
import cv2
import numpy as np
import time

from win10toast import ToastNotifier

faceModel = cv2.CascadeClassifier("res/haarcascade_frontalface_default.xml")
toaster = ToastNotifier()


class CalculationTime:

    def __init__(self):
        self.frame = ''
        self.face = ''
        self.status = ''
        self.startFace = time.time()
        self.startNoFace = time.time()
        self.lookCom = 0
        self.dontLookCom = 0
        self.rateReset = 3
        self.breakMin = 20
        self.breakHour = 2

    def callFrame(self, frame):
        self.frame = frame

    def facedDetect(self, model):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.face = model.detectMultiScale(gray, 1.3, 5)

    def drawFace(self):
        for x, y, w, h in self.face:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    def statusFace(self):

        if self.face != ():  # พบใบหน้า
            self.status = True
            self.lookCom = time.time() - self.startFace

            self.startNoFace = time.time()
            self.dontLookCom = 0

        else:
            self.status = False  # ไม่พบใบหน้า
            self.dontLookCom = time.time() - self.startNoFace

            if self.dontLookCom > self.rateReset:
                self.lookCom = 0
                self.startFace = time.time()

        print(f'Face:{self.status} Look Time: {time.strftime("%H:%M:%S", time.gmtime(self.lookCom))}')
        loookHour, lookMin, lookSecond = time.gmtime(self.lookCom)[3:6]

        if lookMin > self.breakMin:
            print("Pop up 15 sec.")

        if lookSecond > 10:
            notic = toaster.show_toast(title="You Risk!!!",
                                        msg="you look computer more 15 min",
                                        icon_path="graphic/icon.ico",
                                        duration=5,
                                        threaded=True)


_CalculationTime = CalculationTime()

Builder.load_file("gui.kv")


class FrameToKivy(Image):

    def outputFrame(self, frame):
        cols = frame.shape[0]
        rows = frame.shape[1]
        buf1 = cv2.flip(frame, 0)
        buf = buf1.tostring()
        image_texture = Texture.create(size=(rows, cols), colorfmt='bgr')
        image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        self.texture = image_texture


class Main(Widget):
    frameToKivy = ObjectProperty(None)
    textLookTime = StringProperty("")

    def __init__(self, cap, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.cap = cap
        self.output = self.frameToKivy

    def update(self, dt):
        frame = self.cap.read()[1]  # <<< start frame app

        _CalculationTime.callFrame(frame)
        _CalculationTime.facedDetect(faceModel)
        _CalculationTime.drawFace()
        _CalculationTime.statusFace()

        self.output.outputFrame(frame)


class EyeBreakApp(App):

    def build(self):
        self.cap = cv2.VideoCapture(0)
        app = Main(self.cap)
        Clock.schedule_interval(app.update, 1 / 30)
        self.icon = 'graphic/icon_eye_break.png'
        return app

    def on_stop(self):
        self.cap.release()


if __name__ == '__main__':
    EyeBreakApp().run()
