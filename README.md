# ⚽ WC 2026 Analytics

A mini RAG (Retrieval-Augmented Generation) system for FIFA World Cup 2026 stats,
built with Python, ChromaDB, Claude AI, and Plotly.

## Features
- 🤖 Ask natural language questions about WC 2026
- 📊 Generate beautiful interactive charts
- 🔍 Hybrid RAG retrieval (ChromaDB + direct JSON lookup)

## Charts
- Top scorers leaderboard
- Goals scored by team
- All match results table
- Team comparison radar chart

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/wc2026-analytics.git
cd wc2026-analytics
```

**2. Create and activate virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate   # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Add your API keys to `.env`**
```
FOOTBALL_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

**5. Fetch data and build vector store**
```bash
python src/ingest.py
python src/retriever.py
```

**6. Run the app**
```bash
python src/cli.py
```

## Example Questions
```
Who is the top scorer so far?
Show me a chart of top scorers
Plot goals by team
Show me all match results
Compare France vs Argentina
```