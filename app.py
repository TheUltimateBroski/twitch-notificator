import os
import time
import threading
import requests
import random
from flask import Flask

app = Flask(__name__)

CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
USERNAME = "ryusenvt"
WEBHOOK_URL = os.environ["WEBHOOK_URL"]

# 🎬 GIFs que se mostrarán en el embed
GIFS = [
    "https://media.giphy.com/media/3o7aD2saalBwwftBIY/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/ICOgUNjpvO0PC/giphy.gif"
]

was_live = False


def get_access_token():
    response = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    )
    return response.json()["access_token"]


def check_stream_live(token):
    response = requests.get(
        "https://api.twitch.tv/helix/streams",
        headers={
            "Client-ID": CLIENT_ID,
            "Authorization": f"Bearer {token}"
        },
        params={"user_login": USERNAME}
    )
    return response.json().get("data", [])


def send_notification(stream):
    gif = random.choice(GIFS)

    payload = {
        "content": f"@everyone 🔴 ¡{USERNAME} está en vivo!",
        "embeds": [{
            "title": stream["title"],
            "url": f"https://twitch.tv/{USERNAME}",
            "description": f"🎮 Jugando: {stream['game_name']}",
            "color": 6570404,
            "image": {
                "url": gif
            }
        }]
    }

    requests.post(WEBHOOK_URL, json=payload)


def twitch_checker():
    global was_live
    print("Monitor Twitch iniciado...")

    while True:
        try:
            token = get_access_token()
            stream_data = check_stream_live(token)

            if stream_data and not was_live:
                send_notification(stream_data[0])
                was_live = True
                print("Notificación enviada")

            elif not stream_data:
                was_live = False
                print("Offline")

            time.sleep(300)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)


@app.route("/")
def home():
    return "Bot Twitch activo 🚀"


if __name__ == "__main__":
    thread = threading.Thread(target=twitch_checker)
    thread.daemon = True
    thread.start()

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
