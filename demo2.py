from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from kivy.lang.builder import Builder
import cv2
import time
from win10toast import ToastNotifier
from functools import partial

faceModel = cv2.CascadeClassifier('res/haarcascade_frontalface_default.xml')
toaster = ToastNotifier()



Window.size = (640 * .7, 680)

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

    def callFrame(self, frame, turnOn, model):
        self.frame = frame
        self.turnOn = turnOn
        self.model = model

        if self.turnOn:
            self.facedDetect()
            self.drawFace()
            self.statusFace()
        else:
            self.resetValue()


    def facedDetect(self):
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        self.face = self.model.detectMultiScale(gray, 1.3, 5)

    def drawFace(self):
        for x, y, w, h in self.face:
            cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 54, 118), 2)

    def statusFace(self):
        if self.face != ():  # พบใบหน้า
            self.status = True
            self.lookCom = time.time() - self.startFace

            self.startNoFace = time.time()
            self.noLookCom = 0

        else:
            self.status = False  # ไม่พบใบหน้า
            self.noLookCom = time.time() - self.startNoFace

            if self.noLookCom > self.rateReset:
                self.lookCom = 0
                self.startFace = time.time()

        self.timeLook = time.strftime("%H:%M:%S", time.gmtime(self.lookCom))

        self.lookHour, self.lookMin, self.lookSecond = time.gmtime(self.lookCom)[3:6]

        if self.lookMin > self.breakMin:
            print("Pop up 15 sec.")

        if self.lookSecond > 10:
            toaster.show_toast(title=f"{self.titlePopup} !!!",
                               msg=f"{self.msgPopup} {self.timeLook} .\n"
                                   f"So you should rest your eyes for 15 seconds..",
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

# GUI ============================

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

class LineInBOX(Widget):
    pass

class MenuPanelModel(Widget):
    pass

class BtnModeModel(ToggleButton):
    pass

class Main(Widget):
    frameToKivy = ObjectProperty(None)
    textLookTime = ObjectProperty(None)
    textStatusRisk = ObjectProperty(None)
    textGaze = ObjectProperty(None)
    btnStart = ObjectProperty(None)
    tabValue = ObjectProperty(None)
    textModel = ObjectProperty(None)
    btnMenu = ObjectProperty(None)
    widgetBtnMenu = ObjectProperty(None)
    menu = ObjectProperty(None)
    modeBTN = ObjectProperty(None)
    menuPanelModel = ObjectProperty(None)
    btnHAAR = ObjectProperty(None)
    btnHOG = ObjectProperty(None)
    btnDNN = ObjectProperty(None)
    btnYOLO = ObjectProperty(None)




    def __init__(self, cap, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.cap = cap
        self.output = self.frameToKivy
        self.turnOn = False
        self.menuOn = False
        # self.remove_widget(self.panelModel)
        self.nameModel = "HAAR"
        self.remove_widget(self.menu)
        self.remove_widget(self.menuPanelModel)
        self.modelActive = 0

    def detect_toggle(self):
        click = self.btnStart.state == "down"
        self.turnOn = True if click else False

    def uiStart(self):
        self.uiTurnOff()

        if self.turnOn:
            self.uiTurnOn()

    def uiTurnOn(self):
        self.add_widget(self.tabValue)
        self.btnStart.center_y = 262

    def uiTurnOff(self):
        self.remove_widget(self.tabValue)
        self.btnStart.center_y = 200

    def uiMenu(self):
        if self.menuOn:
            self.add_widget(self.menu)
        else:
            self.remove_widget(self.menu)

    def uiMenuToggle(self):
        click = self.btnMenu.state == "down"
        self.menuOn = True if click else False
        self.uiMenu()

    def btnModel(self):
        self.remove_widget(self.menu)
        self.add_widget(self.widgetBtnMenu)


    def textNameModel(self):
        if self.nameModel:
            self.textModel.text = self.nameModel

    def uiModeModel(self):
        self.add_widget(self.menuPanelModel)
        self.remove_widget(self.widgetBtnMenu)
        self.remove_widget(self.menu)

    def onPressActiveModel(self, x):
        self.modelActive = x

    def dis(self):
        if self.closeMenu:
            self.add_widget(self.menu)

    def swapActiveBtnModel(self, model, down, nor1, nor2, nor3):
        if down.state == "down":
            down.state = "down"
            nor1.state = "normal"
            nor2.state = "normal"
            nor3.state = "normal"
            self.nameModel = model
            self.textNameModel()
            self.remove_widget(self.menuPanelModel)
            self.uiMenu()


    def btnModelTask(self):
        self.btnHAAR.on_press = partial(self.onPressActiveModel, x=1)
        self.btnHOG.on_press = partial(self.onPressActiveModel, x=2)
        self.btnDNN.on_press = partial(self.onPressActiveModel, x=3)
        self.btnYOLO.on_press = partial(self.onPressActiveModel, x=4)

        if self.modelActive == 1:
            self.swapActiveBtnModel("HAAR", self.btnHAAR, self.btnHOG, self.btnDNN, self.btnYOLO)
            self.add_widget(self.menu)

        elif self.modelActive == 2:
            self.swapActiveBtnModel("HOG", self.btnHOG, self.btnDNN, self.btnYOLO, self.btnHAAR)

        elif self.modelActive == 3:
            self.swapActiveBtnModel("DNN", self.btnDNN, self.btnYOLO, self.btnHAAR, self.btnHOG)

        elif self.modelActive == 4:
            self.swapActiveBtnModel("YOLO", self.btnYOLO, self.btnHAAR, self.btnHOG, self.btnDNN)
        else:
            pass

    def update(self, dt):
        frame = self.cap.read()[1]  # <<< start frame app
        _CalculationTime.callFrame(frame, self.turnOn, faceModel)

        self.uiStart()
        self.btnModelTask()

        self.textLookTime.text = _CalculationTime.getTimeLook()
        self.textStatusRisk.text = _CalculationTime.getStatusText()[0]
        self.textGaze.text = str(_CalculationTime.getStatusFace())
        self.textNameModel()
        self.output.outputFrame(frame)

        if Window.size[0] < 640 * .7 or Window.size[1] < 680 or \
                Window.size[0] > 640 * .7 or Window.size[1] > 680:
            Window.size = (640 * .7, 680)

class EyeBreakApp(App):

    def build(self):
        self.cap = cv2.VideoCapture(0)
        app = Main(self.cap)
        Clock.schedule_interval(app.update, 1 / 30)
        self.icon = 'graphic/icon_eye_break.png'
        self.background_color = (0, 0, 0, 0)
        return app

    def on_stop(self):
        self.cap.release()

if __name__ == '__main__':
    EyeBreakApp().run()
