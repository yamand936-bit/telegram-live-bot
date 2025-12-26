import requests
import time
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
API_KEY = os.environ.get("API_KEY")

headers = {"x-apisports-key": API_KEY}

TOP_LEAGUES = [39, 140, 135, 78, 61, 188, 307, 203, 308, 204, 144, 6, 40, 154, 153, 41, 42, 43, 110]

last_state = {}

def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def get_live_matches():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    return requests.get(url, headers=headers).json().get("response", [])

def get_statistics(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    return requests.get(url, headers=headers).json().get("response", [])

def shots_on_target(stats):
    for s in stats:
        if s["type"] == "Shots on Goal":
            return s["value"] or 0
    return "?"

send_message("🤖 البوت شغّال (وضع ذكي)")

while True:
    matches = get_live_matches()
    message_lines = []

    for match in matches:
        if match["league"]["id"] not in TOP_LEAGUES:
            continue

        fixture_id = match["fixture"]["id"]
        league = match["league"]["name"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]
        minute = match["fixture"]["status"]["elapsed"]

        gh = match["goals"]["home"]
        ga = match["goals"]["away"]

stats = []
if match["league"]["id"] in STATS_LEAGUES:
    stats = get_statistics(fixture_id)
    
        if stats:
            hs = shots_on_target(stats[0]["statistics"])
            as_ = shots_on_target(stats[1]["statistics"])
        else:
            hs = as_ = "?"

        current_state = f"{gh}-{ga}-{hs}-{as_}"

        if last_state.get(fixture_id) == current_state:
            continue

        last_state[fixture_id] = current_state

        block = f"""⚽ {league}
{home} vs {away}
⏱ {minute}'
🔢 {gh} - {ga}
🎯 تسديدات:
🥅 {home}: {hs}
🥅 {away}: {as_}
"""
        message_lines.append(block)

    if message_lines:
        final_message = "📊 تحديث المباريات المباشرة\n\n" + "\n".join(message_lines)
        send_message(final_message)

    time.sleep(60)
