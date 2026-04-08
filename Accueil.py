from kivy.core.window import Window
Window.size = (360, 740)

from kivy.lang import Builder
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.navigationbar import MDNavigationBar, MDNavigationItem
from kivymd.uix.screen import MDScreen


class BaseMDNavigationItem(MDNavigationItem):
    icon = StringProperty()
    text = StringProperty()


class BaseScreen(MDScreen):
    image_size = StringProperty()


KV = '''
<BaseMDNavigationItem>

    MDNavigationItemIcon:
        icon: root.icon

    MDNavigationItemLabel:
        text: root.text

<BaseScreen>
    FitImage:
        source: f"logo.png"
        size_hint: .5, .125
        pos_hint: {"center_x": .5, "center_y": .925}


MDBoxLayout:
    orientation: "vertical"
    md_bg_color: self.theme_cls.backgroundColor

    MDScreenManager:
        id: screen_manager

        BaseScreen:
            name: "Recherche"
            image_size: "1024"

        BaseScreen:
            name: "Accueil"
            image_size: "800"

        BaseScreen:
            name: "Profil"
            image_size: "600"


    MDNavigationBar:
        on_switch_tabs: app.on_switch_tabs(*args)
        radius: dp(24)

        BaseMDNavigationItem
            icon: "magnify"
            text: "Recherche"

        BaseMDNavigationItem
            icon: "home"
            text: "Accueil"
            active: True

        BaseMDNavigationItem
            icon: "account"
            text: "Profil"
'''


class Example(MDApp):
    def on_switch_tabs(
        self,
        bar: MDNavigationBar,
        item: MDNavigationItem,
        item_icon: str,
        item_text: str,
    ):
        self.root.ids.screen_manager.current = item_text

    def build(self):
        self.theme_cls.primary_palette = "#7A2850"
        return Builder.load_string(KV)


Example().run()