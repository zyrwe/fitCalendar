import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import MDFloatingActionButton

kivy.require('2.1.0')


class FitLayout(Widget):
    pass


class FitCalendarApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepPurple"
        return FitLayout()


if __name__ == '__main__':
    FitCalendarApp().run()
