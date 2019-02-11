from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from DrawWidget import DrawWidget
class DrawApp(App):
    def build(self):
        parent = Widget()
        painter = DrawWidget()
        clearbtn = Button(text='Clear')
        parent.add_widget(painter)
        parent.add_widget(clearbtn)
        
        def clear_canvas(obj):
            painter.canvas.clear()
        clearbtn.bind(on_release=clear_canvas)
        
        return parent
    
if __name__ == '__main__':
    from kivy.core.window import Window
    Window.fullscreen = 'auto'
    DrawApp().run()
             