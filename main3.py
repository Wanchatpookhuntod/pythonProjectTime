from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.core.window import Window
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import ObjectProperty
from functools import partial

from kivy.lang import Builder
import videoProcessing as vdo

from videoProcessing import CalculationTime

_CalculationTime = CalculationTime()
Window.size = (640 * .7, 680)
Builder.load_file("gui3.kv")

class FrameToKivy(Image):
    def outputFrame(self, frame):
        buf = vdo.bufFrame(frame)
        image_texture = Texture.create(size=(buf["rows"], buf["cols"]), colorfmt='bgr')
        image_texture.blit_buffer(buf["buf"], colorfmt='bgr', bufferfmt='ubyte')
        self.texture = image_texture

class TabValue(Widget):
    pass

class Menu(Widget):
    pass

class BtnMenu(Widget):
    pass

class BtnStart(Widget):
    pass

class PanelModel(Widget):
    btnHAAR = ObjectProperty(None)
    btnHOG = ObjectProperty(None)
    btnDNN = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PanelModel, self).__init__(**kwargs)
        Clock.schedule_interval(self.update, 1 / 30)
        self.modelActive = 0
        self.nameModel = ""

    def onPressActiveModel(self, x):
        self.modelActive = x

    def swapActiveBtnModel(self, model, down, nor1, nor2):
        if down.state == "down":
            down.state = "down"
            nor1.state = "normal"
            nor2.state = "normal"
            self.nameModel = model

        if self.btnHAAR.state == "normal" and self.btnHOG.state == "normal" and self.btnDNN.state == "normal":
            self.btnHAAR.state = "down"
            self.nameModel = self.btnHAAR.text

    def btnModelTask(self):
        self.btnHAAR.on_press = partial(self.onPressActiveModel, x=0)
        self.btnHOG.on_press = partial(self.onPressActiveModel, x=1)
        self.btnDNN.on_press = partial(self.onPressActiveModel, x=2)

        if self.modelActive == 0:
            self.swapActiveBtnModel(self.btnHAAR.text, self.btnHAAR, self.btnHOG, self.btnDNN)

        elif self.modelActive == 1:
            self.swapActiveBtnModel(self.btnHOG.text, self.btnHOG, self.btnDNN, self.btnHAAR)

        elif self.modelActive == 2:
            self.swapActiveBtnModel(self.btnDNN.text, self.btnDNN, self.btnHAAR, self.btnHOG)

        else:
            pass

    def update(self, dt):
        self.btnModelTask()


class Main(Widget):
    frameToKivy = ObjectProperty(None)
    btnStart = ObjectProperty(None)
    menu = ObjectProperty(None)

    def __init__(self, cap, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.cap = cap
        self.output = self.frameToKivy
        self.turnOn = False

        self.tabValue = TabValue()

        self.btnMenu = BtnMenu()
        self.add_widget(self.btnMenu)

        self.btnStart = BtnStart()
        self.add_widget(self.btnStart)
        self.btnStart.btn.bind(on_press=self.detect_toggle)

        self.panelModel = PanelModel()
        self.remove_widget(self.panelModel)
        self.panelModel.btnClosedPanelModel.bind(on_press=self.cbClosePanelModel)

        self.menuGUI = Menu()
        self.menuGUI.modelBTN.bind(on_press=self.cbPanelModel)

    def whenOnStart(self):
        self.remove_widget(self.tabValue)
        if self.turnOn:
            self.add_widget(self.tabValue)
            self.tabValue.textLookTime.text = _CalculationTime.getTimeLook()
            self.tabValue.textStatusRisk.text = _CalculationTime.getStatusText()[0]
            self.tabValue.textGaze.text = str(_CalculationTime.getStatusFace())
            self.tabValue.textModel.text = self.panelModel.nameModel
            self.tabValue.labelTimeProcess.text = f"{_CalculationTime.timeProcessing():.2f} f/s"

    def detect_toggle(self, instance):
        if self.btnStart.btn.state == "down":
            self.turnOn = True
            self.btnStart.btn.center_y = 262
        else:
            self.turnOn = False
            self.btnStart.btn.center_y = 200

    def menuFunc(self):
        self.remove_widget(self.menuGUI)
        if self.btnMenu.btnMenuToggle.state == "down":
            self.add_widget(self.menuGUI)

    def cbPanelModel(self, instance):
        self.add_widget(self.panelModel)
        self.btnMenu.btnMenuToggle.state = "normal"
        self.remove_widget(self.btnMenu)
        self.remove_widget(self.btnStart)

        # set button start
        self.turnOn = False
        self.btnStart.btn.state = "normal"
        self.btnStart.btn.center_y = 200

    def cbClosePanelModel(self, instance):
        self.remove_widget(self.panelModel)
        self.add_widget(self.btnMenu)
        self.add_widget(self.btnStart)

        # set button start
        self.turnOn = True
        self.btnStart.btn.state = "down"
        self.btnStart.btn.center_y = 262

    def update(self, dt):
        frame = self.cap.read()[1]
        _CalculationTime.callFrame(frame, self.turnOn, self.panelModel.modelActive)
        self.whenOnStart()
        self.menuFunc()
        self.output.outputFrame(frame)

        if Window.size[0] < 640 * .7 or Window.size[1] < 680 or \
                Window.size[0] > 640 * .7 or Window.size[1] > 680:
            Window.size = (640 * .7, 680)


class TestApp(App):
    capture = vdo.cameraOpen()

    def build(self):
        app = Main(self.capture)
        Clock.schedule_interval(app.update, 1 / 30)
        self.icon = 'graphic/icon_eye_break.png'
        return app

if __name__ == '__main__':
    TestApp().run()
