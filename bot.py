import requests
import time
import os

# ================== ENV VARIABLES ==================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
API_KEY = os.environ.get("API_KEY")

# ================== HEADERS ==================
headers = {
    "x-apisports-key": API_KEY
}

# ================== LEAGUES ==================
# كل الدوريات التي اخترتها
TOP_LEAGUES = [
    39,   # Premier League
    40,   # Championship
    41,   # National League
    42,   # National League South
    110,  # Welsh Premier League
    140,  # La Liga
    135,  # Serie A
    78,   # Bundesliga
    61,   # Ligue 1
    188,  # A-League
    307,  # Saudi Pro League
    308,  # Saudi First Division
    203,  # Turkish Super Lig
    204,  # TFF 1. Lig
    144,  # Belgian Pro League
    6     # Africa Cup of Nations
]

# الدوريات التي نطلب لها إحصائيات فقط
STATS_LEAGUES = [39, 40, 140, 135, 78, 61, 307, 203]

# ================== MEMORY ==================
last_state = {}

# ================== FUNCTIONS ==================
def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})


def get_live_matches():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    r = requests.get(url, headers=headers)
    return r.json().get("response", [])


def get_statistics(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    r = requests.get(url, headers=headers)
    return r.json().get("response", [])


def shots_on_target(stats):
    for s in stats:
        if s["type"] == "Shots on Goal":
            return s["value"] or 0
    return "?"

# ================== START ==================
send_message("🤖 البوت شغّال (وضع ذكي)")

while True:
    matches = get_live_matches()
    messages = []

    for match in matches:
        league_id = match["league"]["id"]
        if league_id not in TOP_LEAGUES:
            continue

        fixture_id = match["fixture"]["id"]
        league = match["league"]["name"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        minute = match["fixture"]["status"]["elapsed"]

        gh = match["goals"]["home"]
        ga = match["goals"]["away"]

        # ================== STATISTICS ==================
        hs = as_ = "?"

        if league_id in STATS_LEAGUES:
            stats = get_statistics(fixture_id)
            if stats:
                home_stats = stats[0]["statistics"]
                away_stats = stats[1]["statistics"]
                hs = shots_on_target(home_stats)
                as_ = shots_on_target(away_stats)

        state = f"{gh}-{ga}-{hs}-{as_}"
        if last_state.get(fixture_id) == state:
            continue

        last_state[fixture_id] = state

        block = (
            f"⚽ {league}\n"
            f"{home} vs {away}\n"
            f"⏱ {minute}'\n"
            f"🔢 {gh} - {ga}\n"
            f"🎯 تسديدات على المرمى:\n"
            f"🥅 {home}: {hs}\n"
            f"🥅 {away}: {as_}\n"
        )

        messages.append(block)

    if messages:
        final_message = "📊 تحديث المباريات المباشرة\n\n" + "\n".join(messages)
        send_message(final_message)

    time.sleep(60)
