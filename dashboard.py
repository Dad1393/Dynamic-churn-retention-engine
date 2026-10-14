
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Churn Prevention & Retention Engine",
    page_icon="📈",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "churn_project.sqlite"
RISK_PATH = BASE_DIR / "churn_risk_segments.csv"
IMPACT_PATH = BASE_DIR / "retention_impact_by_offer.csv"

st.title("Dynamic Churn Prevention & Retention Growth Engine")
st.caption("Portfolio project | Synthetic subscription dataset")

if not DB_PATH.exists():
    st.error("Database not found. Keep dashboard.py beside churn_project.sqlite.")
    st.stop()

# Load the data
with sqlite3.connect(DB_PATH) as conn:
    subscriptions = pd.read_sql_query(
        "SELECT * FROM subscriptions", conn
    )
    cancellation = pd.read_sql_query(
        "SELECT * FROM cancellation_events", conn
    )

if RISK_PATH.exists():
    risk = pd.read_csv(RISK_PATH)
else:
    risk = pd.DataFrame()

if IMPACT_PATH.exists():
    impact = pd.read_csv(IMPACT_PATH)
else:
    impact = pd.DataFrame()

# Sidebar filters
st.sidebar.header("Dashboard filters")

if not subscriptions.empty and "status" in subscriptions.columns:
    statuses = sorted(subscriptions["status"].dropna().unique().tolist())
    selected_statuses = st.sidebar.multiselect(
        "Subscription status",
        statuses,
        default=statuses
    )
    filtered_subscriptions = subscriptions[
        subscriptions["status"].isin(selected_statuses)
    ]
else:
    filtered_subscriptions = subscriptions

# Top-level KPIs
total_subscriptions = len(filtered_subscriptions)
active_count = (
    filtered_subscriptions["status"].eq("active").sum()
    if "status" in filtered_subscriptions.columns else 0
)
canceled_count = (
    filtered_subscriptions["status"].eq("canceled").sum()
    if "status" in filtered_subscriptions.columns else 0
)
paused_count = (
    filtered_subscriptions["status"].eq("paused").sum()
    if "status" in filtered_subscriptions.columns else 0
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Subscriptions", f"{total_subscriptions:,}")
col2.metric("Active", f"{active_count:,}")
col3.metric("Canceled", f"{canceled_count:,}")
col4.metric("Paused", f"{paused_count:,}")

st.divider()

# Risk segmentation
st.subheader("1. Customer churn-risk segments")

if not risk.empty and "risk_segment" in risk.columns:
    risk_counts = (
        risk["risk_segment"]
        .value_counts()
        .rename_axis("Risk segment")
        .reset_index(name="Customers")
    )
    st.plotly_chart(
        px.bar(
            risk_counts,
            x="Risk segment",
            y="Customers",
            color="Risk segment",
            title="Customers by risk segment"
        ),
        use_container_width=True
    )

    st.dataframe(risk.head(100), use_container_width=True)
else:
    st.info("Run churn_segmentation.py to generate the risk CSV.")

st.divider()

# Cancellation reasons
st.subheader("2. Cancellation reasons")

if not cancellation.empty and "cancellation_reason" in cancellation.columns:
    reason_counts = (
        cancellation["cancellation_reason"]
        .value_counts()
        .rename_axis("Reason")
        .reset_index(name="Attempts")
    )
    st.plotly_chart(
        px.bar(
            reason_counts,
            x="Attempts",
            y="Reason",
            orientation="h",
            title="Cancellation attempts by reason"
        ),
        use_container_width=True
    )

st.divider()

# Experiment analysis
st.subheader("3. Control vs. treatment")

if not cancellation.empty and {
    "experiment_group", "outcome"
}.issubset(cancellation.columns):
    experiment = cancellation[
        cancellation["experiment_group"].isin(["control", "treatment"])
    ].copy()

    experiment["saved"] = experiment["outcome"].eq("retained")

    summary = (
        experiment.groupby("experiment_group")
        .agg(attempts=("saved", "size"), saved=("saved", "sum"))
        .reset_index()
    )
    summary["save_rate_pct"] = (
        summary["saved"] / summary["attempts"] * 100
    )

    st.dataframe(summary, use_container_width=True)

    st.plotly_chart(
        px.bar(
            summary,
            x="experiment_group",
            y="save_rate_pct",
            text="save_rate_pct",
            title="Save rate by experiment group",
            labels={
                "experiment_group": "Experiment group",
                "save_rate_pct": "Save rate (%)"
            }
        ),
        use_container_width=True
    )

    if set(summary["experiment_group"]) == {"control", "treatment"}:
        rates = summary.set_index("experiment_group")["save_rate_pct"]
        lift = rates["treatment"] - rates["control"]
        st.metric("Treatment absolute lift", f"{lift:+.2f} percentage points")

st.divider()

# Retention offers
st.subheader("4. Retention offer performance")

if not impact.empty and "selected_offer" in impact.columns:
    st.dataframe(impact, use_container_width=True)

    if {"selected_offer", "save_rate_pct"}.issubset(impact.columns):
        st.plotly_chart(
            px.bar(
                impact.sort_values("save_rate_pct"),
                x="save_rate_pct",
                y="selected_offer",
                orientation="h",
                title="Save rate by selected offer",
                labels={
                    "selected_offer": "Retention offer",
                    "save_rate_pct": "Save rate (%)"
                }
            ),
            use_container_width=True
        )

    if "estimated_monthly_revenue_associated" in impact.columns:
        st.caption(
            "Revenue is an estimate associated with retained events, "
            "not proven incremental revenue."
        )
else:
    st.info("Run retention_impact.py to generate the impact CSV.")

st.divider()

st.subheader("5. Product recommendations")

st.markdown("""
- **Price-sensitive customers:** test a lower-cost plan against the existing experience.
- **Temporarily leaving customers:** test an account pause with a defined restart date.
- **Low-usage customers:** test contextual onboarding and usage guidance.
- **Payment problems:** test payment recovery before offering discounts.
- **Experimentation:** compare outcomes using randomized groups and a predefined success metric.
""")

st.caption(
    "All data is synthetic. Dashboard metrics are descriptive and should not "
    "be presented as verified real-world business results."
)
