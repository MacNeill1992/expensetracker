import requests
import json
from kivy.app import App
from kivy.uix.screenmanager import SlideTransition

class MyFirebase():
    wak = "AIzaSyDjJGbx1HkOLSfDjuLz5DTg3vQj9nPp0MQ"

    def sign_up(self, email, password):
        app = App.get_running_app()
        print("SIGNIUP")
        signup_url = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/signupNewUser?key=" + self.wak
        signup_payload = {"email": email, "password": password, "returnSecureToken": True}
        sign_up_request = requests.post(signup_url, data=signup_payload)
        print(sign_up_request.ok)
        print(sign_up_request.content.decode())
        sign_up_data = json.loads(sign_up_request.content.decode())
        if sign_up_request.ok == True:
            refresh_token = sign_up_data['refreshToken']
            localId = sign_up_data['localId']
            idToken = sign_up_data['idToken']
            with open("refresh_token.txt", "w") as f:
                f.write(refresh_token)

            app.local_id = localId
            app.id_token = idToken
            #default data for new accounts.

            my_data = '{"displayname": "test user", "budget": 200, "expenses": ""}'
            post_request = requests.patch("https://expensetracker-d3a98.firebaseio.com/" + localId + ".json?auth=" + idToken,
                           data=my_data)
            print(post_request.ok)
            print(json.loads(post_request.content.decode()))

            app.change_screen("connected")

        if sign_up_request.ok == False:
            error_data = json.loads(sign_up_request.content.decode())
            error_message = error_data["error"]['message']
            app.root.ids['login_screen'].ids['login_message'].text = error_message


        pass

    def exchange_refresh_token(self, refresh_token):
        refresh_url = "https://securetoken.googleapis.com/v1/token?key=" + self.wak
        refresh_payload = '{"grant_type": "refresh_token", "refresh_token": "%s"}' % refresh_token
        refresh_req = requests.post(refresh_url, data=refresh_payload)
        id_token = refresh_req.json()['id_token']
        local_id = refresh_req.json()['user_id']
        return id_token, local_id

    def sign_in(self):
        pass
