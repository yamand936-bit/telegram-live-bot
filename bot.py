import requests
import time
import os

# ================== ENV ==================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
SPORTMONKS_TOKEN = os.environ.get("SPORTMONKS_TOKEN")

BASE_URL = "https://api.sportmonks.com/v3/football"

# ================== LEAGUES ==================
# كل الدوريات التي طلبتها
TOP_LEAGUES = [
    8,    # Premier League
    9,    # Championship
    10,   # League One
    11,   # League Two
    12,   # National League
    72,   # National League South
    110,  # Wales Premier League
    82,   # La Liga
    384,  # Serie A
    564,  # Bundesliga
    301,  # Ligue 1
    188,  # Australia A-League
    307,  # Saudi Pro League
    308,  # Saudi First Division
    203,  # Turkey Super Lig
    204,  # Turkey 1. Lig
    144,  # Belgium Pro League
    6     # Africa Cup of Nations
]

last_state = {}

# ================== FUNCTIONS ==================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_live_matches():
    url = f"{BASE_URL}/livescores"
    params = {
        "api_token": SPORTMONKS_TOKEN,
        "include": "statistics;participants;league"
    }
    r = requests.get(url, params=params)
    return r.json().get("data", [])


def get_shots_on_target(stats, team_id):
    for s in stats:
        if s["team_id"] == team_id and s["type"]["code"] == "shots_on_target":
            return s["value"]
    return "?"


# ================== START ==================
send_message("🤖 البوت شغّال باستخدام SportMonks")

while True:
    try:
        matches = get_live_matches()
        messages = []

        for match in matches:
            league_id = match["league_id"]
            if league_id not in TOP_LEAGUES:
                continue

            home = match["participants"][0]
            away = match["participants"][1]

            home_id = home["id"]
            away_id = away["id"]

            home_name = home["name"]
            away_name = away["name"]

            minute = match["time"]["minute"]
            score_home = match["scores"]["localteam_score"]
            score_away = match["scores"]["visitorteam_score"]

            stats = match.get("statistics", [])

            home_shots = get_shots_on_target(stats, home_id)
            away_shots = get_shots_on_target(stats, away_id)

            state = f"{score_home}-{score_away}-{home_shots}-{away_shots}"
            if last_state.get(match["id"]) == state:
                continue

            last_state[match["id"]] = state

            msg = (
                f"⚽ {match['league']['name']}\n"
                f"{home_name} vs {away_name}\n"
                f"⏱ {minute}'\n"
                f"🔢 {score_home} - {score_away}\n"
                f"🎯 تسديدات على المرمى:\n"
                f"🥅 {home_name}: {home_shots}\n"
                f"🥅 {away_name}: {away_shots}"
            )

            messages.append(msg)

        if messages:
            send_message("📊 تحديث المباريات المباشرة\n\n" + "\n\n".join(messages))

        time.sleep(60)

    except Exception as e:
        send_message(f"⚠️ خطأ مؤقت:\n{e}")
        time.sleep(60)
