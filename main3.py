from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.progressbar import ProgressBar
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Ellipse, Rectangle
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

class CircularProgressBar(ProgressBar):

    def __init__(self, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)
        Clock.schedule_interval(self.animate, 1)

        # Set constant for the bar thickness
        self.thickness = 38

        # Create a direct text representation
        self.label = CoreLabel(text="0%", font_size=25)

        # Initialise the texture_size variable
        self.texture_size = None

        # Refresh the text
        self.refresh_text()

        # Redraw on innit
        self.draw()

        self._lookTime = ""
        self.turnOn = False
        self.limit = 20
        self.a = 0

    def draw(self):

        with self.canvas:


            # Empty canvas instructions
            self.canvas.clear()

            # Draw no-progress circle
            Color(0.26, 0.26, 0.26)
            Ellipse(pos=self.pos, size=self.size)

            # Draw progress circle, small hack if there is no progress (angle_end = 0 results in full progress)
            Color(0 + self.value_normalized, 1 - self.value_normalized, 0)

            Ellipse(pos=self.pos, size=self.size,
                    angle_end=(0.001 if self.value_normalized == 0 else self.value_normalized * 360))

            # Draw the inner circle (colour should be equal to the background)
            Color(0, 0, 0)
            Ellipse(pos=(self.pos[0] + self.thickness / 2, self.pos[1] + self.thickness / 2),
                    size=(self.size[0] - self.thickness, self.size[1] - self.thickness))

            # Center and draw the progress text
            Color(1, 1, 1, 1)
            # added pos[0]and pos[1] for centralizing label text whenever pos_hint is set
            Rectangle(texture=self.label.texture, size=self.texture_size,
                      pos=(self.size[0] / 2 - self.texture_size[0] / 2 + self.pos[0],
                           self.size[1] / 2 - self.texture_size[1] / 2 + self.pos[1]))


    def refresh_text(self):
        # Render the label
        self.label.refresh()

        # Set the texture size each refresh
        self.texture_size = list(self.label.texture.size)

    def set_value(self, value):
        # Update the progress bar value
        self.value = value

        # Update textual value and refresh the texture
        self.label.text = str(int(self.value_normalized * 100)) + "%"
        self.refresh_text()

        # Draw all the elements
        self.draw()

    def animate(self, dt):
        perCircle = 80

        division = self.limit * 100
        x = (division * perCircle) / division
        limitNormalize = perCircle / (self.limit - .1)

        if self.turnOn:
            if self._lookTime != 0:
                if self.value < x:
                    self.set_value(self.value + limitNormalize)
            else:
                self.set_value(0)
        else:
            self.set_value(0)


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
        self.circularBar = CircularProgressBar()
        # self.remove_widget(self.circularBar)

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
        self.remove_widget(self.circularBar)

        if self.turnOn:
            self.add_widget(self.tabValue)
            self.circularBar._lookTime = _CalculationTime.getLookSecond()
            self.tabValue.textLookTime.text = _CalculationTime.getTimeLook()
            self.tabValue.textStatusRisk.text = _CalculationTime.getStatusText()[0]
            self.tabValue.textGaze.text = str(_CalculationTime.getStatusFace())
            self.tabValue.textModel.text = self.panelModel.nameModel
            self.tabValue.labelTimeProcess.text = f"{_CalculationTime.timeProcessing():.2f} f/s"
            self.add_widget(self.circularBar)

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
        limit = 20
        _CalculationTime.callFrame(frame, self.turnOn, self.panelModel.modelActive, limit)

        # GUI
        self.whenOnStart()
        self.menuFunc()
        self.output.outputFrame(frame)

        # Circle bar
        self.circularBar.turnOn = self.turnOn
        self.circularBar.limit = limit

        # Window size fixed
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
