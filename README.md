# 🍬 Nassau Candy: Product Line Profitability & Margin Performance

Streamlit dashboard + analysis for the Unified Mentor project *Product Line Profitability & Margin Performance Analysis for Nassau Candy Distributor*.

## Features
- Product leaderboard, profit contribution, segmentation (Star / Volume trap / Niche earner / Underperformer)
- Division revenue-vs-profit comparison and margin distribution
- Cost-vs-sales scatter, margin-risk flags (repricing, cost renegotiation, discontinuation review)
- Pareto (80/20) concentration, HHI, geographic and factory dependency
- Filters: date range, division, margin-threshold slider, product search

## Project structure
```
app.py               Streamlit dashboard
analysis.py          Cleaning + metric functions
make_figures.py      Static figures for the paper
data/                Nassau_Candy_Distributor.csv
docs/                research_paper.md, executive_summary.md, video_script.md
figures/             PNG charts
requirements.txt
```

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy free on Streamlit Community Cloud
1. Push this folder to a GitHub repo (see below).
2. Go to https://share.streamlit.io → **New app**.
3. Pick your repo, branch `main`, main file `app.py` → **Deploy**.

## Push to GitHub
```bash
git init
git add .
git commit -m "Nassau Candy profitability analysis"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```

## Key results
Sales $138,284 · Gross profit $91,076 · Margin 65.9%. Five chocolate products = 92.7% of revenue and 94.9% of profit. Biggest margin risk: Kazookles (7.7%). See `docs/`.
