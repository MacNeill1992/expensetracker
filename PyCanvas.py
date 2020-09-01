from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle, Color
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex


class pythoncanvas(FloatLayout):
    def __init__(self, hex_color, **kwargs):
        super(pythoncanvas, self).__init__(**kwargs)
        self.size_hint_y = 0.15
        with self.canvas:
            back_color = hex_color
            Color(rgb=get_color_from_hex(back_color))
            self.rect = Rectangle(pos=self.pos, size=self.size)
            self.bind(pos=self.update_rect)
            self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
