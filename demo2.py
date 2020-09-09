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

faceModel = cv2.CascadeClassifier("res/haarcascade_frontalface_default.xml")

class CalculationTime:

    def __init__(self):
        self.frame = ''
        self.face = ''
        self.status = ''
        self.startTimeFind = time.time()

    def callFrame(self, frame):
        self.frame = frame

    def facedDetect(self, model):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.face = model.detectMultiScale(gray, 1.3, 5)

    def drawFace(self):
        for x, y, w, h in self.face:
            cv2.rectangle(self.frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    def statusFace(self):

        if type(self.face) == tuple:
            self.status = "No Face"
            elapsed_time = 0
            self.startTimeFind = time.time()

        else:
            self.status = "Face"
            elapsed_time = time.time() - self.startTimeFind

        print(f'{self.status} {time.strftime("%H:%M:%S", time.gmtime(elapsed_time))}')

    def startTimeNoFind(self):
        if self.status == "No Face":
            self.startHideFace = time.time()



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
        Clock.schedule_interval(app.update, 1/30)
        self.icon = 'res/icon.ico'
        return app

    def on_stop(self):
        self.cap.release()


if __name__ == '__main__':
    EyeBreakApp().run()
