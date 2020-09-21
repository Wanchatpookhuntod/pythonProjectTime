import kivy.properties
from kivy.lang.builder import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window
import random


Window.size = (640 * .7, 680)
Window.left = 600

# Window.borderless = True

Builder.load_file("UI_demo.kv")


class Main(Widget):
    statusRisk = kivy.properties.ObjectProperty(None)
    btnStart = kivy.properties.ObjectProperty(None)
    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)
        l = random.randint(0, 500)
        Window.left = l


        print(l)


class DemoApp(App):

    def build(self):
        app = Main()
        return app


if __name__ == '__main__':

    DemoApp().run()

