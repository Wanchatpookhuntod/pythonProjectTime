from kivy.lang.builder import Builder
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.core.window import Window


Window.size = (640 * .7, 680)
# Window.borderless = True

Builder.load_file("UI_demo.kv")


class Main(Widget):
    def __init__(self, **kwargs):
        super(Main, self).__init__(**kwargs)

class DemoApp(App):

    def build(self):
        app = Main()
        return app


if __name__ == '__main__':

    DemoApp().run()

