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

    def on_start(self):
        try:
            self.get_data()
            # populate add expense category srollview
            self.add_expense_icons()
            # initial screen load of expenses by month on startup
            self.expense_by_month()
            #logged in
            self.on_log_in("connected", NoTransition())

        except Exception:
            print("EXCEPTION")
            traceback.print_exc()
            print("EXCEPTION")
            pass

    def get_data(self):
        with open("refresh_token.txt", 'r') as f:
            refresh_token = f.read()
        id_token, local_id = self.my_firebase.exchange_refresh_token(refresh_token)
        self.local_id = local_id
        self.id_token = id_token
        # Get database data
        result = requests.get("https://expensetracker-d3a98.firebaseio.com/" + local_id + ".json?auth=" + id_token)
        self.data = json.loads(result.content.decode())
        # get expenses
        self.expenses = self.data['expenses']
        # get and update user name
        # add budget to settings screen
        user_name = self.root.ids['connected'].ids['main_header']
        user_name.text = self.data['displayname'] + '\'s Expenses'  # for adding user name to banner
        self.root.ids['connected'].ids['settings_screen'].ids['display_id'].hint_text = self.data['displayname']
        self.root.ids['connected'].ids['settings_screen'].ids['budget_id'].hint_text = '$' + str(self.data['budget'])
        # get color scheme
        self.back_col = self.data['colorscheme']['background_color']
        self.bann_col = self.data['colorscheme']['banner_color']
        self.dock_col = self.data['colorscheme']['dock_color']
        self.util_col = self.data['colorscheme']['utility_color']
        # set color scheme
        self.root.ids['connected'].ids['settings_screen'].ids['background_color_id'].col = self.back_col
        self.root.ids['connected'].ids['expense_screen'].ids['background_color_id'].col = self.back_col
        self.root.ids['connected'].ids['category_screen'].ids['background_color_id'].col = self.back_col
        self.root.ids['connected'].ids['add_expense_screen'].ids['background_color_id'].col = self.back_col
        self.root.ids['connected'].ids['banner_color_id'].col = self.bann_col
        self.root.ids['connected'].ids['dock_color_id'].col = self.dock_col
        # set color scheme in settings screen
        self.root.ids['connected'].ids['settings_screen'].ids['background_color_hint_id'].hint_text = self.back_col
        self.root.ids['connected'].ids['settings_screen'].ids['dock_color_hint_id'].hint_text = self.dock_col
        self.root.ids['connected'].ids['settings_screen'].ids['banner_color_hint_id'].hint_text = self.bann_col
        self.root.ids['connected'].ids['settings_screen'].ids['utility_color_hint_id'].hint_text = self.util_col

    def update_color_scheme(self):
        back_col = self.root.ids['connected'].ids['settings_screen'].ids['background_color_hint_id']
        dock_col = self.root.ids['connected'].ids['settings_screen'].ids['dock_color_hint_id']
        bann_col = self.root.ids['connected'].ids['settings_screen'].ids['banner_color_hint_id']
        util_col = self.root.ids['connected'].ids['settings_screen'].ids['utility_color_hint_id']

        background_color = back_col.hint_text
        dock_color = dock_col.hint_text
        banner_color = bann_col.hint_text
        utility_color = util_col.hint_text

        if len(back_col.text) == 6:
            background_color = back_col.text.upper()

        if len(dock_col.text) == 6:
            dock_color = dock_col.text.upper()

        if len(bann_col.text) == 6:
            banner_color = bann_col.text.upper()

        if len(util_col.text) == 6:
            utility_color = util_col.text.upper()

        patch_data = '{"colorscheme": {"background_color": "%s", "banner_color": "%s", "dock_color": "%s", "utility_color": "%s"}}' % (background_color, banner_color, dock_color, utility_color)
        patch_req = requests.patch(
            "https://expensetracker-d3a98.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token),
            data=patch_data)

        back_col.hint_text = background_color
        dock_col.hint_text = dock_color
        bann_col.hint_text = banner_color
        util_col.hint_text = utility_color

        back_col.text = ''
        dock_col.text = ''
        bann_col.text = ''
        util_col.text = ''

        self.on_start()

    def update_budget(self, *args):
        targetbudget = self.root.ids['connected'].ids['settings_screen'].ids['budget_id']
        if targetbudget.text != "":
            patch_data = '{"budget": %s}' % int(targetbudget.text)
            patch_req = requests.patch(
                "https://expensetracker-d3a98.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token),
                data=patch_data)
            targetbudget.hint_text = '$' + targetbudget.text
        else:
            targetbudget.text = '0'
            patch_data = '{"budget": %s}' % int(targetbudget.text)
            patch_req = requests.patch(
                "https://expensetracker-d3a98.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token),
                data=patch_data)
            targetbudget.hint_text = '$0'
        targetbudget.text = ''

    def update_display_name(self, *args):
        change_name = self.root.ids['connected'].ids['settings_screen'].ids['display_id']
        if change_name.text != "":
            patch_data = '{"displayname": "%s"}' % change_name.text
            patch_req = requests.patch(
                "https://expensetracker-d3a98.firebaseio.com/%s.json?auth=%s" % (self.local_id, self.id_token),
                data=patch_data)
            user_name = self.root.ids['connected'].ids['main_header']
            user_name.text = change_name.text + '\'s Expenses'
            change_name.hint_text = change_name.text
            change_name.text = ''

    def expense_by_month(self):
        result = requests.get("https://expensetracker-d3a98.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
        data = json.loads(result.content.decode())
        expense_months = self.root.ids['connected'].ids['expense_screen'].ids['expense_months']

        if len(expense_months.slides):
            expense_months.index = 0
            expense_months.clear_widgets()

        months = data['expenses']
        if months != "":
            for month in months:
                N = ExpenseByMonth(month, data)
                expense_months.add_widget(N)
            expense_months.load_slide(N)

    def expense_by_category(self):
        result = requests.get(
            "https://expensetracker-d3a98.firebaseio.com/" + self.local_id + ".json?auth=" + self.id_token)
        data = json.loads(result.content.decode())
        expense_category = self.root.ids['connected'].ids['category_screen'].ids['expense_categories']

        if len(expense_category.slides):
            expense_category.index = 0
            expense_category.clear_widgets()

        months = data['expenses']
        if months != "":
            for month in months:
                N = ExpenseByCategory(month, data)
                expense_category.add_widget(N)
            expense_category.load_slide(N)

    def add_expense_icons(self):
        category_image_grid = self.root.ids['connected'].ids['add_expense_screen'].ids['add_category_grid']
        for root_dir, folders, files in walk("icons/expenses"):
            for f in files:
                if 'dark' not in f:
                    img = ImageButton(source="icons/expenses/" + f, id=f[:-4] + '_id',
                                      on_release=partial(self.button_pressed, f))
                    category_image_grid.add_widget(img)

    def add_expense(self):
        today = datetime.today()
        months = [1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        days = [1, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
        years = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]
        # get date of expense occurance
        expense_ids = self.root.ids['connected'].ids['add_expense_screen'].ids
        price_input = expense_ids['add_price_id'].text
        month_input = expense_ids['month_input_id'].text
        day_input = expense_ids['day_input_id'].text
        year_input = expense_ids['year_input_id'].text

        if self.category_image == None:
            select_category_image_label = self.root.ids['connected'].ids.add_expense_screen.ids.select_category_image_label
            select_category_image_label.color = (1, 0, 0, 1)
            return
        # if price not integer return error
        if price_input == "":
            expense_ids['add_price_id'].background_color = (.8, 0, 0, 1)
            return
        try:
            float_price = float(price_input)
        except:
            expense_ids['add_price_id'].background_color = (.8, 0, 0, 1)
            return
        if month_input != '':
            try:
                int_month = int(month_input)
            except:
                expense_ids['month_input_id'].background_color = (.8, 0, 0, 1)
                return
        else:
            month_input = str(today.month).zfill(2)

        if day_input != '':
            try:
                int_day = int(day_input)
            except:
                expense_ids['day_input_id'].background_color = (.8, 0, 0, 1)
                return
        else:
            day_input = str(today.day).zfill(2)

        if year_input != '':
            try:
                int_year = int(year_input)
            except:
                expense_ids['year_input_id'].background_color = (.8, 0, 0, 1)
                return
        else:
            year_input = str(today.year)[2:]

        #check if valid month/date/year and zill(2)
        if int(month_input) not in months:
            expense_ids['month_input_id'].background_color = (.8, 0, 0, 1)
            return
        else:
            month_input = month_input.zfill(2)

        if int(day_input) not in days:
            expense_ids['day_input_id'].background_color = (.8, 0, 0, 1)
            return
        else:
            day_input = day_input.zfill(2)

        if int(year_input) not in years:
            expense_ids['year_input_id'].background_color = (.8, 0, 0, 1)
            return

        month = '20' + year_input + '-' + month_input

        # add expense to firebase
        price_post = float(price_input)
        date_post = int('20' + year_input + month_input + day_input)
        expense_payload = {"category": self.category_image, "price": price_post, "date": date_post}
        expense_request = requests.post("https://expensetracker-d3a98.firebaseio.com/%s/expenses/%s.json?auth=%s" % (self.local_id, month, self.id_token), data=json.dumps(expense_payload))

        #clear data
        self.root.ids['connected'].ids['add_expense_screen'].ids['add_price_id'].text = ''
        self.root.ids['connected'].ids['add_expense_screen'].ids['month_input_id'].text = ''
        self.root.ids['connected'].ids['add_expense_screen'].ids['day_input_id'].text = ''
        self.root.ids['connected'].ids['add_expense_screen'].ids['year_input_id'].text = ''
        self.root.ids['connected'].ids['add_expense_screen'].ids['add_expense_id'].text = 'Expense Added'
        self.category_image_widget.canvas.before.clear()
        self.category_image = None

    def change_screen(self, screen_name, screen_transition):
        # Get the screen manager from the kv file
        screen_manager = self.root.ids['connected'].ids['screen_manager']
        screen_manager.transition = screen_transition
        screen_manager.current = screen_name

    def on_log_in(self, screen_name, screen_transition):
        screen_manager = self.root.ids['screen_manager']
        screen_manager.transition = screen_transition
        screen_manager.current = screen_name

    def clear_expense(self):
        self.root.ids['connected'].ids['add_expense_screen'].ids['add_expense_id'].text = ''

    def button_pressed(self, button_name, widget_id):
        self.previous_category_image_widget = self.category_image_widget
        self.category_image = button_name[:-4].title()
        self.category_image_widget = widget_id

        if self.previous_category_image_widget:
            self.previous_category_image_widget.canvas.before.clear()

        select_category_image_label = self.root.ids.connected.ids.add_expense_screen.ids.select_category_image_label
        select_category_image_label.color = (1, 1, 1, 1)

        with self.category_image_widget.canvas.before:
            Color(rgb=(kivy.utils.get_color_from_hex("#6C5B7B")))
            RoundedRectangle(size=self.category_image_widget.size, pos=self.category_image_widget.pos, radius = [15,])

    def log_out(self):
        with open(self.refresh_token_file, 'w') as f:
            f.write("")
        self.on_log_in("login_screen", SlideTransition(direction='down', duration=.15))
        self.root.ids.login_screen.ids.login_email.text = ""
        self.root.ids.login_screen.ids.login_password.text = ""


MainApp().run()
