# coding:utf-8
from kivy.app import App
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
from kivy.config import Config

Config.set('kivy','window_icon',r"C:\Users\USER\Codepython\pythonProjectTime\res\inter.png")



class CamApp(App):
    def build(self):
        return


if __name__ == '__main__':
    App().run()