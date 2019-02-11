from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window


class MyPaintWidget(Widget):

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.start(self)


    def start(self):
  	while True:
            with self.canvas:
                color = (2, 1, 1)
                Color(*color, mode='hsv')
                d = 2.
                Ellipse(pos=(Window.mouse_pos[0], Window.mouse_pos[1]), size=(d, d))

    def __init__(self, **kwargs):
        self.writing = False
        Window.bind(mouse_pos=self.update_pos)
        super(MyPaintWidget, self).__init__(**kwargs)

    def togglewriting(self):
        if self.writing == True:
            self.writing = False
        else:
            self.writing = True

class MyPaintApp(App):

    def build(self):
        parent = Widget()
        painter = MyPaintWidget()
        clearbtn = Button(text='Clear')
        parent.add_widget(painter)
        parent.add_widget(clearbtn)

        def clear_canvas(obj):
            painter.canvas.clear()
        clearbtn.bind(on_release=clear_canvas)

        return parent


if __name__ == '__main__':
    MyPaintApp().run()

