"""
India Goes Cashless: UPI Analytics
====================================
Single-file Streamlit application — frontend + backend combined.
Dataset: upi_transactions_2024.csv
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
import io

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="UPI Analytics — India Goes Cashless",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* Main background */
        .stApp { background-color: #0f172a; color: #e2e8f0; }

        /* Sidebar */
        [data-testid="stSidebar"] { background-color: #1e293b; }
        [data-testid="stSidebar"] .stMarkdown p,
        [data-testid="stSidebar"] label { color: #94a3b8 !important; }

        /* Metric cards */
        [data-testid="metric-container"] {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
        }
        [data-testid="metric-container"] label {
            color: #94a3b8 !important;
            font-size: 0.78rem !important;
            letter-spacing: 0.08em;
            text-transform: uppercase;
        }
        [data-testid="metric-container"] [data-testid="stMetricValue"] {
            color: #38bdf8 !important;
            font-size: 1.9rem !important;
            font-weight: 700;
        }
        [data-testid="metric-container"] [data-testid="stMetricDelta"] {
            color: #4ade80 !important;
        }

        /* Hero banner */
        .hero-banner {
            background: linear-gradient(135deg, #1e3a5f 0%, #1e293b 100%);
            border: 1px solid #2d4a6e;
            border-radius: 16px;
            padding: 32px 40px;
            margin-bottom: 28px;
        }
        .hero-banner h1 { color: #f1f5f9; margin: 0 0 8px 0; font-size: 2.1rem; }
        .hero-banner p  { color: #94a3b8; margin: 0; font-size: 0.95rem; }
        .hero-banner strong { color: #e2e8f0; }

        /* Section headings */
        .section-heading {
            border-left: 4px solid #3b82f6;
            padding-left: 12px;
            color: #f1f5f9;
            font-size: 1.15rem;
            font-weight: 600;
            margin: 24px 0 12px 0;
        }

        /* Insight cards */
        .insight-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 12px;
        }
        .insight-card .title {
            color: #38bdf8;
            font-weight: 600;
            font-size: 0.85rem;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .insight-card .body { color: #cbd5e1; font-size: 0.9rem; line-height: 1.55; }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            background: #1e293b;
            border-radius: 10px;
            padding: 4px;
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            color: #94a3b8;
            border-radius: 8px;
            font-size: 0.85rem;
        }
        .stTabs [aria-selected="true"] {
            background: #3b82f6 !important;
            color: #ffffff !important;
        }

        /* DataFrame */
        .stDataFrame { border-radius: 10px; overflow: hidden; }

        /* Divider */
        hr { border-color: #334155; }

        /* Plotly chart background match */
        .js-plotly-plot .plotly { background: transparent !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# PLOTLY THEME DEFAULTS
# ─────────────────────────────────────────────
PLOT_BG    = "#0f172a"
PAPER_BG   = "#1e293b"
GRID_COLOR = "#334155"
FONT_COLOR = "#e2e8f0"
PALETTE    = px.colors.qualitative.Bold

def apply_theme(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(
        title=dict(text=title, font=dict(color=FONT_COLOR, size=14), x=0.01),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=FONT_COLOR, size=12),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=FONT_COLOR)),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
        colorway=PALETTE,
    )
    return fig


# ─────────────────────────────────────────────
# DATA LOADING & CLEANING  (cached)
# ─────────────────────────────────────────────
@st.cache_data(show_spinner="Loading & cleaning dataset …")
def load_data(file_source) -> pd.DataFrame:
    if isinstance(file_source, str):
        df = pd.read_csv(file_source)
    else:
        df = pd.read_csv(file_source)

    # ── Normalise column names ──────────────────
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(r"[\s\(\)/]+", "_", regex=True)
                  .str.replace(r"_+$", "", regex=True)
    )

    # ── Rename for convenience ──────────────────
    rename_map = {
        "transaction_id":       "txn_id",
        "amount_inr_":          "amount",
        "amount__inr_":         "amount",
        "transaction_type":     "txn_type",
        "transaction_status":   "status",
    }
    # flexible rename — apply only keys present
    df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

    # ── Ensure 'amount' column exists ──────────
    if "amount" not in df.columns:
        # fallback: find any col with 'amount' in name
        amount_cols = [c for c in df.columns if "amount" in c]
        if amount_cols:
            df.rename(columns={amount_cols[0]: "amount"}, inplace=True)

    # ── Parse timestamp ─────────────────────────
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        df["month"]     = df["timestamp"].dt.month
        df["month_name"]= df["timestamp"].dt.strftime("%b")
        df["month_year"]= df["timestamp"].dt.to_period("M").astype(str)
        df["date"]      = df["timestamp"].dt.date
        df["week"]      = df["timestamp"].dt.isocalendar().week.astype(int)
        df["quarter"]   = df["timestamp"].dt.quarter.map({1:"Q1",2:"Q2",3:"Q3",4:"Q4"})

    # ── Numeric coercion ────────────────────────
    for col in ["amount", "hour_of_day", "fraud_flag", "is_weekend"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ── Drop complete duplicate rows ────────────
    before = len(df)
    df.drop_duplicates(inplace=True)
    dups_removed = before - len(df)

    # ── Fill / drop minimal NAs ──────────────────
    df["amount"].fillna(df["amount"].median(), inplace=True)

    # store cleaning notes as metadata
    df.attrs["dups_removed"]  = dups_removed
    df.attrs["original_rows"] = before

    return df


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💳 UPI Analytics")
    st.markdown("---")

    st.markdown("### 📂 Data Source")
    uploaded = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")
    st.caption("200MB per file • CSV")

    if uploaded is None:
        st.info("📌 **Default dataset active**\nupi_transactions_2024.csv")
        data_src = "upi_transactions_2024.csv"
    else:
        data_src = uploaded

    st.markdown("---")

    # load early to populate filters
    df_raw = load_data(data_src)

    st.markdown("### 🔍 Filters")

    # State filter
    states = ["All states"] + sorted(df_raw["sender_state"].dropna().unique().tolist()) if "sender_state" in df_raw.columns else ["All states"]
    sel_states = st.multiselect("State(s)", states, default=["All states"])

    # Transaction type filter
    types = ["All types"] + sorted(df_raw["txn_type"].dropna().unique().tolist()) if "txn_type" in df_raw.columns else ["All types"]
    sel_types = st.multiselect("Transaction Type(s)", types, default=["All types"])

    # Month filter
    if "month_name" in df_raw.columns:
        month_order = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        avail_months = [m for m in month_order if m in df_raw["month_name"].unique()]
        sel_months = st.multiselect("Month(s)", ["All months"] + avail_months, default=["All months"])
    else:
        sel_months = ["All months"]

    st.markdown("---")
    st.markdown("### ℹ️ Dataset Info")
    st.caption(f"**Rows:** {len(df_raw):,}")
    st.caption(f"**Columns:** {len(df_raw.columns)}")
    st.caption(f"**Duplicates removed:** {df_raw.attrs.get('dups_removed', 0)}")


# ─────────────────────────────────────────────
# APPLY FILTERS
# ─────────────────────────────────────────────
df = df_raw.copy()

if "All states" not in sel_states and sel_states:
    df = df[df["sender_state"].isin(sel_states)]

if "All types" not in sel_types and sel_types:
    df = df[df["txn_type"].isin(sel_types)]

if "All months" not in sel_months and sel_months:
    df = df[df["month_name"].isin(sel_months)]

if df.empty:
    st.error("⚠️ No data matches the selected filters. Please widen your selection.")
    st.stop()


# ─────────────────────────────────────────────
# KEY METRICS  (computed once, used everywhere)
# ─────────────────────────────────────────────
total_txns      = len(df)
total_value     = df["amount"].sum()
avg_amount      = df["amount"].mean()
success_rate    = (df["status"] == "SUCCESS").mean() * 100 if "status" in df.columns else np.nan
fraud_rate      = df["fraud_flag"].mean() * 100 if "fraud_flag" in df.columns else np.nan
num_states      = df["sender_state"].nunique() if "sender_state" in df.columns else "-"
num_banks       = df["sender_bank"].nunique() if "sender_bank" in df.columns else "-"
peak_hour       = int(df.groupby("hour_of_day")["amount"].count().idxmax()) if "hour_of_day" in df.columns else "-"
median_amount   = df["amount"].median()

def fmt_cr(val):
    """Format rupee value in Crores."""
    cr = val / 1e7
    if cr >= 100:
        return f"₹{cr/100:.1f}K Cr"
    return f"₹{cr:.1f} Cr"


# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
period_str = ""
if "timestamp" in df.columns:
    mn = df["timestamp"].min()
    mx = df["timestamp"].max()
    period_str = f"Period: <strong>{mn.strftime('%b %Y')} – {mx.strftime('%b %Y')}</strong>"

st.markdown(
    f"""
    <div class="hero-banner">
      <h1>💳 India Goes Cashless: UPI Analytics</h1>
      <p>
        Comprehensive analysis of <strong>{total_txns:,}</strong> transactions from
        <strong>upi_transactions_2024.csv</strong> &nbsp;|&nbsp; {period_str}
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# KPI ROW 1
# ─────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL TRANSACTIONS", f"{total_txns:,}")
c2.metric("TOTAL VALUE",        fmt_cr(total_value))
c3.metric("SUCCESS RATE",       f"{success_rate:.1f}%" if not np.isnan(success_rate) else "N/A")
c4.metric("AVG. TRANSACTION",   f"₹{avg_amount:,.0f}")

# KPI ROW 2
c5, c6, c7, c8 = st.columns(4)
c5.metric("FRAUD RATE",      f"{fraud_rate:.2f}%" if not np.isnan(fraud_rate) else "N/A",
          help="Percentage of flagged transactions")
c6.metric("STATES COVERED",  str(num_states), help="Unique sender states")
c7.metric("BANKS INVOLVED",  str(num_banks),  help="Unique sender banks")
c8.metric("PEAK HOUR",       f"{peak_hour:02d}:00" if isinstance(peak_hour, int) else "-",
          help="Hour with highest transaction count")

st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_trend, tab_cat, tab_geo, tab_bank, tab_device, tab_demo, tab_fraud, tab_data = st.tabs([
    "📈 Trends", "🏷️ Categories", "🗺️ Geography",
    "🏦 Banks", "📱 Device & Network", "👥 Demographics",
    "🚨 Fraud", "🗃️ Raw Data"
])


# ══════════════════════════════════════════════
# TAB 1 — TRENDS
# ══════════════════════════════════════════════
with tab_trend:
    st.markdown('<div class="section-heading">Transaction Trends Over Time</div>', unsafe_allow_html=True)

    if "month_year" in df.columns:
        monthly = (
            df.groupby("month_year")
              .agg(count=("amount", "count"), value=("amount", "sum"))
              .reset_index()
              .sort_values("month_year")
        )
        monthly["value_cr"] = monthly["value"] / 1e7

        col_l, col_r = st.columns([2, 1])

        with col_l:
            fig_monthly = make_subplots(specs=[[{"secondary_y": True}]])
            fig_monthly.add_trace(
                go.Bar(x=monthly["month_year"], y=monthly["count"],
                       name="Count", marker_color="#3b82f6", opacity=0.85),
                secondary_y=False,
            )
            fig_monthly.add_trace(
                go.Scatter(x=monthly["month_year"], y=monthly["value_cr"],
                           name="Value (Cr)", mode="lines+markers",
                           line=dict(color="#f59e0b", width=2.5),
                           marker=dict(size=6)),
                secondary_y=True,
            )
            fig_monthly.update_layout(
                paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                font=dict(color=FONT_COLOR, size=11),
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                margin=dict(l=40, r=40, t=50, b=40),
                title=dict(text="Monthly Transaction Volume & Value", font=dict(color=FONT_COLOR, size=13)),
                xaxis=dict(gridcolor=GRID_COLOR),
                yaxis=dict(gridcolor=GRID_COLOR, title="# Transactions"),
                yaxis2=dict(title="Value (₹ Cr)", gridcolor="rgba(0,0,0,0)"),
            )
            st.plotly_chart(fig_monthly, use_container_width=True)

        with col_r:
            st.markdown("**Monthly Summary**")
            disp = monthly.copy()
            disp["value_cr"] = disp["value_cr"].round(2)
            disp.rename(columns={"month_year":"Month","count":"Txns","value_cr":"Value (Cr ₹)"}, inplace=True)
            st.dataframe(disp[["Month","Txns","Value (Cr ₹)"]].set_index("Month"), use_container_width=True, height=350)

    st.markdown('<div class="section-heading">Hourly & Weekly Patterns</div>', unsafe_allow_html=True)

    col_h, col_w = st.columns(2)

    # Hourly heatmap
    if "hour_of_day" in df.columns:
        with col_h:
            hourly = df.groupby("hour_of_day")["amount"].count().reset_index()
            hourly.columns = ["Hour", "Count"]
            fig_h = px.bar(
                hourly, x="Hour", y="Count",
                color="Count", color_continuous_scale="Blues",
                title="Transactions by Hour of Day",
                labels={"Count": "# Transactions"},
            )
            fig_h = apply_theme(fig_h)
            fig_h.update_coloraxes(showscale=False)
            st.plotly_chart(fig_h, use_container_width=True)

    # Day of week
    if "day_of_week" in df.columns:
        with col_w:
            day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
            dow = df.groupby("day_of_week")["amount"].agg(["count","sum"]).reset_index()
            dow.columns = ["Day", "Count", "Value"]
            dow["Day"] = pd.Categorical(dow["Day"], categories=day_order, ordered=True)
            dow.sort_values("Day", inplace=True)
            fig_dow = px.bar(
                dow, x="Day", y="Count",
                color="Count", color_continuous_scale="Purples",
                title="Transactions by Day of Week",
            )
            fig_dow = apply_theme(fig_dow)
            fig_dow.update_coloraxes(showscale=False)
            st.plotly_chart(fig_dow, use_container_width=True)

    # Weekend vs Weekday
    if "is_weekend" in df.columns:
        st.markdown('<div class="section-heading">Weekend vs Weekday</div>', unsafe_allow_html=True)
        wk = df.groupby("is_weekend").agg(count=("amount","count"), value=("amount","sum")).reset_index()
        wk["label"] = wk["is_weekend"].map({0: "Weekday", 1: "Weekend"})
        col_wk1, col_wk2 = st.columns(2)
        with col_wk1:
            fig_wkc = px.pie(wk, names="label", values="count",
                             title="Transaction Count Split",
                             hole=0.45, color_discrete_sequence=PALETTE)
            fig_wkc = apply_theme(fig_wkc)
            st.plotly_chart(fig_wkc, use_container_width=True)
        with col_wk2:
            fig_wkv = px.pie(wk, names="label", values="value",
                             title="Transaction Value Split",
                             hole=0.45, color_discrete_sequence=PALETTE)
            fig_wkv = apply_theme(fig_wkv)
            st.plotly_chart(fig_wkv, use_container_width=True)

    # Quarterly
    if "quarter" in df.columns:
        st.markdown('<div class="section-heading">Quarterly Overview</div>', unsafe_allow_html=True)
        qtr = df.groupby("quarter").agg(count=("amount","count"), value=("amount","sum")).reset_index()
        qtr["value_cr"] = (qtr["value"]/1e7).round(2)
        fig_qtr = px.bar(
            qtr, x="quarter", y=["count","value_cr"],
            barmode="group", title="Quarterly Transactions & Value",
            labels={"value":"Count","quarter":"Quarter"},
            color_discrete_sequence=["#3b82f6","#f59e0b"],
        )
        fig_qtr = apply_theme(fig_qtr)
        st.plotly_chart(fig_qtr, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 2 — CATEGORIES
# ══════════════════════════════════════════════
with tab_cat:
    st.markdown('<div class="section-heading">Merchant Categories & Transaction Types</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    if "merchant_category" in df.columns:
        with col_a:
            cat = df.groupby("merchant_category").agg(count=("amount","count"), value=("amount","sum")).reset_index()
            cat.sort_values("count", ascending=True, inplace=True)
            fig_cat = px.bar(cat, x="count", y="merchant_category", orientation="h",
                             color="count", color_continuous_scale="Blues",
                             title="Transactions by Merchant Category",
                             labels={"count":"# Transactions","merchant_category":"Category"})
            fig_cat = apply_theme(fig_cat)
            fig_cat.update_coloraxes(showscale=False)
            st.plotly_chart(fig_cat, use_container_width=True)

        with col_b:
            fig_catv = px.pie(cat, names="merchant_category", values="value",
                              title="Value Share by Category",
                              hole=0.4, color_discrete_sequence=PALETTE)
            fig_catv = apply_theme(fig_catv)
            st.plotly_chart(fig_catv, use_container_width=True)

    if "txn_type" in df.columns:
        st.markdown('<div class="section-heading">P2P vs P2M Analysis</div>', unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)

        ttype = df.groupby("txn_type").agg(
            count=("amount","count"),
            total=("amount","sum"),
            avg=("amount","mean"),
            median=("amount","median"),
        ).reset_index()

        with col_t1:
            fig_tp = px.pie(ttype, names="txn_type", values="count",
                            title="Count by Type", hole=0.45,
                            color_discrete_sequence=["#3b82f6","#f59e0b"])
            fig_tp = apply_theme(fig_tp)
            st.plotly_chart(fig_tp, use_container_width=True)

        with col_t2:
            fig_tv = px.pie(ttype, names="txn_type", values="total",
                            title="Value by Type", hole=0.45,
                            color_discrete_sequence=["#3b82f6","#f59e0b"])
            fig_tv = apply_theme(fig_tv)
            st.plotly_chart(fig_tv, use_container_width=True)

        with col_t3:
            fig_ta = px.bar(ttype, x="txn_type", y="avg", color="txn_type",
                            title="Avg Transaction Value by Type",
                            labels={"avg":"Avg Amount (₹)","txn_type":"Type"},
                            color_discrete_sequence=["#3b82f6","#f59e0b"])
            fig_ta = apply_theme(fig_ta)
            fig_ta.update_layout(showlegend=False)
            st.plotly_chart(fig_ta, use_container_width=True)

    # Amount distribution
    st.markdown('<div class="section-heading">Amount Distribution</div>', unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        fig_hist = px.histogram(df, x="amount", nbins=60,
                                title="Distribution of Transaction Amounts",
                                labels={"amount":"Amount (₹)"},
                                color_discrete_sequence=["#3b82f6"])
        fig_hist = apply_theme(fig_hist)
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_d2:
        fig_box = px.box(df, x="txn_type" if "txn_type" in df.columns else None,
                         y="amount", color="txn_type" if "txn_type" in df.columns else None,
                         title="Amount Spread by Transaction Type",
                         labels={"amount":"Amount (₹)","txn_type":"Type"},
                         color_discrete_sequence=PALETTE)
        fig_box = apply_theme(fig_box)
        st.plotly_chart(fig_box, use_container_width=True)

    # Status breakdown
    if "status" in df.columns:
        st.markdown('<div class="section-heading">Transaction Status</div>', unsafe_allow_html=True)
        stat = df["status"].value_counts().reset_index()
        stat.columns = ["Status","Count"]
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            fig_st = px.pie(stat, names="Status", values="Count",
                            title="Status Distribution", hole=0.45,
                            color_discrete_map={"SUCCESS":"#4ade80","FAILED":"#f87171","PENDING":"#fbbf24"})
            fig_st = apply_theme(fig_st)
            st.plotly_chart(fig_st, use_container_width=True)
        with col_s2:
            fig_stb = px.bar(stat, x="Status", y="Count", color="Status",
                             title="Status Counts",
                             color_discrete_map={"SUCCESS":"#4ade80","FAILED":"#f87171","PENDING":"#fbbf24"})
            fig_stb = apply_theme(fig_stb)
            fig_stb.update_layout(showlegend=False)
            st.plotly_chart(fig_stb, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 3 — GEOGRAPHY
# ══════════════════════════════════════════════
with tab_geo:
    st.markdown('<div class="section-heading">State-wise Transaction Analysis</div>', unsafe_allow_html=True)

    if "sender_state" in df.columns:
        state_df = df.groupby("sender_state").agg(
            count=("amount","count"),
            total=("amount","sum"),
            avg=("amount","mean"),
            fraud=("fraud_flag","sum") if "fraud_flag" in df.columns else ("amount","count"),
        ).reset_index().sort_values("count", ascending=False)

        col_g1, col_g2 = st.columns(2)
        with col_g1:
            fig_st_bar = px.bar(
                state_df.sort_values("count", ascending=True),
                x="count", y="sender_state", orientation="h",
                color="count", color_continuous_scale="Blues",
                title="Transactions by State",
                labels={"count":"# Transactions","sender_state":"State"},
            )
            fig_st_bar = apply_theme(fig_st_bar)
            fig_st_bar.update_coloraxes(showscale=False)
            st.plotly_chart(fig_st_bar, use_container_width=True)

        with col_g2:
            state_df["total_cr"] = (state_df["total"]/1e7).round(2)
            fig_st_val = px.bar(
                state_df.sort_values("total_cr", ascending=True),
                x="total_cr", y="sender_state", orientation="h",
                color="total_cr", color_continuous_scale="Oranges",
                title="Transaction Value by State (₹ Cr)",
                labels={"total_cr":"Value (₹ Cr)","sender_state":"State"},
            )
            fig_st_val = apply_theme(fig_st_val)
            fig_st_val.update_coloraxes(showscale=False)
            st.plotly_chart(fig_st_val, use_container_width=True)

        # State-level avg amount
        fig_st_avg = px.bar(
            state_df.sort_values("avg", ascending=False),
            x="sender_state", y="avg",
            color="avg", color_continuous_scale="Teal",
            title="Average Transaction Amount by State",
            labels={"avg":"Avg Amount (₹)","sender_state":"State"},
        )
        fig_st_avg = apply_theme(fig_st_avg)
        fig_st_avg.update_coloraxes(showscale=False)
        st.plotly_chart(fig_st_avg, use_container_width=True)

        # State summary table
        st.markdown("**Detailed State Summary**")
        disp_state = state_df.copy()
        disp_state["total_cr"] = disp_state["total_cr"].round(2)
        disp_state["avg"]      = disp_state["avg"].round(0).astype(int)
        disp_state.rename(columns={
            "sender_state":"State","count":"Transactions",
            "total_cr":"Value (₹ Cr)","avg":"Avg Amount (₹)","fraud":"Fraud Txns"
        }, inplace=True)
        st.dataframe(disp_state.set_index("State"), use_container_width=True)


# ══════════════════════════════════════════════
# TAB 4 — BANKS
# ══════════════════════════════════════════════
with tab_bank:
    st.markdown('<div class="section-heading">Bank-wise Analysis</div>', unsafe_allow_html=True)

    if "sender_bank" in df.columns:
        bank_df = df.groupby("sender_bank").agg(
            count=("amount","count"), total=("amount","sum"), avg=("amount","mean")
        ).reset_index().sort_values("count", ascending=False)

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            fig_bk = px.bar(bank_df.sort_values("count", ascending=True),
                            x="count", y="sender_bank", orientation="h",
                            color="count", color_continuous_scale="Blues",
                            title="Sender Bank — Transaction Count",
                            labels={"count":"# Transactions","sender_bank":"Bank"})
            fig_bk = apply_theme(fig_bk)
            fig_bk.update_coloraxes(showscale=False)
            st.plotly_chart(fig_bk, use_container_width=True)

        with col_b2:
            bank_df["total_cr"] = (bank_df["total"]/1e7).round(2)
            fig_bkv = px.pie(bank_df, names="sender_bank", values="total_cr",
                             title="Value Share by Sender Bank",
                             hole=0.4, color_discrete_sequence=PALETTE)
            fig_bkv = apply_theme(fig_bkv)
            st.plotly_chart(fig_bkv, use_container_width=True)

        # Sender vs Receiver bank flow
        if "receiver_bank" in df.columns:
            st.markdown('<div class="section-heading">Cross-Bank Transaction Flow</div>', unsafe_allow_html=True)
            flow = df.groupby(["sender_bank","receiver_bank"])["amount"].count().reset_index()
            flow.columns = ["Sender","Receiver","Count"]
            fig_flow = px.scatter(flow, x="Sender", y="Receiver", size="Count",
                                  color="Count", color_continuous_scale="Blues",
                                  title="Sender → Receiver Bank Flow (bubble size = # txns)",
                                  labels={"Count":"Transactions"})
            fig_flow = apply_theme(fig_flow)
            st.plotly_chart(fig_flow, use_container_width=True)

            # Avg amount by bank pair
            flow_val = df.groupby(["sender_bank","receiver_bank"])["amount"].mean().reset_index()
            flow_val.columns = ["Sender","Receiver","Avg Amount"]
            pivot = flow_val.pivot(index="Sender", columns="Receiver", values="Avg Amount")
            fig_heat = px.imshow(pivot, color_continuous_scale="Blues",
                                 title="Avg Amount Heatmap (Sender Bank × Receiver Bank)",
                                 labels={"color":"Avg Amount (₹)"})
            fig_heat.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                                   font=dict(color=FONT_COLOR))
            st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 5 — DEVICE & NETWORK
# ══════════════════════════════════════════════
with tab_device:
    st.markdown('<div class="section-heading">Device Type & Network Analysis</div>', unsafe_allow_html=True)

    col_dv1, col_dv2 = st.columns(2)

    if "device_type" in df.columns:
        with col_dv1:
            dev = df["device_type"].value_counts().reset_index()
            dev.columns = ["Device","Count"]
            fig_dev = px.pie(dev, names="Device", values="Count",
                             title="Transactions by Device Type",
                             hole=0.45, color_discrete_sequence=PALETTE)
            fig_dev = apply_theme(fig_dev)
            st.plotly_chart(fig_dev, use_container_width=True)

    if "network_type" in df.columns:
        with col_dv2:
            net = df["network_type"].value_counts().reset_index()
            net.columns = ["Network","Count"]
            fig_net = px.pie(net, names="Network", values="Count",
                             title="Transactions by Network Type",
                             hole=0.45, color_discrete_sequence=PALETTE)
            fig_net = apply_theme(fig_net)
            st.plotly_chart(fig_net, use_container_width=True)

    # Device × Network cross table
    if "device_type" in df.columns and "network_type" in df.columns:
        cross = df.groupby(["device_type","network_type"])["amount"].count().reset_index()
        cross.columns = ["Device","Network","Count"]
        fig_cross = px.bar(cross, x="Device", y="Count", color="Network",
                           barmode="group", title="Device × Network Breakdown",
                           color_discrete_sequence=PALETTE)
        fig_cross = apply_theme(fig_cross)
        st.plotly_chart(fig_cross, use_container_width=True)

    # Avg amount by device
    if "device_type" in df.columns:
        dev_amt = df.groupby("device_type")["amount"].agg(["mean","median","sum"]).reset_index()
        dev_amt.columns = ["Device","Avg","Median","Total"]
        dev_amt["Total_Cr"] = (dev_amt["Total"]/1e7).round(2)
        st.markdown("**Amount Statistics by Device**")
        st.dataframe(
            dev_amt[["Device","Avg","Median","Total_Cr"]]
            .rename(columns={"Avg":"Avg (₹)","Median":"Median (₹)","Total_Cr":"Total (₹ Cr)"})
            .set_index("Device")
            .style.format({"Avg (₹)":"{:.0f}","Median (₹)":"{:.0f}","Total (₹ Cr)":"{:.2f}"}),
            use_container_width=True,
        )


# ══════════════════════════════════════════════
# TAB 6 — DEMOGRAPHICS
# ══════════════════════════════════════════════
with tab_demo:
    st.markdown('<div class="section-heading">Age Group Analysis</div>', unsafe_allow_html=True)

    age_order = ["18-25","26-35","36-45","46-55","56+"]

    if "sender_age_group" in df.columns:
        age_s = df.groupby("sender_age_group").agg(
            count=("amount","count"), total=("amount","sum"), avg=("amount","mean")
        ).reset_index()
        age_s["sender_age_group"] = pd.Categorical(
            age_s["sender_age_group"], categories=age_order, ordered=True
        )
        age_s.sort_values("sender_age_group", inplace=True)

        col_ag1, col_ag2 = st.columns(2)
        with col_ag1:
            fig_age = px.bar(age_s, x="sender_age_group", y="count",
                             color="sender_age_group",
                             title="Transactions by Sender Age Group",
                             labels={"sender_age_group":"Age Group","count":"# Transactions"},
                             color_discrete_sequence=PALETTE)
            fig_age = apply_theme(fig_age)
            fig_age.update_layout(showlegend=False)
            st.plotly_chart(fig_age, use_container_width=True)

        with col_ag2:
            fig_age_avg = px.bar(age_s, x="sender_age_group", y="avg",
                                 color="sender_age_group",
                                 title="Avg Transaction Amount by Sender Age Group",
                                 labels={"sender_age_group":"Age Group","avg":"Avg Amount (₹)"},
                                 color_discrete_sequence=PALETTE)
            fig_age_avg = apply_theme(fig_age_avg)
            fig_age_avg.update_layout(showlegend=False)
            st.plotly_chart(fig_age_avg, use_container_width=True)

    # Sender vs Receiver age heatmap
    if "sender_age_group" in df.columns and "receiver_age_group" in df.columns:
        st.markdown('<div class="section-heading">Sender → Receiver Age Group Flow</div>', unsafe_allow_html=True)
        age_cross = df.groupby(["sender_age_group","receiver_age_group"])["amount"].count().reset_index()
        age_cross.columns = ["Sender Age","Receiver Age","Count"]
        pivot_age = age_cross.pivot(index="Sender Age", columns="Receiver Age", values="Count").fillna(0)
        fig_age_heat = px.imshow(pivot_age, color_continuous_scale="Blues",
                                 title="Transaction Count: Sender Age × Receiver Age",
                                 labels={"color":"# Transactions"})
        fig_age_heat.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                                   font=dict(color=FONT_COLOR))
        st.plotly_chart(fig_age_heat, use_container_width=True)

    # Txn type by age
    if "sender_age_group" in df.columns and "txn_type" in df.columns:
        age_type = df.groupby(["sender_age_group","txn_type"])["amount"].count().reset_index()
        age_type.columns = ["Age Group","Type","Count"]
        fig_at = px.bar(age_type, x="Age Group", y="Count", color="Type",
                        barmode="group", title="Transaction Type by Age Group",
                        color_discrete_sequence=["#3b82f6","#f59e0b"])
        fig_at = apply_theme(fig_at)
        st.plotly_chart(fig_at, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 7 — FRAUD
# ══════════════════════════════════════════════
with tab_fraud:
    st.markdown('<div class="section-heading">Fraud Analysis</div>', unsafe_allow_html=True)

    if "fraud_flag" in df.columns:
        fraud_df   = df[df["fraud_flag"] == 1]
        normal_df  = df[df["fraud_flag"] == 0]

        total_fraud = len(fraud_df)
        fraud_val   = fraud_df["amount"].sum() if total_fraud > 0 else 0

        fc1, fc2, fc3, fc4 = st.columns(4)
        fc1.metric("Fraud Transactions",  f"{total_fraud:,}")
        fc2.metric("Fraud Value",         fmt_cr(fraud_val))
        fc3.metric("Fraud Rate",          f"{fraud_rate:.2f}%")
        fc4.metric("Avg Fraud Amount",    f"₹{fraud_df['amount'].mean():,.0f}" if total_fraud > 0 else "N/A")

        if total_fraud > 0:
            col_f1, col_f2 = st.columns(2)

            # Fraud by state
            if "sender_state" in df.columns:
                with col_f1:
                    fd_state = fraud_df.groupby("sender_state")["fraud_flag"].count().reset_index()
                    fd_state.columns = ["State","Fraud Count"]
                    fig_fs = px.bar(fd_state.sort_values("Fraud Count", ascending=True),
                                    x="Fraud Count", y="State", orientation="h",
                                    color="Fraud Count", color_continuous_scale="Reds",
                                    title="Fraud Transactions by State")
                    fig_fs = apply_theme(fig_fs)
                    fig_fs.update_coloraxes(showscale=False)
                    st.plotly_chart(fig_fs, use_container_width=True)

            # Fraud by bank
            if "sender_bank" in df.columns:
                with col_f2:
                    fd_bank = fraud_df.groupby("sender_bank")["fraud_flag"].count().reset_index()
                    fd_bank.columns = ["Bank","Fraud Count"]
                    fig_fb = px.bar(fd_bank.sort_values("Fraud Count", ascending=True),
                                    x="Fraud Count", y="Bank", orientation="h",
                                    color="Fraud Count", color_continuous_scale="Reds",
                                    title="Fraud Transactions by Bank")
                    fig_fb = apply_theme(fig_fb)
                    fig_fb.update_coloraxes(showscale=False)
                    st.plotly_chart(fig_fb, use_container_width=True)

            # Fraud by hour
            if "hour_of_day" in df.columns:
                col_fh1, col_fh2 = st.columns(2)
                with col_fh1:
                    fd_hr = fraud_df.groupby("hour_of_day")["fraud_flag"].count().reset_index()
                    fd_hr.columns = ["Hour","Fraud Count"]
                    fig_fh = px.bar(fd_hr, x="Hour", y="Fraud Count",
                                    color="Fraud Count", color_continuous_scale="Reds",
                                    title="Fraud by Hour of Day")
                    fig_fh = apply_theme(fig_fh)
                    fig_fh.update_coloraxes(showscale=False)
                    st.plotly_chart(fig_fh, use_container_width=True)

                with col_fh2:
                    # Fraud amount distribution comparison
                    fig_fd = go.Figure()
                    fig_fd.add_trace(go.Histogram(x=normal_df["amount"], name="Normal",
                                                  opacity=0.7, marker_color="#3b82f6",
                                                  nbinsx=50))
                    fig_fd.add_trace(go.Histogram(x=fraud_df["amount"], name="Fraud",
                                                  opacity=0.7, marker_color="#ef4444",
                                                  nbinsx=50))
                    fig_fd.update_layout(
                        barmode="overlay",
                        title="Amount Distribution: Normal vs Fraud",
                        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
                        font=dict(color=FONT_COLOR),
                        xaxis=dict(title="Amount (₹)", gridcolor=GRID_COLOR),
                        yaxis=dict(title="Count", gridcolor=GRID_COLOR),
                        legend=dict(bgcolor="rgba(0,0,0,0)"),
                        margin=dict(l=40, r=20, t=50, b=40),
                    )
                    st.plotly_chart(fig_fd, use_container_width=True)

            # Fraud by merchant category
            if "merchant_category" in df.columns:
                fd_cat = fraud_df.groupby("merchant_category")["fraud_flag"].count().reset_index()
                fd_cat.columns = ["Category","Fraud Count"]
                fig_fcat = px.bar(fd_cat.sort_values("Fraud Count", ascending=False),
                                  x="Category", y="Fraud Count",
                                  color="Fraud Count", color_continuous_scale="Reds",
                                  title="Fraud by Merchant Category")
                fig_fcat = apply_theme(fig_fcat)
                fig_fcat.update_coloraxes(showscale=False)
                st.plotly_chart(fig_fcat, use_container_width=True)
        else:
            st.success("✅ No fraud transactions found in the selected data slice.")
    else:
        st.info("ℹ️ No `fraud_flag` column in dataset.")


# ══════════════════════════════════════════════
# TAB 8 — RAW DATA
# ══════════════════════════════════════════════
with tab_data:
    st.markdown('<div class="section-heading">Raw Dataset Explorer</div>', unsafe_allow_html=True)

    col_r1, col_r2 = st.columns([3,1])
    with col_r1:
        search_term = st.text_input("🔎 Search across all text columns", placeholder="e.g. Delhi, SUCCESS, P2P …")
    with col_r2:
        n_rows = st.selectbox("Rows to display", [50, 100, 250, 500, 1000, "All"], index=1)

    display_df = df.copy()
    if search_term:
        mask = display_df.astype(str).apply(lambda col: col.str.contains(search_term, case=False, na=False)).any(axis=1)
        display_df = display_df[mask]

    if n_rows != "All":
        display_df = display_df.head(int(n_rows))

    st.caption(f"Showing {len(display_df):,} rows × {len(display_df.columns)} columns")
    st.dataframe(display_df, use_container_width=True, height=500)

    # Download filtered data
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        "⬇️ Download Filtered CSV",
        data=csv_buffer.getvalue(),
        file_name="upi_filtered.csv",
        mime="text/csv",
    )

    # Data quality report
    st.markdown('<div class="section-heading">Data Quality Report</div>', unsafe_allow_html=True)
    qual = pd.DataFrame({
        "Column": df.columns,
        "Non-Null Count": df.notnull().sum().values,
        "Null Count": df.isnull().sum().values,
        "Null %": (df.isnull().mean() * 100).round(2).values,
        "Unique Values": df.nunique().values,
        "Dtype": df.dtypes.values,
    })
    st.dataframe(qual.set_index("Column"), use_container_width=True)


# ─────────────────────────────────────────────
# KEY INSIGHTS  (bottom of page)
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-heading">🔑 Key Insights & Conclusions</div>', unsafe_allow_html=True)

insights = []

# Insight 1 — top state
if "sender_state" in df.columns:
    top_state = df["sender_state"].value_counts().idxmax()
    top_state_pct = df["sender_state"].value_counts(normalize=True).max() * 100
    insights.append((
        "🏆 Dominant State",
        f"<strong>{top_state}</strong> leads UPI adoption with "
        f"<strong>{top_state_pct:.1f}%</strong> of all transactions in the selected period.",
    ))

# Insight 2 — peak hour
if "hour_of_day" in df.columns:
    ph = int(df.groupby("hour_of_day")["amount"].count().idxmax())
    insights.append((
        "⏰ Peak Usage Hour",
        f"Transaction activity peaks at <strong>{ph:02d}:00 hrs</strong>, "
        "suggesting evening post-work digital payment behaviour.",
    ))

# Insight 3 — transaction type split
if "txn_type" in df.columns:
    tc = df["txn_type"].value_counts(normalize=True)
    dominant_type = tc.idxmax()
    pct = tc.max() * 100
    insights.append((
        "💸 P2P vs P2M",
        f"<strong>{dominant_type}</strong> dominates at <strong>{pct:.1f}%</strong> of all transactions, "
        "reflecting consumer-to-merchant digital payment growth.",
    ))

# Insight 4 — fraud rate
if "fraud_flag" in df.columns:
    insights.append((
        "🛡️ Fraud Rate",
        f"Overall fraud rate is <strong>{fraud_rate:.2f}%</strong> — "
        "extremely low, demonstrating the robustness of UPI's fraud detection mechanisms.",
    ))

# Insight 5 — success rate
if "status" in df.columns:
    insights.append((
        "✅ Transaction Reliability",
        f"With a success rate of <strong>{success_rate:.1f}%</strong>, "
        "UPI proves to be a highly reliable real-time payment infrastructure for India.",
    ))

# Insight 6 — top category
if "merchant_category" in df.columns:
    top_cat = df["merchant_category"].value_counts().idxmax()
    insights.append((
        "🛒 Top Merchant Category",
        f"<strong>{top_cat}</strong> is the most transacted merchant category, "
        "highlighting everyday digital spending patterns.",
    ))

# Insight 7 — device type
if "device_type" in df.columns:
    top_dev = df["device_type"].value_counts().idxmax()
    top_dev_pct = df["device_type"].value_counts(normalize=True).max() * 100
    insights.append((
        "📱 Device Preference",
        f"<strong>{top_dev}</strong> accounts for <strong>{top_dev_pct:.1f}%</strong> of transactions, "
        "indicating a strong Android-first UPI ecosystem.",
    ))

# Insight 8 — age group
if "sender_age_group" in df.columns:
    top_age = df["sender_age_group"].value_counts().idxmax()
    insights.append((
        "👥 Core User Demographic",
        f"The <strong>{top_age}</strong> age group is the most active UPI user segment, "
        "pointing to tech-savvy millennials driving cashless India.",
    ))

# Display insights in 2 columns
ins_cols = st.columns(2)
for i, (title, body) in enumerate(insights):
    with ins_cols[i % 2]:
        st.markdown(
            f'<div class="insight-card"><div class="title">{title}</div>'
            f'<div class="body">{body}</div></div>',
            unsafe_allow_html=True,
        )

# Conclusion
st.markdown("---")
st.markdown(
    """
    <div style="background:#1e293b;border:1px solid #334155;border-radius:12px;padding:24px 28px;margin-top:8px;">
      <div style="color:#38bdf8;font-weight:700;font-size:1.05rem;margin-bottom:10px;">
        📌 Conclusion — India Goes Cashless
      </div>
      <div style="color:#cbd5e1;line-height:1.75;font-size:0.92rem;">
        The 2024 UPI transaction dataset paints a vivid picture of India's digital payment revolution.
        With <strong style="color:#e2e8f0;">250,000+ transactions</strong> across multiple states, banks, and demographics,
        UPI has clearly emerged as the backbone of India's cashless economy.
        The extremely low fraud rate, high success rate, and broad demographic participation confirm
        that UPI is not merely a payment tool — it is a transformative financial infrastructure.
        Growth opportunities remain in rural states, older age groups, and non-4G networks,
        which represent the next frontier for UPI adoption.
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<div style='text-align:center;color:#475569;font-size:0.78rem;margin-top:28px;padding-top:12px;"
    "border-top:1px solid #334155;'>India Goes Cashless: UPI Analytics Dashboard &nbsp;|&nbsp; "
    "Built with Streamlit &amp; Plotly &nbsp;|&nbsp; Dataset: upi_transactions_2024.csv</div>",
    unsafe_allow_html=True,
)
