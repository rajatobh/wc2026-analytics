import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FOOTBALL_API_KEY")
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

WC_2026_ID = 2000


def fetch_teams() ->list[dict]:
    """Fetch all the teams in WC 2026"""
    url = f"{BASE_URL}/competitions/{WC_2026_ID}/teams"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    teams = []
    for team in data.get("teams", []):
        teams.append({
            "id": team["id"],
            "name": team["name"],
            "short_name": team["shortName"],
            "country": team["area"]["name"],
            "crest": team.get("crest", "")
        })
    print(f"✅ Fetched {len(teams)} teams")
    return teams



def fetch_matches() -> list[dict]:
    """Fetch all WC 2026 matches"""
    url = f"{BASE_URL}/competitions/{WC_2026_ID}/matches"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    matches = []
    for m in data.get("matches", []):
        matches.append({
            "id": m["id"],
            "stage": m["stage"],
            "group": m.get("group"),
            "date": m["utcDate"],
            "home_team": m["homeTeam"]["name"],
            "away_team": m["awayTeam"]["name"],
            "home_score": m["score"]["fullTime"]["home"],
            "away_score": m["score"]["fullTime"]["away"],
            "status": m["status"]
        })
    print(f"✅ Fetched {len(matches)} matches")
    return matches



def fetch_scorers() -> list[dict]:
    """Fetch top scorers for WC 2026"""
    url = f"{BASE_URL}/competitions/{WC_2026_ID}/scorers?limit=20"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    scorers = []
    for s in data.get("scorers", []):
        scorers.append({
            "player": s["player"]["name"],
            "team": s["team"]["name"],
            "goals": s["goals"],
            "assists": s.get("assists", 0),
            "penalties": s.get("penalties", 0)
        })
    print(f"✅ Fetched {len(scorers)} top scorers")
    return scorers


def save_data(data: list[dict], filename: str):
    """Save fetched data as JSON."""
    path = os.path.join("data", filename)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"💾 Saved → {path}")


def run():
    print("🌍 Fetching WC 2026 data...\n")
    teams = fetch_teams()
    matches = fetch_matches()
    scorers = fetch_scorers()

    save_data(teams, "teams.json")
    save_data(matches, "matches.json")
    save_data(scorers, "scorers.json")

    print("\n✅ All data fetched and saved to data/")


if __name__ == "__main__":
    run()
