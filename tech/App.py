from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.metrics import dp
class MyApp(MDApp):

    def build(self):

        return Builder.load_file("interface_design.kv")
    
    def on_start(self):
        pass
    