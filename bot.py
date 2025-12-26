import requests
import time

TELEGRAM_TOKEN = "8504344551:AAEINvlgMKfITy7ZQCTWEUyNN0VVsysmiRE"
CHAT_ID = "1375730721"
API_KEY = "f2dbf064f057c5e705df59bc1ca5cd86"

headers = {
    "x-apisports-key": API_KEY
}

# الدوريات القوية فقط
TOP_LEAGUES = [39, 140, 135, 78, 61, 188]

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(url, data=data)

def get_live_matches():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    return requests.get(url, headers=headers).json()

def get_statistics(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    return requests.get(url, headers=headers).json()

def shots_on_target(stats):
    for s in stats:
        if s["type"] == "Shots on Goal":
            return s["value"] or 0
    return "?"

send_message("ok")
while True:
    live_data = get_live_matches()
    matches = live_data.get("response", [])

    if not matches:
        send_message("⚠️ لا توجد مباريات مباشرة حاليًا")
        time.sleep(60)
        continue

    for match in matches:
        league_id = match["league"]["id"]
        league_name = match["league"]["name"]

        if league_id not in TOP_LEAGUES:
            continue

        fixture_id = match["fixture"]["id"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        minute = match["fixture"]["status"]["elapsed"]

        goals_home = match["goals"]["home"]
        goals_away = match["goals"]["away"]

        stats_data = get_statistics(fixture_id)

        if not stats_data.get("response"):
            send_message(f"""⚠️ LIVE لكن بدون إحصائيات
{league_name}
{home} vs {away}
⏱ {minute}'
النتيجة: {goals_home}-{goals_away}
""")
            continue

        home_stats = stats_data["response"][0]["statistics"]
        away_stats = stats_data["response"][1]["statistics"]

        home_shots = shots_on_target(home_stats)
        away_shots = shots_on_target(away_stats)

        send_message(f"""⚽ LIVE | {league_name}
{home} vs {away}
⏱ {minute}'
النتيجة: {goals_home}-{goals_away}

🎯 تسديدات على المرمى:
{home}: {home_shots}
{away}: {away_shots}
""")

    time.sleep(60)
