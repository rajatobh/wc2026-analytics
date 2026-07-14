import os
import json
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHARTS_DIR = os.path.join(BASE_DIR, "charts")


def load_json(filename: str) -> list[dict]:
    path = os.path.join(BASE_DIR, "data", filename)
    with open(path, "r") as f:
        return json.load(f)


def save_and_show(fig, filename: str):
    """Save chart to charts/ folder and open in browser."""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    path = os.path.join(CHARTS_DIR, filename)
    fig.write_html(path)
    print(f"📊 Chart saved → {path}")
    fig.show()


def chart_top_scorers(top_n: int = 10):
    """Horizontal bar chart of top N scorers."""
    scorers = load_json("scorers.json")
    scorers_sorted = sorted(scorers, key=lambda x: x["goals"], reverse=True)[:top_n]
    df = pd.DataFrame(scorers_sorted)

    fig = px.bar(
        df,
        x="goals",
        y="player",
        orientation="h",
        color="goals",
        color_continuous_scale="Viridis",
        title=f"⚽ WC 2026 — Top {top_n} Scorers",
        labels={"goals": "Goals", "player": "Player"},
        text="goals",
        hover_data=["team", "assists", "penalties"]
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        plot_bgcolor="#0d1b2a",
        paper_bgcolor="#0d1b2a",
        font_color="white",
        title_font_size=22,
        yaxis={"categoryorder": "total ascending"},
        coloraxis_showscale=False,
        height=500
    )
    save_and_show(fig, "top_scorers.html")


def chart_goals_by_team():
    """Bar chart of total goals scored by each team."""
    matches = load_json("matches.json")
    finished = [m for m in matches if m["status"] == "FINISHED"]

    goals: dict = {}
    for m in finished:
        home, away = m["home_team"], m["away_team"]
        goals[home] = goals.get(home, 0) + (m["home_score"] or 0)
        goals[away] = goals.get(away, 0) + (m["away_score"] or 0)

    df = pd.DataFrame(
        sorted(goals.items(), key=lambda x: x[1], reverse=True),
        columns=["team", "goals"]
    )

    fig = px.bar(
        df,
        x="team",
        y="goals",
        color="goals",
        color_continuous_scale="Blues",
        title="🌍 WC 2026 — Goals Scored by Team",
        labels={"goals": "Goals", "team": "Team"},
        text="goals"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        plot_bgcolor="#0d1b2a",
        paper_bgcolor="#0d1b2a",
        font_color="white",
        title_font_size=22,
        xaxis_tickangle=-45,
        coloraxis_showscale=False,
        height=550
    )
    save_and_show(fig, "goals_by_team.html")


def chart_match_results():
    """Table of all finished match results."""
    matches = load_json("matches.json")
    finished = [m for m in matches if m["status"] == "FINISHED"]

    rows = []
    for m in finished:
        score = f"{m['home_score']} - {m['away_score']}"
        winner = (
            m["home_team"] if m["home_score"] > m["away_score"]
            else m["away_team"] if m["away_score"] > m["home_score"]
            else "Draw"
        )
        rows.append({
            "Date": m["date"][:10],
            "Home": m["home_team"],
            "Score": score,
            "Away": m["away_team"],
            "Stage": m["stage"],
            "Winner": winner
        })

    df = pd.DataFrame(rows)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=list(df.columns),
            fill_color="#1f3a5f",
            font=dict(color="white", size=13),
            align="center"
        ),
        cells=dict(
            values=[df[col] for col in df.columns],
            fill_color="#0d1b2a",
            font=dict(color="white", size=12),
            align="center",
            height=30
        )
    )])
    fig.update_layout(
        title="📅 WC 2026 — Match Results",
        title_font_size=22,
        paper_bgcolor="#0d1b2a",
        font_color="white",
        height=600
    )
    save_and_show(fig, "match_results.html")


def chart_team_comparison(team1: str, team2: str):
    """Radar chart comparing two teams across key stats."""
    matches = load_json("matches.json")
    finished = [m for m in matches if m["status"] == "FINISHED"]

    def get_stats(team: str) -> dict:
        played, wins, draws, losses, gf, ga = 0, 0, 0, 0, 0, 0
        for m in finished:
            if m["home_team"] == team:
                played += 1
                gf += m["home_score"] or 0
                ga += m["away_score"] or 0
                if m["home_score"] > m["away_score"]: wins += 1
                elif m["home_score"] == m["away_score"]: draws += 1
                else: losses += 1
            elif m["away_team"] == team:
                played += 1
                gf += m["away_score"] or 0
                ga += m["home_score"] or 0
                if m["away_score"] > m["home_score"]: wins += 1
                elif m["away_score"] == m["home_score"]: draws += 1
                else: losses += 1
        return {
            "Played": played, "Wins": wins, "Draws": draws,
            "Losses": losses, "Goals For": gf, "Goals Against": ga
        }

    stats1 = get_stats(team1)
    stats2 = get_stats(team2)
    categories = list(stats1.keys())

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=list(stats1.values()), theta=categories,
        fill="toself", name=team1, line_color="#00d4ff"
    ))
    fig.add_trace(go.Scatterpolar(
        r=list(stats2.values()), theta=categories,
        fill="toself", name=team2, line_color="#ff6b6b"
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1f3a5f",
            radialaxis=dict(visible=True, color="white"),
            angularaxis=dict(color="white")
        ),
        paper_bgcolor="#0d1b2a",
        font_color="white",
        title=f"🕸️ {team1} vs {team2} — Team Comparison",
        title_font_size=22,
        legend=dict(font=dict(color="white")),
        height=550
    )
    save_and_show(fig, "team_comparison.html")