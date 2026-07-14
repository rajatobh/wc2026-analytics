import os
import json
import anthropic
from dotenv import load_dotenv
from retriever import query_vector_store
from visualizer import (
    chart_top_scorers,
    chart_goals_by_team,
    chart_match_results,
    chart_team_comparison
)

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def load_json(filename: str) -> list[dict]:
    path = os.path.join(BASE_DIR, "data", filename)
    with open(path, "r") as f:
        return json.load(f)


def build_scorer_context() -> str:
    scorers = load_json("scorers.json")
    scorers_sorted = sorted(scorers, key=lambda x: x["goals"], reverse=True)
    lines = []
    for i, s in enumerate(scorers_sorted, 1):
        lines.append(
            f"{i}. {s['player']} ({s['team']}): "
            f"{s['goals']} goals, {s['assists']} assists"
        )
    return "Top scorers in WC 2026:\n" + "\n".join(lines)


def is_scorer_question(question: str) -> bool:
    keywords = ["scorer", "goal", "goals", "scored", "top scorer", "most goals"]
    return any(kw in question.lower() for kw in keywords)


def detect_chart_request(question: str) -> str | None:
    """Detect if the user wants a chart and which type."""
    q = question.lower()
    if any(k in q for k in ["chart", "graph", "plot", "visuali", "show me"]):
        if any(k in q for k in ["scorer", "goal scorer", "top scorer"]):
            return "top_scorers"
        if any(k in q for k in ["goals by team", "team goals", "which team scored"]):
            return "goals_by_team"
        if any(k in q for k in ["match result", "results", "scores", "all matches"]):
            return "match_results"
        if "vs" in q or "compare" in q:
            return "team_comparison"
    return None


def extract_teams(question: str) -> tuple[str, str] | None:
    """Extract two team names from a comparison question."""
    teams = load_json("teams.json")
    team_names = [t["name"] for t in teams]
    found = [t for t in team_names if t.lower() in question.lower()]
    if len(found) >= 2:
        return found[0], found[1]
    return None


def ask(question: str) -> str:
    """Retrieve relevant chunks and ask Claude to answer."""

    # Check for chart requests first
    chart_type = detect_chart_request(question)
    if chart_type:
        print(f"\n📊 Chart request detected: {chart_type}")
        if chart_type == "top_scorers":
            chart_top_scorers()
        elif chart_type == "goals_by_team":
            chart_goals_by_team()
        elif chart_type == "match_results":
            chart_match_results()
        elif chart_type == "team_comparison":
            teams = extract_teams(question)
            if teams:
                chart_team_comparison(teams[0], teams[1])
            else:
                return "Please name two teams to compare, e.g. 'Compare France vs Brazil'"
        return "✅ Chart opened in your browser and saved to charts/"

    print("\n🔍 Searching knowledge base...")
    if is_scorer_question(question):
        print("📊 Scorer question detected — using direct data lookup...")
        context = build_scorer_context()
    else:
        chunks = query_vector_store(question)
        context = "\n".join(f"- {chunk}" for chunk in chunks)

    prompt = f"""You are a FIFA World Cup 2026 statistics assistant.
Use ONLY the context below to answer the user's question.
If the answer isn't in the context, say "I don't have that data yet."

Context:
{context}

Question: {question}

Answer in a clear, concise way. If stats are involved, mention the numbers explicitly.
"""

    print("🤖 Asking Claude...\n")
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def main():
    print("⚽ WC 2026 Analytics — RAG Assistant")
    print("Type 'exit' to quit\n")
    print("💡 Try: 'Show me a chart of top scorers'")
    print("💡 Try: 'Plot goals by team'")
    print("💡 Try: 'Compare France vs Brazil'\n")

    while True:
        question = input("Ask a question: ").strip()
        if question.lower() == "exit":
            print("Goodbye! 👋")
            break
        if not question:
            continue

        answer = ask(question)
        print(f"\n💬 {answer}\n")
        print("-" * 50)


if __name__ == "__main__":
    main()