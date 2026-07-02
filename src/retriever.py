import os
import json
import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = "data"
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBEDDINGS_DIR = os.path.join(BASE_DIR, "embeddings")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Use ChromaDB's built-in sentence transformer
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def load_json(filename: str) -> list[dict]:
    path = os.path.join(DATA_DIR, filename)
    with open(path, "r") as f:
        return json.load(f)


def chunk_teams(teams: list[dict]) -> list[tuple[str, str]]:
    """Convert team data into text chunks"""
    chunks = []
    for t in teams:
        text = (
            f"Team: {t['name']} ({t['short_name']}) "
            f"represents {t['country']} in the FIFA World Cup 2026."
        )
        chunks.append((f"team_{t['id']}", text))
    return chunks


def chunk_matches(matches: list[dict]) -> list[tuple[str, str]]:
    """Convert finished match data into text chunks"""
    chunks = []
    for m in matches:
        if m["status"] != "FINISHED":
            continue  # skip unplayed matches
        result = (
            f"{m['home_team']} {m['home_score']} - "
            f"{m['away_score']} {m['away_team']}"
        )
        text = (
            f"Match result on {m['date'][:10]}: {result}. "
            f"Stage: {m['stage']}. "
            f"Group: {m['group'] or 'Knockout'}."
        )
        chunks.append((f"match_{m['id']}", text))
    return chunks


def chunk_scorers(scorers: list[dict]) -> list[tuple[str, str]]:
    """Convert scorer data into text chunks"""
    chunks = []
    for i, s in enumerate(scorers):
        text = (
            f"Player {s['player']} playing for {s['team']} "
            f"has scored {s['goals']} goals, "
            f"{s['assists']} assists, and "
            f"{s['penalties']} penalties in WC 2026."
        )
        chunks.append((f"scorer_{i}", text))
    return chunks


def build_vector_store():
    """Chunk all data and load into ChromaDB"""
    print("📦 Building vector store...\n")

    client = chromadb.PersistentClient(path=EMBEDDINGS_DIR)

    # Delete existing collection if rebuilding
    try:
        client.delete_collection("wc2026")
    except Exception:
        pass

    collection = client.create_collection(
        name="wc2026",
        embedding_function=embedding_fn
    )

    # Load and chunk all data
    all_chunks = []
    all_chunks += chunk_teams(load_json("teams.json"))
    all_chunks += chunk_matches(load_json("matches.json"))
    all_chunks += chunk_scorers(load_json("scorers.json"))

    # Unzip into ids and documents
    ids, documents = zip(*all_chunks)

    # Add to ChromaDB in batches
    batch_size = 50
    for i in range(0, len(ids), batch_size):
        collection.add(
            ids=list(ids[i:i+batch_size]),
            documents=list(documents[i:i+batch_size])
        )
        print(f"  ✅ Embedded batch {i // batch_size + 1}")

    print(f"\n✅ Vector store built with {len(ids)} chunks → {EMBEDDINGS_DIR}/")


def query_vector_store(question: str, n_results: int = 5) -> list[str]:
    """Query ChromaDB and return the most relevant chunks"""
    client = chromadb.PersistentClient(path=EMBEDDINGS_DIR)
    collection = client.get_collection(
        name="wc2026",
        embedding_function=embedding_fn
    )
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    return results["documents"][0]  # list of matching text chunks


if __name__ == "__main__":
    build_vector_store()