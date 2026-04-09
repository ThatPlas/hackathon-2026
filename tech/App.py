from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, IconRightWidget
from kivy.metrics import dp
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty
from kivymd.uix.fitimage import FitImage

from Historique import Historique

class MyApp(MDApp):

    def build(self):
        return Builder.load_file("interface_design.kv")

    def show_date_picker(self, focus):
        if focus:
            date_dialog = MDDatePicker()
            date_dialog.open()
    def show_date_picker(self, focus):
        if focus:
            date_dialog = MDDatePicker()
            date_dialog.bind(on_save=self.on_save_date)
            date_dialog.open()  

    def on_save_date(self, instance, value, date_range):
        self.root.ids.field.text = str(value)
    