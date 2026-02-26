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

LAST_COMMIT_FILE = "last_commit.txt"

GIFS = [
    "https://media.tenor.com/JCL2ng6ARjIAAAAM/chen-endfield.gif",
    "https://i.pinimg.com/originals/74/82/a8/7482a87e51359e6bb08084511c89a098.gif",
    "https://media.tenor.com/FQTla-UcgOQAAAAM/amiya-arknights.gif"
]

was_live = False


def send_startup_message_if_new_deploy():
    current_commit = os.environ.get("RENDER_GIT_COMMIT")
    if not current_commit:
        return

    if os.path.exists(LAST_COMMIT_FILE):
        with open(LAST_COMMIT_FILE, "r") as f:
            previous_commit = f.read().strip()
    else:
        previous_commit = None

    if previous_commit == current_commit:
        return

    with open(LAST_COMMIT_FILE, "w") as f:
        f.write(current_commit)

    payload = {
        "content": "🚀 Nuevo deploy detectado!",
        "embeds": [{
            "title": "Bot actualizado correctamente",
            "description": f"Commit: `{current_commit[:7]}`\nUsuario: {USERNAME}",
            "color": 3066993,
            "image": {"url": random.choice(GIFS)}
        }]
    }

    requests.post(WEBHOOK_URL, json=payload)


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
        "content": f"@everyone <:TwitchSymbol:1474627947599237245> ¡{USERNAME} ya abrió el stream, vayan a tirarle cosas!",
        "embeds": [{
            "title": stream["title"],
            "url": f"https://twitch.tv/{USERNAME}",
            "description": f"🎮 Jugando: {stream['game_name']}",
            "color": 6570404,
            "image": {"url": gif}
        }]
    }

    requests.post(WEBHOOK_URL, json=payload)


def twitch_checker():
    global was_live

    while True:
        try:
            token = get_access_token()
            stream_data = check_stream_live(token)

            if stream_data and not was_live:
                send_notification(stream_data[0])
                was_live = True

            elif not stream_data:
                was_live = False

            time.sleep(300)

        except Exception as e:
            print("Error:", e)
            time.sleep(60)


@app.route("/")
def home():
    return "Bot Twitch activo 🚀"


# 🔥 ESTA PARTE SE EJECUTA TAMBIÉN CON GUNICORN
def start_background_tasks():
    thread = threading.Thread(target=twitch_checker)
    thread.daemon = True
    thread.start()


start_background_tasks()
