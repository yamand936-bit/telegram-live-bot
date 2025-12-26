import os
import time
import requests

API_KEY = os.getenv("API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# الدوريات المسموحة
ALLOWED_LEAGUES = [
    302,  # Saudi Pro League
    203,  # Turkey Super Lig
    144,  # Belgium Pro League
    241,  # England Championship
    550,  # National League South
    201,  # Wales Premier League
    321   # Africa Cup of Nations
]

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

def get_live_matches():
    url = (
        "https://api.sportmonks.com/v3/football/livescores"
        f"?api_token={API_KEY}&include=participants;statistics"
    )
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.json()

def extract_shots_on_target(stats):
    home = away = 0
    for stat in stats:
        if stat.get("type", {}).get("name") == "Shots On Target":
            if stat.get("participant_id") == stat.get("fixture", {}).get("home_id"):
                home = stat.get("value", 0)
            else:
                away = stat.get("value", 0)
    return home, away

def main():
    send_message("🤖 البوت شغّال باستخدام SportMonks")

    while True:
        try:
            data = get_live_matches()
            matches = data.get("data", [])

            if not matches:
                time.sleep(60)
                continue

            for match in matches:
                league_id = match.get("league_id")
                if league_id not in ALLOWED_LEAGUES:
                    continue

                name = match.get("name", "مباراة")
                stats = match.get("statistics", [])
                home_shots, away_shots = extract_shots_on_target(stats)

                msg = (
                    f"⚽ {name}\n"
                    f"🎯 تسديدات على المرمى:\n"
                    f"🏠 صاحب الأرض: {home_shots}\n"
                    f"✈️ الضيف: {away_shots}"
                )
                send_message(msg)

            time.sleep(60)

        except Exception as e:
            send_message(f"❌ Error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
