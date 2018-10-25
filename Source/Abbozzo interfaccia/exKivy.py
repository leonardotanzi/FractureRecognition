import kivy
kivy.require("1.9.0")
 
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup
 
# Used to display popup
class CustomPopup(Popup):
    pass
 
class SampBoxLayout(BoxLayout):
 
    # For checkbox
    checkbox_is_active = ObjectProperty(False)
    def checkbox_18_clicked(self, instance, value):
        if value is True:
            print("Checkbox Checked")
        else:
            print("Checkbox Unchecked")
 
    # For radio buttons
    blue = ObjectProperty(True)
    red = ObjectProperty(False)
    green = ObjectProperty(False)
 
    # For Switch
    def switch_on(self, instance, value):
        if value is True:
            print("Switch On")
        else:
            print("Switch Off")
 
    # Opens Popup when called
    def open_popup(self):
        the_popup = CustomPopup()
        the_popup.open()
 
    # For Spinner
    def spinner_clicked(self, value):
        print("Spinner Value " + value)
 
 
class SampleApp(App):
    source = '/Users/leonardotanzi/Desktop/Fratture Computer Vision/Jpeg Notevoli/Broken/ok9.jpg'
    outLines = '/Users/leonardotanzi/Desktop/FractureRecognition/OutputFracture/houghLines.jpg'
    outCanny = '/Users/leonardotanzi/Desktop/FractureRecognition/OutputFracture/canny.jpg'
    outGraph = '/Users/leonardotanzi/Desktop/FractureRecognition/OutputFracture/graph.jpg'


    def build(self):
        
        # Set the background color for the window
        Window.clearcolor = (1, 1, 1, 1)
        
        return SampBoxLayout()
 
sample_app = SampleApp()
sample_app.run()
 
