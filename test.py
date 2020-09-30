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
from kivy.uix.screenmanager import ScreenManager, Screen
import videoProcessing as vdo

from videoProcessing import CalculationTime

_CalculationTime = CalculationTime()
Window.size = (640 * .7, 680)
Builder.load_file("UI_demo.kv")

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

class Main(Screen, Widget):
    frameToKivy = ObjectProperty(None)
    btnStart = ObjectProperty(None)
    textLookTime = ObjectProperty(None)
    textStatusRisk = ObjectProperty(None)
    textGaze = ObjectProperty(None)
    textModel = ObjectProperty(None)
    btnMenuToggle = ObjectProperty(None)
    menu = ObjectProperty(None)
    modeBTN = ObjectProperty(None)
    # labelTimeProcess = ObjectProperty(None)
    # tabValue = ObjectProperty(None)

    def __init__(self, cap, **kwargs):
        super(Main, self).__init__(**kwargs)
        self.cap = cap
        self.output = self.frameToKivy
        self.turnOn = False
        self.tabValue = TabValue()
        self.btnMenu = BtnMenu()
        self.menuGUI = Menu()
        Clock.schedule_interval(self.update, 1 / 30)
        self.add_widget(self.btnMenu)





    def whenOnStart(self):
        self.remove_widget(self.tabValue)

        if self.turnOn:
            self.tabValue.textLookTime.text = _CalculationTime.getTimeLook()
            self.tabValue.textStatusRisk.text = _CalculationTime.getStatusText()[0]
            self.tabValue.textGaze.text = str(_CalculationTime.getStatusFace())
            self.add_widget(self.tabValue)
            self.tabValue.labelTimeProcess.text = f"{_CalculationTime.timeProcessing():.2f} f/s"


    def detect_toggle(self):
        self.turnOn = True if self.btnStart.state == "down" else False
        self.btnStart.center_y = 262 if self.turnOn else 200

    def menuFunc(self):
        self.remove_widget(self.menuGUI)

        if self.btnMenu.btnMenuToggle.state == "down":
            self.add_widget(self.menuGUI)


    def update(self, dt):
        frame = self.cap.read()[1]
        _CalculationTime.callFrame(frame, self.turnOn, 0)

        # self.whenOffStart()
        self.whenOnStart()
        self.menuFunc()

        self.output.outputFrame(frame)

class SettingsScreen(Screen):
    pass

capture = vdo.cameraOpen()

sm = ScreenManager()
sm.add_widget(Main(cap=capture, name='menu'))
sm.add_widget(SettingsScreen(name='settings'))

class TestApp(App):

    def build(self):
        return sm

if __name__ == '__main__':
    TestApp().run()
