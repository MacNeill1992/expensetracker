import requests
import json
from kivy.app import App
from kivy.uix.screenmanager import SlideTransition

class MyFirebase():
    wak = "AIzaSyDjJGbx1HkOLSfDjuLz5DTg3vQj9nPp0MQ"

    def sign_up(self, email, password):
        app = App.get_running_app()
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        sign_up_data = json.loads(sign_up_request.content.decode())
        if sign_up_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            with open(app.refresh_token_file, "w") as f:
                f.write(refresh_token)

            app.local_id = localId
            app.id_token = idToken
            #default data for new accounts.
            disp_name = email.split('@')[0]
            my_data = '{"displayname": "%s", "budget": 200, "expenses": "", "colorscheme": {"background_color": "2F575D", "banner_color": "2F575D", "dock_color": "2F575D", "utility_color": "191919"}}' % disp_name
            post_request = requests.patch("https://expensetracker-d3a98.firebaseio.com/" + localId + ".json?auth=" +
                                          idToken, data=my_data)
            app.get_data()
            app.add_expense_icons()
            app.on_log_in("connected", SlideTransition(direction='up', duration=.15))

        elif sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]['message']
            if error_message == "EMAIL_EXISTS":
                self.sign_in_existing_user(email, password)
            else:
                app.root.ids['login_screen'].ids['login_message'].text = error_message

    def sign_in_existing_user(self, email, password):
        signin_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key=" + self.wak
        signin_payload = {"email": email, "password": password, "returnSecureToken": True}
        signin_request = requests.post(signin_url, data=signin_payload)
        sign_up_data = json.loads(signin_request.content.decode())
        app = App.get_running_app()

        if signin_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            # Save refreshToken to a file
            with open(app.refresh_token_file, "w") as f:
                f.write(refresh_token)

            # Save localId to a variable in main app class
            # Save idToken to a variable in main app class
            app.local_id = localId
            app.id_token = idToken
            app.on_start()
        elif signin_request.ok == False:
            error_data = json.loads(signin_request.content.decode())
            error_message = error_data["error"]['message']
            app.root.ids['login_screen'].ids['login_message'].text = "EMAIL EXISTS - " + error_message.replace("_", " ")


    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id

