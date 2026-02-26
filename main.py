import requests
import time
import os

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = "ryusenvt"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

was_live = False

def get_access_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    response = requests.post(url, params=params)
    return response.json()["access_token"]

def check_stream_live(token):
    url = f"https://api.twitch.tv/helix/streams?user_login={USERNAME}"
    headers = {
        "Client-ID": CLIENT_ID,
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    return response.json()["data"]

def send_notification(stream):
    thumbnail = stream["thumbnail_url"].replace("{width}", "1280").replace("{height}", "720")

    payload = {
        "content": "@everyone"
        "embeds": [{
            "title": stream["title"],
            "url": f"https://twitch.tv/{USERNAME}",
            "color": 2832289,
            "icon_url": "https://static-cdn.jtvnw.net/jtv_user_pictures/b9270b10-6bc4-468f-838e-7d0130f51176-profile_image-70x70.png"
    },
    "description": "*Vayan a tirarle cosas a Ryu que no me paga lo suficiente*",
    "fields": [
      {"name": "<:TwitchSymbol:1474627947599237245> Twitch", "value": "[Twitch](https://www.twitch.tv/ryusenvt)", "inline": true},
      {"name": "<:Youtube_logo:1474628135093010442> YouTube", "value": "[YouTube](https://www.youtube.com/@RyuSenVOD)", "inline": true}
            "image": {"url": thumbnail}
        }]
    }

    requests.post(WEBHOOK_URL, json=payload)

print("Bot iniciado...")

while True:
    try:
        token = get_access_token()
        stream_data = check_stream_live(token)

        if len(stream_data) > 0 and not was_live:
            send_notification(stream_data[0])
            was_live = True
            print("Notificación enviada")
        elif len(stream_data) == 0:
            was_live = False
            print("Offline")

        time.sleep(300)

    except Exception as e:
        print("Error:", e)
        time.sleep(60)
