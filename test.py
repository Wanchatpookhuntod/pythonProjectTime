from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.button import Button

class MyLayout(BoxLayout):
    pass

class HoverButton(Button):
    def __init__(self, **kwargs):
        # Call the initialization function of the parent class
        super(HoverButton, self).__init__(**kwargs)
        # Set the control to fill horizontally and set the height vertically
        self.size_hint = (1, None)
        self.height = 50
        # binding[subscribe]Event handling method of mouse position change
        Window.bind(mouse_pos=self.on_mouse_pos)
        Window.set_system_cursor('arrow')

   # Mouse position processing method
    def on_mouse_pos(self, *args):
        # Determine whether the control is in root In root control
        if not self.get_root_window():
           return
        # Get mouse position data
        pos = args[1]
        # Check whether the mouse position is in the control
        if self.collide_point(*pos):
           # If on a control, the style method entered by the mouse is called
           Clock.schedule_once(self.mouse_enter_css, 0)
        else:
           # If on a control, the style method of mouse out is called
           Clock.schedule_once(self.mouse_leave_css, 0)

    def mouse_leave_css(self, *args):
        # Reset background and mouse style
        self.background_normal = 'res/btn_1.png'
        Window.set_system_cursor('arrow')

    def mouse_enter_css(self, *args):
        Window.set_system_cursor('hand')
        self.background_normal = 'res/btn_2.png'

class MainApp(App):
    def build(self):
        # Form not full screen
        Window.fullscreen = False

        # load kv File layout data
        Builder.load_file('demoGUI.kv')
        # return root Root control
        return MyLayout()


if __name__ == '__main__':
    MainApp().run()