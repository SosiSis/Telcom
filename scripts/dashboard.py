import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st
from load_data import load_data_from_postgres, load_data_using_sqlalchemy

try:
    import statsmodels.api  # noqa: F401
    HAS_STATSMODELS = True
except ModuleNotFoundError:
    HAS_STATSMODELS = False


st.set_page_config(
    page_title="Telecom Analytics Dashboard",
    page_icon="📶",
    layout="wide",
    menu_items={
        "About": "Task 5 dashboard combining Tasks 1-4 analytics with interactive visuals."
    },
)


@st.cache_data(show_spinner=False)
def load_processed_scores() -> pd.DataFrame:
    data_path = Path("notebooks") / "artifacts" / "scores_full.parquet"
    if data_path.exists():
        return pd.read_parquet(data_path)

    sql_candidates = [
        ("scores_full_view", "SELECT * FROM scores_full_view"),
        ("scores_full", "SELECT * FROM scores_full"),
    ]

    for source_name, query in sql_candidates:
        df = load_data_using_sqlalchemy(query)
        if df is not None and not df.empty:
            st.sidebar.success(f"Loaded data from {source_name}")
            return df

    raise RuntimeError(
        "Unable to load `scores_full` dataset. Upload `notebooks/artifacts/scores_full.parquet` "
        "or create the `scores_full` table/view in PostgreSQL."
    )


try:
    agg_data = load_processed_scores()
except Exception as exc:
    st.error(str(exc))
    st.stop()


metrics_columns = {
    "overview": [
        "MSISDN",
        "Handset Type",
        "engagement_score",
        "experience_score",
        "satisfaction_score",
    ],
    "engagement": [
        "Session Frequency",
        "Total Session Duration",
        "Total Traffic (Bytes)",
        "engagement_score",
        "Engagement Cluster",
    ],
    "experience": [
        "Handset Type",
        "Average TCP Retransmission",
        "Average RTT",
        "Average Throughput",
        "Experience Cluster",
    ],
    "satisfaction": [
        "MSISDN",
        "engagement_score",
        "experience_score",
        "satisfaction_score",
        "Satisfaction Cluster",
    ],
}

missing_columns = {
    section: [col for col in cols if col not in agg_data.columns]
    for section, cols in metrics_columns.items()
}
missing_columns = {k: v for k, v in missing_columns.items() if v}
if missing_columns:
    st.warning(
        "Some expected columns are missing. Please verify preprocessing pipeline before deploying the dashboard:\n"
        + "\n".join(f"- {section.title()}: {', '.join(cols)}" for section, cols in missing_columns.items())
    )

agg_data = agg_data.copy()
if "Total Traffic (Bytes)" in agg_data.columns and "Total Traffic (MB)" not in agg_data.columns:
    agg_data["Total Traffic (MB)"] = agg_data["Total Traffic (Bytes)"] / (1024 ** 2)


st.sidebar.title("Dashboard Navigation")
st.sidebar.caption("Select a task to explore its insights.")
page = st.sidebar.radio(
    "Go to",
    [
        "User Overview Analysis",
        "User Engagement Analysis",
        "Experience Analysis",
        "Satisfaction Analysis",
    ],
    label_visibility="collapsed",
)


def add_footer():
    st.markdown(
        "<div style='text-align: center; color: #888; margin-top: 2rem;'>"
        "Built with Streamlit • Telecom Analytics Dashboard"
        "</div>",
        unsafe_allow_html=True,
    )


def overview_page(data: pd.DataFrame):
    st.title("User Overview Analysis")
    st.subheader("High-level metrics and handset distribution")

    kpi_cols = st.columns(3)
    with kpi_cols[0]:
        st.metric("Total Users", f"{data['MSISDN'].nunique():,}")
    with kpi_cols[1]:
        st.metric("Average Engagement Score", f"{data['engagement_score'].mean():.2f}")
    with kpi_cols[2]:
        st.metric("Average Experience Score", f"{data['experience_score'].mean():.2f}")

    st.markdown("### Top Handsets by Count")
    handset_counts = data["Handset Type"].value_counts().head(10).reset_index()
    handset_counts.columns = ["Handset Type", "Users"]
    fig = px.bar(handset_counts, x="Handset Type", y="Users", color="Users", height=400)
    fig.update_layout(xaxis_tickangle=-30, margin=dict(t=20, b=100))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Summary Statistics")
    st.dataframe(data[[col for col in metrics_columns["overview"] if col in data.columns]].describe())


def engagement_page(data: pd.DataFrame):
    st.title("User Engagement Analysis")
    st.subheader("Session activity and usage clusters")

    engagement_cols = [col for col in metrics_columns["engagement"] if col in data.columns]
    engagement_df = data[engagement_cols].copy()

    cluster_counts = engagement_df["Engagement Cluster"].value_counts().sort_index()
    st.markdown("### Engagement Cluster Distribution")
    c_fig = px.pie(
        cluster_counts,
        values=cluster_counts.values,
        names=[f"Cluster {idx}" for idx in cluster_counts.index],
        color=cluster_counts.index,
        color_discrete_sequence=px.colors.sequential.Blues_r,
    )
    st.plotly_chart(c_fig, use_container_width=True)

    st.markdown("### Engagement vs. Total Traffic")
    trendline_mode = "ols" if HAS_STATSMODELS else None
    if not HAS_STATSMODELS:
        st.caption(
            "Install `statsmodels` to enable the OLS trendline in this scatter plot."
        )
    scatter_fig = px.scatter(
        data,
        x="engagement_score",
        y="Total Traffic (MB)",
        color="Engagement Cluster",
        hover_data=["MSISDN"],
        marginal_y="box",
        trendline=trendline_mode,
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

    st.markdown("### Top 10 Engaged Users")
    st.dataframe(
        data.nlargest(10, "engagement_score")[
            [col for col in ["MSISDN", "engagement_score", "Total Traffic (MB)"] if col in data.columns]
        ]
    )


def experience_page(data: pd.DataFrame):
    st.title("Experience Analysis")
    st.subheader("Network quality metrics by handset")

    pivot_cols = [col for col in ["Handset Type", "Experience Cluster", "Average RTT"] if col in data.columns]
    experience_df = data[pivot_cols].dropna()

    st.markdown("### Average RTT by Handset")
    rtt_fig = px.box(
        experience_df,
        x="Handset Type",
        y="Average RTT",
        color="Experience Cluster",
    )
    rtt_fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(rtt_fig, use_container_width=True)

    st.markdown("### Experience Score Distribution")
    hist_fig = px.histogram(
        data,
        x="experience_score",
        marginal="violin",
        color="Experience Cluster",
        nbins=40,
    )
    st.plotly_chart(hist_fig, use_container_width=True)


def satisfaction_page(data: pd.DataFrame):
    st.title("Satisfaction Analysis")
    st.subheader("Score segmentation and recommendations")

    st.markdown("### Satisfaction Score by Cluster")
    box_fig = px.box(
        data,
        x="Satisfaction Cluster",
            y="satisfaction_score",
        color="Satisfaction Cluster",
        points="all",
    )
    st.plotly_chart(box_fig, use_container_width=True)

    st.markdown("### Satisfaction vs. Engagement & Experience")
    radar_cols = ["engagement_score", "experience_score", "satisfaction_score"]
    radar_df = (
        data.groupby("Satisfaction Cluster")[radar_cols]
        .mean()
        .reset_index()
        .rename(columns={"Satisfaction Cluster": "Cluster"})
    )
    radar_fig = px.line_polar(
        radar_df.melt(id_vars="Cluster", value_vars=radar_cols, var_name="Metric", value_name="Score"),
        r="Score",
        theta="Metric",
        color="Cluster",
        line_close=True,
    )
    st.plotly_chart(radar_fig, use_container_width=True)

    st.markdown("### Top 10 Satisfied Users")
    st.dataframe(
        data.nlargest(10, "satisfaction_score")[["MSISDN", "satisfaction_score", "Satisfaction Cluster"]]
    )


page_renderers = {
    "User Overview Analysis": overview_page,
    "User Engagement Analysis": engagement_page,
    "Experience Analysis": experience_page,
    "Satisfaction Analysis": satisfaction_page,
}

page_renderers[page](agg_data)
add_footer()

