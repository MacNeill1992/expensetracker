from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.uix.screenmanager import SlideTransition, NoTransition
from kivy.uix.button import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle, Ellipse, Line
import kivy.utils
from expense_by_month import ExpenseByMonth
from expense_by_category import ExpenseByCategory
from kivy.config import Config
from kivy.properties import StringProperty
from myfirebase import MyFirebase
import traceback
from os import walk
# Config.set('graphics', 'width', '260')
# Config.set('graphics', 'height', '480')
import requests
import json
from functools import partial
from datetime import datetime
import certifi

class LoginScreen(Screen):
    pass

class AddExpenseScreen(Screen):
    pass

class Connected(Screen):
    pass

class ExpenseScreen(Screen):
    pass

class CategoryScreen(Screen):
    pass

class SettingsScreen(Screen):
    pass

class ImageButton(ButtonBehavior, Image):
    pass

class LabelButton(ButtonBehavior, Label):
    pass

#########DEL###########
class Screen1(Screen):
    pass
class Screen2(Screen):
    pass
#########DEL############


GUI = Builder.load_file("main.kv")
class MainApp(App):
    user_id = 1
    category_image = None
    category_image_widget = ''
    previous_category_image_widget = None
    refresh_token_file = "refresh_token.txt"

    def build(self):
        self.my_firebase = MyFirebase()
        return GUI
#######UP TO DATE ^^^^######
    def on_start(self):
        try:
            with open("refresh_token.txt", 'r') as f:
                refresh_token = f.read()
            id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token
            # Get database data
            result = requests.get("https://expensetracker-d3a98.firebaseio.com/" + local_id + ".json?auth=" + id_token)
            data = json.loads(result.content.decode())

            self.change_screen("connected")

        except Exception:
            print("EXCEPTION")
            traceback.print_exc()
            print("EXCEPTION")
            pass

    def change_screen(self, screen_name):
        screen_manager = self.root.ids['screen_manager']
        screen_manager.current = screen_name

    def connected_change_screen(self, screen_name):
        screen_manager = self.root.ids['connected'].ids['connected_screen_manager']
        screen_manager.current = screen_name

MainApp().run()

