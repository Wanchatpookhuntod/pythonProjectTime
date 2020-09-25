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
from functools import partial

import videoProcessing as vdo
from videoProcessing import CalculationTime


Window.size = (640 * .7, 680)

# GUI =====================================================

_CalculationTime = CalculationTime()
Builder.load_file("gui.kv")

class FrameToKivy(Image):

    def outputFrame(self, frame):

        buf = vdo.bufFrame(frame)
        image_texture = Texture.create(size=(buf["rows"], buf["cols"]), colorfmt='bgr')
        image_texture.blit_buffer(buf["buf"], colorfmt='bgr', bufferfmt='ubyte')
        self.texture = image_texture

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
    menu = ObjectProperty(None)
    modeBTN = ObjectProperty(None)
    menuPanelModel = ObjectProperty(None)
    btnHAAR = ObjectProperty(None)
    btnHOG = ObjectProperty(None)
    btnDNN = ObjectProperty(None)
    bgPanelModel_1 = ObjectProperty(None)

    def __init__(self, cap, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.cap = cap
        self.output = self.frameToKivy
        self.turnOn = False
        self.menuOn = False
        self.nameModel = "HAAR"
        self.remove_widget(self.menu)
        self.remove_widget(self.menuPanelModel)
        self.modelActive = 0
        self.showBtnMenuOn = True
        self.panelModelOn = False
        self.btnOn = True

    def detect_toggle(self):
        click = self.btnStart.state == "down"
        self.turnOn = True if click else False

    def uiMenuOn(self):
        click = self.btnMenu.state == "down"
        self.menuOn = True if click else False

    def textNameModel(self):
        if self.nameModel:
            self.textModel.text = self.nameModel

    def uiModeModel(self):
        self.menuOn = False
        self.showBtnMenuOn = False
        self.panelModelOn = True
        self.btnOn = False

    def onPressActiveModel(self, x):
        self.modelActive = x

    def swapActiveBtnModel(self, model, down, nor1, nor2):
        if down.state == "down":
            down.state = "down"
            nor1.state = "normal"
            nor2.state = "normal"
            self.nameModel = model
            self.textNameModel()

    def resetPanelModel(self, instance):
        self.panelModelOn = False
        self.showBtnMenuOn = True
        self.btnOn = True
        self.btnMenu.state = "normal"
        self.btnStart.state = "normal"

    def btnModelTask(self):
        self.btnHAAR.bind(on_press=self.resetPanelModel)
        self.btnHAAR.on_press = partial(self.onPressActiveModel, x=0)

        self.btnHOG.bind(on_press=self.resetPanelModel)
        self.btnHOG.on_press = partial(self.onPressActiveModel, x=1)

        self.btnDNN.bind(on_press=self.resetPanelModel)
        self.btnDNN.on_press = partial(self.onPressActiveModel, x=2)


        if self.modelActive == 0:
            self.swapActiveBtnModel(self.btnHAAR.text, self.btnHAAR, self.btnHOG, self.btnDNN)

        elif self.modelActive == 1:
            self.swapActiveBtnModel(self.btnHOG.text, self.btnHOG, self.btnDNN, self.btnHAAR)

        elif self.modelActive == 2:
            self.swapActiveBtnModel(self.btnDNN.text, self.btnDNN, self.btnHAAR, self.btnHOG)



    def addWidget(self):
        if self.showBtnMenuOn:
            self.add_widget(self.btnMenu)

        if self.menuOn:
            self.add_widget(self.menu)

        if self.panelModelOn:
            self.add_widget(self.menuPanelModel)
            self.turnOn = False


        if self.btnOn:
            self.add_widget(self.btnStart)

        if self.turnOn:
            self.add_widget(self.tabValue)
            self.btnStart.center_y = 262
        else:
            self.btnStart.center_y = 200

    def removeWidget(self):
        self.remove_widget(self.menu)
        self.remove_widget(self.btnMenu)
        self.remove_widget(self.menuPanelModel)
        self.remove_widget(self.btnStart)
        self.remove_widget(self.tabValue)

    def update(self, dt):
        frame = self.cap.read()[1]  # <<< start frame app
        _CalculationTime.callFrame(frame, self.turnOn, self.modelActive)

        self.removeWidget()

        self.btnModelTask()

        self.addWidget()

        self.textLookTime.text = _CalculationTime.getTimeLook()
        self.textStatusRisk.text = _CalculationTime.getStatusText()[0]
        self.textGaze.text = str(_CalculationTime.getStatusFace())
        self.textNameModel()
        self.output.outputFrame(frame)

        if Window.size[0] < 640 * .7 or Window.size[1] < 680 or \
                Window.size[0] > 640 * .7 or Window.size[1] > 680:
            Window.size = (640 * .7, 680)

class EyeBreakApp(App):
    capture = vdo.cameraOpen()

    def build(self):
        app = Main(self.capture)
        Clock.schedule_interval(app.update, 1 / 30)
        self.icon = 'graphic/icon_eye_break.png'
        self.background_color = (0, 0, 0, 0)
        return app

    def on_stop(self):
        self.capture.release()

if __name__ == '__main__':
    EyeBreakApp().run()
