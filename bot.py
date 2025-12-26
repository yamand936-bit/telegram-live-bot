import os
import time
import requests

# ====== ENV VARIABLES ======
SPORTMONKS_API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY is missing")

# ====== TELEGRAM ======
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)

# ====== SPORTMONKS ======
def get_live_matches():
    url = "https://api.sportmonks.com/v3/football/livescores"
    params = {
        "api_token": SPORTMONKS_API_KEY,
        "include": "participants"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("data", [])

# ====== MAIN LOOP ======
send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    try:
        matches = get_live_matches()

        if not matches:
            send_message("⚽ لا توجد مباريات مباشرة الآن")
        else:
            for match in matches:
                name = match.get("name", "مباراة")
                minute = match.get("time", {}).get("minute", "؟")
                result = match.get("result_info", "—")

                msg = f"""⚽ {name}
⏱ الدقيقة: {minute}
📊 النتيجة: {result}
"""
                send_message(msg)

        time.sleep(60)

    except Exception as e:
        send_message(f"❌ Error: {e}")
        time.sleep(60)
