from random import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Color, Ellipse, Line
from kivy.core.window import Window
import win32api, win32con, win32gui
class MyPaintWidget(Widget):
    
    
    
    def __init__(self):
        super(MyPaintWidget, self).__init__()
        self.writing = False

        #Window.bind(mouse_pos=self.my_callback)
      

    def draw(self,ud):
        (x,y) = win32api.GetCursorPos()
        ud['line'] = Line(points=(x,y))
        
    def on_touch_down(self, touch):
        # get cursos position
        (x,y) = win32api.GetCursorPos()
    
           
        if touch.is_double_tap:
            self.toggleWriting()
        if self.writing == True:
                color = (random(), 1, 1)
                with self.canvas:
                    Color(*color, mode='hsv')
                    d = 5.
                    Ellipse(pos=(touch.x - d / 2, touch.y - d / 2), size=(d, d))
                    touch.ud['line'] = Line(points=(x,y))

    def on_touch_move(self, touch):
        if self.writing == True:
            (x,y) = win32api.GetCursorPos()
            touch.ud['line'].points += [x, y]
    def my_callback(self,instance,value):
         if self.writing == True:
            #instance.ud['line'].points += [instance.x, instance.y]
            pass
  
    def toggleWriting(self):
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