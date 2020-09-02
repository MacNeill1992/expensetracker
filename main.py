from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.config import Config
from myfirebase import MyFirebase
import json
import traceback
import requests
# Config.set('graphics', 'width', '500')
# Config.set('graphics', 'height', '850')

class LoginScreen(Screen):
    pass

class Screen1(Screen):
    pass

class Screen2(Screen):
    pass

class Connected(Screen):
    pass


GUI = Builder.load_file("main.kv")
# LOGIN = Builder.load_file("loginscreen.kv")

class MainApp(App):

    def build(self):
        self.my_firebase = MyFirebase()
        return GUI


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

