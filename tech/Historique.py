from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconLeftWidget, MDList
from kivymd.uix.scrollview import ScrollView

class Historique(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # on attend que le widget soit construit pour remplir la liste
        self.bind(parent=self.populate_list)

    def populate_list(self, *args):
        list_view = self.ids.prestations_list
        for i in range(3):
            item = ThreeLineAvatarIconListItem(
                text=f"Prestation {i+1}",
                secondary_text="Historique d'intervention",
                tertiary_text="Terminé"
            )
            item.add_widget(IconLeftWidget(icon="clock-outline"))
            list_view.add_widget(item)

class TestApp(MDApp):
    def build(self):
        Builder.load_file("historique_template.kv")
        return Historique()

if __name__ == "__main__":
    TestApp().run()