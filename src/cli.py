import os
import json
import anthropic
from dotenv import load_dotenv
from retriever import query_vector_store

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def load_json(filename: str) -> list[dict]:
    path = os.path.join(BASE_DIR, "data", filename)
    with open(path, "r") as f:
        return json.load(f)


def build_scorer_context() -> str:
    """Always build scorer context directly from JSON, sorted by goals."""
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
    """Detect if the question is about goals or scorers."""
    keywords = ["scorer", "goal", "goals", "scored", "top scorer", "most goals"]
    return any(kw in question.lower() for kw in keywords)


def ask(question: str) -> str:
    """Retrieve relevant chunks and ask Claude to answer the question."""

    print("\n🔍 Searching knowledge base...")

    # Hybrid approach: use direct data for scorer questions
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

    while True:
        question = input("Ask a question: ").strip()
        if question.lower() == "exit":
            print("Goodbye! 👋")
            break
        if not question:
            continue

        answer = ask(question)
        print(f"\n💬 Answer:\n{answer}\n")
        print("-" * 50)


if __name__ == "__main__":
    main()