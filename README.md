# Telecom Analytics Platform

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://sosisis-telcom-scriptsdashboard-ra9hlu.streamlit.app/)

An end-to-end analytics workspace that unifies exploratory notebooks, data processing utilities, and a Streamlit dashboard for telecom subscriber insights. The project aggregates network usage and experience metrics into engagement, experience, and satisfaction scores to help data teams monitor customer health in real time.

## Highlights

- **Streamlit dashboard** combining the four analytics tasks (overview, engagement, experience, satisfaction) with interactive Plotly visuals.
- **Reusable data layer** via `scripts/load_data.py` for PostgreSQL connectivity using either psycopg2 or SQLAlchemy.
- **Preprocessing helpers** in `scripts/data_cleaning.py` and example SQL workloads in `scripts/sql_queries.py` to reproduce intermediate datasets.
- **Research notebooks** under `notebooks/` that document feature engineering, clustering, and scoring logic.

## Repository layout

```
├── notebooks/
│   ├── user_overview_analysis.ipynb      # Task 1 insights and baseline metrics
│   ├── user_engagement_analysis.ipynb    # Task 2 engagement scoring and clusters
│   ├── user_experience_analytics.ipynb   # Task 3 network quality deep-dive
│   ├── user_satisfaction_analysis.ipynb  # Task 4 satisfaction modelling
│   └── artifacts/scores_full.parquet     # Precomputed combined dataset for the app
├── scripts/
│   ├── dashboard.py                      # Streamlit entry-point
│   ├── load_data.py                      # Database access helpers
│   ├── data_cleaning.py                  # Sample preprocessing utilities
│   └── sql_queries.py                    # Reference telecom SQL workloads
├── requirements.txt
└── README.md
```

## Data prerequisites

The dashboard expects the unified `scores_full` dataset containing per-subscriber metrics and cluster labels. You can supply it in either of two ways:

1. **Local artifact** – place `scores_full.parquet` under `notebooks/artifacts/` (already ignored from version control).
2. **Database view/table** – provision a PostgreSQL table or view named `scores_full` (or `scores_full_view`) with the columns referenced in `scripts/dashboard.py`.

If any required columns are missing, the dashboard surfaces a warning in the sidebar so you can revisit the preprocessing pipeline.

## Quick start

### Prerequisites

- Python 3.11+ (the repo was last developed against Python 3.12)
- Access to the telecom dataset or the precomputed parquet artifact
- Optional: PostgreSQL instance when sourcing data on demand

### Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Environment variables

Configure the following in a `.env` file at the project root (loaded by `python-dotenv`) or export them directly in your shell:

| Variable      | Description                                 |
|---------------|---------------------------------------------|
| `DB_HOST`     | PostgreSQL host                             |
| `DB_PORT`     | PostgreSQL port (e.g., `5432`)              |
| `DB_NAME`     | Database name containing telecom tables     |
| `DB_USER`     | Database user                               |
| `DB_PASSWORD` | Password for the database user              |

### Run the dashboard locally

```powershell
streamlit run scripts/dashboard.py
```

By default Streamlit opens at <http://localhost:8501>. Use the sidebar to navigate between the four analytic views. Missing data triggers inline warnings to help you validate the upstream pipeline.

## Working with notebooks

- Each notebook focuses on one analytics task and documents the feature engineering used to derive the aggregate scores.
- The shared `notebooks/artifacts/` directory stores intermediate parquet files that the dashboard can load without re-running the entire notebook stack.
- Commit large artifacts to object storage instead of the repo if you need to collaborate within a team.

## Development tips

- Re-create the combined dataset after modifying preprocessing logic so that column names stay in sync with the dashboard expectations.
- When deploying, ensure the environment variables are set and that the `scores_full` table or parquet file is available to the runtime.
- Streamlit caching (`@st.cache_data`) is enabled for data loading; clear the cache (`?cache=clear` suffix in the app URL) if you update the underlying dataset.

## Troubleshooting

- **`RuntimeError: Unable to load scores_full dataset`** – confirm the parquet artifact exists or that the SQL view is reachable from the deployment environment.
- **Module import errors** – run Streamlit from the project root so relative imports like `from load_data import ...` resolve correctly.
- **Trendline disabled warning** – install `statsmodels` if you want the engagement scatter plot to display the OLS trendline; the app will fall back to a scatter without it when `statsmodels` is missing.
- **Database timeouts** – verify firewall rules and that the credentials in `.env` match your PostgreSQL instance.

---

Made with ❤️ to accelerate telecom customer experience insights.
