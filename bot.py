import os
import requests

SPORTMONKS_API_KEY = os.getenv("SPORTMONKS_API_KEY")

if not SPORTMONKS_API_KEY:
    raise ValueError("❌ SPORTMONKS_API_KEY غير موجود")

URL = "https://api.sportmonks.com/v3/football/livescores"

params = {
    "api_token": SPORTMONKS_API_KEY,
    "filters": "league_id:550",
    "include": "participants"
}

response = requests.get(URL, params=params)
response.raise_for_status()

data = response.json().get("data", [])

if not data:
    print("🇹🇷 لا توجد مباريات مباشرة حاليًا في الدوري التركي الدرجة الأولى")
    exit()

print("🇹🇷 مباريات الدوري التركي الدرجة الأولى (مباشر):\n")

for match in data:
    teams = {p["meta"]["location"]: p["name"] for p in match["participants"]}
    home = teams.get("home", "؟")
    away = teams.get("away", "؟")

    score = match.get("scores", {})
    home_goals = score.get("home", 0)
    away_goals = score.get("away", 0)

    state = match.get("state", {}).get("name", "غير معروف")

    print(f"{home} {home_goals} - {away_goals} {away}")
    print(f"الحالة: {state}")
    print("-" * 30)
