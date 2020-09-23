from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button


class TutorialApp(App):
    def gratulation(self, *args):
        print(args)

    def build(self):
        boxLayout = BoxLayout(spacing=10,orientation='vertical')
        g = TextInput(text='Enter gratulation',
                      multiline=False,
                      font_size=20,
                      height=100)
        button = Button(text='Send')
        button.bind(on_press=self.gratulation)

        boxLayout.add_widget(g)
        boxLayout.add_widget(button)
        return boxLayout

if __name__ == "__main__":
    TutorialApp().run()