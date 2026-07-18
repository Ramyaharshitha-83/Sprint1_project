import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go

DB_PATH = "data/nifty100.db"


@st.cache_data(ttl=600)
def load_data():

    conn = sqlite3.connect(DB_PATH)

    peers = pd.read_sql(
        "SELECT * FROM peer_groups",
        conn
    )

    ratios = pd.read_sql(
        "SELECT * FROM financial_ratios",
        conn
    )

    companies = pd.read_sql(
        "SELECT id, company_name FROM companies",
        conn
    )

    conn.close()

    companies.rename(
        columns={"id": "company_id"},
        inplace=True
    )

    return peers, ratios, companies


peers, ratios, companies = load_data()

st.title("🤝 Peer Comparison")

# ------------------------------------------------
# Peer Group
# ------------------------------------------------

groups = sorted(peers["peer_group_name"].unique())

group = st.sidebar.selectbox(
    "Peer Group",
    groups
)

peer_df = peers[
    peers["peer_group_name"] == group
]

company_ids = peer_df["company_id"].tolist()

ticker = st.selectbox(
    "Select Company",
    company_ids
)

# ------------------------------------------------
# Latest Annual Data
# ------------------------------------------------

latest = ratios[
    ratios["year"] == "Mar 2024"
]

latest = latest[
    latest["company_id"].isin(company_ids)
]

metrics = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "asset_turnover",
    "debt_to_equity",
    "interest_coverage",
    "earnings_per_share",
    "book_value_per_share",
    "free_cash_flow_cr"
]

available = [
    c for c in metrics
    if c in latest.columns
]

peer_avg = latest[available].mean()

company = latest[
    latest["company_id"] == ticker
].iloc[0]

# -----------------------------
# Normalize metrics (0-100)
# -----------------------------

normalized_company = []
normalized_peer = []

for metric in available:

    values = latest[metric].fillna(0)

    min_val = values.min()
    max_val = values.max()

    if max_val == min_val:
        normalized_company.append(50)
        normalized_peer.append(50)
    else:
        normalized_company.append(
            ((company[metric] - min_val) / (max_val - min_val)) * 100
        )

        normalized_peer.append(
            ((peer_avg[metric] - min_val) / (max_val - min_val)) * 100
        )

# ------------------------------------------------
# Radar Chart
# ------------------------------------------------

st.subheader("Radar Chart")

fig = go.Figure()

fig.add_trace(
    go.Scatterpolar(
        r=normalized_company,
        theta=available,
        fill="toself",
        name=ticker
    )
)

fig.add_trace(
    go.Scatterpolar(
        r=normalized_peer,
        theta=available,
        fill="toself",
        name="Peer Average"
    )
)

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 100]
        )
    ),
    height=650,
    showlegend=True
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# ------------------------------------------------
# Peer Table
# ------------------------------------------------

st.subheader("Peer Companies")

table = latest.merge(
    companies,
    on="company_id",
    how="left"
)

table = table[
    table["company_id"].isin(company_ids)
]

benchmark = peer_df[
    peer_df["is_benchmark"] == 1
]["company_id"].iloc[0]

table["Benchmark"] = table["company_id"].apply(
    lambda x: "⭐" if x == benchmark else ""
)

columns = [
    "Benchmark",
    "company_id",
    "company_name"
] + available

st.dataframe(
    table[columns],
    hide_index=True,
    use_container_width=True,
    height=450
)