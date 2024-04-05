import base64
import json
import os
import secrets
from flask import Flask, request
import threading
import webbrowser
import urllib.parse
import requests
from dotenv import load_dotenv

app = Flask(__name__)

load_dotenv()


# Function to shut down the server
def shutdown_server():
    # TODO: figure out a way to stop the server
    global server_thread
    server_thread._stop()


# Route to handle the callback from Spotify
@app.route("/callback")
def callback():
    auth_code = request.args.get("code")
    error = request.args.get("error")

    if error:
        print(f"Error during authorization: {error}")
    else:
        print(f"Authorization code: {auth_code}")

        # Get access token
        url = "https://accounts.spotify.com/api/token"

        client_creds = (
            f"{os.getenv('SPOTIFY_CLIENT_ID')}:{os.getenv('SPOTIFY_CLIENT_SECRET')}"
        )
        client_creds_b64 = base64.b64encode(client_creds.encode()).decode()

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {client_creds_b64}",
        }

        data = {
            "grant_type": "authorization_code",
            "code": auth_code,
            "redirect_uri": "http://localhost:5027/callback",
        }

        response = requests.post(
            url, headers=headers, data=urllib.parse.urlencode(data)
        )

        print(response.json())
        # put the response in a json file
        with open("auth_response.json", "w") as f:
            json.dump(response.json(), f)

    shutdown_server()
    return "Authorization received, you can close this window."


# Function to run the server
def run_server():
    app.run(port=5027)


# Function to start the server in a thread
def start_server():
    global server_thread
    server_thread = threading.Thread(target=run_server)
    server_thread.start()

    # Generate random csrf string
    state = secrets.token_urlsafe(16)
    redirect_uri = "http://localhost:5027/callback"
    scope = "user-read-private user-read-email playlist-modify-private playlist-modify-public"
    client_id = os.getenv("SPOTIFY_CLIENT_ID")

    print(client_id)

    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scope,
        "redirect_uri": redirect_uri,
        "state": state,
    }
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(
        params
    )

    webbrowser.open_new(auth_url)


start_server()
