import time
import requests
from plyer import notification

BOT_TOKEN = "8500905322:AAEufrxEYMoHmhmJ0X0Bo1OeeCpOo2fAzCU"
CHAT_ID = "7589082187"

while True:
    try:
        # Notification every 60 sec
        notification.notify(
            title="Jarvis AI",
            message="Service running in background",
            timeout=5
        )

        # Telegram message
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": "Jarvis is alive!"}
        requests.post(url, data=data)

    except Exception as e:
        print("Error sending telegram:", e)

    time.sleep(60)  # repeat every 1 min
