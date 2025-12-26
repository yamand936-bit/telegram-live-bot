import requests
import time
import os

# ============ ENV ============
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SPORTMONKS_TOKEN = os.environ.get("SPORTMONKS_TOKEN")

BASE_URL = "https://api.sportmonks.com/v3/football"

# ============ LEAGUES ============
LEAGUE_IDS = [
    8,    # Premier League
    9,    # Championship
    30,   # National League
    31,   # National League South
    110,  # Cymru Premier
    564,  # La Liga
    384,  # Serie A
    82,   # Bundesliga
    301,  # Ligue 1
    125,  # A-League
    292,  # Saudi Pro League
    293,  # Saudi First Division
    271,  # Turkish Super Lig
    272,  # TFF 1. Lig
    144,  # Belgian Pro League
    1     # Africa Cup of Nations
]

last_state = {}

# ============ FUNCTIONS ============
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def get_live_fixtures():
    url = f"{BASE_URL}/fixtures/live"
    params = {
        "api_token": SPORTMONKS_TOKEN,
        "include": "league,participants,statistics"
    }
    r = requests.get(url, params=params)
    return r.json().get("data", [])

def get_stat(stats, stat_type):
    for s in stats:
        if s["type"]["name"] == stat_type:
            return s["value"]
    return "?"

# ============ START ============
send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    fixtures = get_live_fixtures()
    messages = []

    for f in fixtures:
        league_id = f["league"]["id"]
        if league_id not in LEAGUE_IDS:
            continue

        home = f["participants"][0]["name"]
        away = f["participants"][1]["name"]
        minute = f["time"]["minute"]

        stats_home = f["statistics"][0]["data"] if f["statistics"] else []
        stats_away = f["statistics"][1]["data"] if f["statistics"] else []

        shots_home = get_stat(stats_home, "Shots On Target")
        shots_away = get_stat(stats_away, "Shots On Target")

        state = f"{shots_home}-{shots_away}"
        if last_state.get(f["id"]) == state:
            continue

        last_state[f["id"]] = state

        msg = (
            f"⚽ {f['league']['name']}\n"
            f"{home} vs {away}\n"
            f"⏱ {minute}'\n"
            f"🎯 تسديدات على المرمى:\n"
            f"🥅 {home}: {shots_home}\n"
            f"🥅 {away}: {shots_away}\n"
        )
        messages.append(msg)

    if messages:
        send_message("📊 تحديث مباشر\n\n" + "\n".join(messages))

    time.sleep(60)
