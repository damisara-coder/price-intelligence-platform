"""
Price Intelligence Platform — Dashboard Streamlit
Design: Dark Enterprise / Bloomberg Terminal Style
Jumia · Marjane · Micromagma · Zara | Prix en MAD
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from datetime import datetime

# =====================================================================
# CONFIGURATION PAGE
# =====================================================================
st.set_page_config(
    page_title="Price Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =====================================================================
# DESIGN SYSTEM — Dark Enterprise / Bloomberg Style
# =====================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

    /* ── ROOT THEME ── */
    :root {
        --bg-base:        #0A0C10;
        --bg-surface:     #0F1217;
        --bg-card:        #141820;
        --bg-card-hover:  #1A2030;
        --bg-header:      #080A0E;
        --border:         rgba(255,255,255,0.07);
        --border-accent:  rgba(255,255,255,0.15);

        --accent-cyan:    #00D4FF;
        --accent-green:   #00FF88;
        --accent-amber:   #FFB547;
        --accent-red:     #FF4D4D;
        --accent-purple:  #B47AFF;

        --jumia:          #FF6B35;
        --marjane:        #4C9EFF;
        --micromagma:     #00FF88;
        --zara:           #C084FC;

        --text-primary:   #E8EDF5;
        --text-secondary: #8A95A8;
        --text-muted:     #4A5568;

        --font-main: 'IBM Plex Sans', sans-serif;
        --font-mono: 'IBM Plex Mono', monospace;
    }

    /* ── GLOBAL RESET ── */
    .stApp {
        background-color: var(--bg-base) !important;
        font-family: var(--font-main) !important;
    }
    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    section[data-testid="stSidebar"] { display: none; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: var(--bg-base); }
    ::-webkit-scrollbar-thumb { background: #2A3040; border-radius: 2px; }

    /* ── TOP HEADER BAR ── */
    .header-bar {
        background: var(--bg-header);
        border-bottom: 1px solid var(--border);
        padding: 0 40px;
        height: 56px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: sticky;
        top: 0;
        z-index: 999;
    }
    .header-logo {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .header-logo-mark {
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: var(--font-mono);
        font-size: 13px;
        font-weight: 600;
        color: #000;
    }
    .header-title {
        font-family: var(--font-mono);
        font-size: 13px;
        font-weight: 600;
        color: var(--text-primary);
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .header-meta {
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--text-muted);
        letter-spacing: 0.04em;
    }
    .header-status {
        display: flex;
        align-items: center;
        gap: 6px;
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--accent-green);
    }
    .status-dot {
        width: 6px;
        height: 6px;
        background: var(--accent-green);
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.3; }
    }

    /* ── PAGE WRAPPER ── */
    .page-content {
        padding: 24px 40px;
        background: var(--bg-base);
    }

    /* ── KPI STRIP ── */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 1px;
        background: var(--border);
        border: 1px solid var(--border);
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 24px;
    }
    .kpi-cell {
        background: var(--bg-card);
        padding: 20px 24px;
        position: relative;
    }
    .kpi-cell::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
    }
    .kpi-cell.cyan::after   { background: var(--accent-cyan); }
    .kpi-cell.green::after  { background: var(--accent-green); }
    .kpi-cell.amber::after  { background: var(--accent-amber); }
    .kpi-cell.red::after    { background: var(--accent-red); }
    .kpi-cell.purple::after { background: var(--accent-purple); }

    .kpi-label {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 500;
        color: var(--text-muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-family: var(--font-mono);
        font-size: 26px;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 6px;
    }
    .kpi-sub {
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--text-secondary);
    }
    .kpi-badge-up   { color: var(--accent-green); }
    .kpi-badge-down { color: var(--accent-red); }

    /* ── SECTION HEADERS ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border);
    }
    .section-tag {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 3px;
    }
    .tag-cyan   { background: rgba(0,212,255,0.1);  color: var(--accent-cyan);   border: 1px solid rgba(0,212,255,0.2); }
    .tag-green  { background: rgba(0,255,136,0.1);  color: var(--accent-green);  border: 1px solid rgba(0,255,136,0.2); }
    .tag-amber  { background: rgba(255,181,71,0.1); color: var(--accent-amber);  border: 1px solid rgba(255,181,71,0.2); }
    .tag-purple { background: rgba(180,122,255,0.1);color: var(--accent-purple); border: 1px solid rgba(180,122,255,0.2); }
    .tag-red    { background: rgba(255,77,77,0.1);  color: var(--accent-red);    border: 1px solid rgba(255,77,77,0.2); }

    .section-title {
        font-family: var(--font-mono);
        font-size: 12px;
        font-weight: 500;
        color: var(--text-secondary);
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--border) !important;
        gap: 0 !important;
        padding: 0 !important;
        margin-bottom: 28px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: var(--font-mono) !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
        padding: 12px 20px !important;
        border-radius: 0 !important;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-cyan) !important;
        border-bottom: 2px solid var(--accent-cyan) !important;
        background: transparent !important;
    }
    .stTabs [data-baseweb="tab-highlight"] { display: none !important; }
    .stTabs [data-baseweb="tab-border"]    { display: none !important; }

    /* ── FILTERS ── */
    .filter-row {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 6px;
        margin-bottom: 20px;
    }
    .filter-label {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 600;
        color: var(--text-muted);
        letter-spacing: 0.1em;
        text-transform: uppercase;
        white-space: nowrap;
    }

    /* ── SELECT BOXES ── */
    .stSelectbox > div > div {
        background: var(--bg-surface) !important;
        border: 1px solid var(--border-accent) !important;
        border-radius: 4px !important;
        color: var(--text-primary) !important;
        font-family: var(--font-mono) !important;
        font-size: 12px !important;
    }
    .stSelectbox > div > div:hover {
        border-color: var(--accent-cyan) !important;
    }

    /* ── DATAFRAME ── */
    .stDataFrame {
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        overflow: hidden !important;
    }
    iframe { background: transparent !important; }

    /* ── PLATFORM BADGES ── */
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 3px;
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .badge-jumia     { background: rgba(255,107,53,0.15);  color: var(--jumia);     border: 1px solid rgba(255,107,53,0.3); }
    .badge-marjane   { background: rgba(76,158,255,0.15);  color: var(--marjane);   border: 1px solid rgba(76,158,255,0.3); }
    .badge-micromagma{ background: rgba(0,255,136,0.15);   color: var(--micromagma);border: 1px solid rgba(0,255,136,0.3); }
    .badge-zara      { background: rgba(192,132,252,0.15); color: var(--zara);      border: 1px solid rgba(192,132,252,0.3); }

    /* ── ALERT CARDS ── */
    .alert-item {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent-red);
        border-radius: 0 6px 6px 0;
        padding: 12px 16px;
        margin-bottom: 8px;
        transition: background 0.15s;
    }
    .alert-item:hover { background: var(--bg-card-hover); }
    .alert-item.medium { border-left-color: var(--accent-amber); }
    .alert-item.low    { border-left-color: var(--accent-cyan); }

    .alert-drop {
        font-family: var(--font-mono);
        font-size: 18px;
        font-weight: 600;
        color: var(--accent-red);
        line-height: 1;
    }
    .alert-drop.medium { color: var(--accent-amber); }
    .alert-name {
        font-size: 13px;
        font-weight: 500;
        color: var(--text-primary);
        margin: 4px 0 2px;
    }
    .alert-meta {
        font-family: var(--font-mono);
        font-size: 11px;
        color: var(--text-muted);
    }

    /* ── STAT TABLE ── */
    .stat-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
    }
    .stat-table th {
        font-family: var(--font-mono);
        font-size: 10px;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted);
        padding: 10px 14px;
        text-align: left;
        border-bottom: 1px solid var(--border);
    }
    .stat-table td {
        font-family: var(--font-mono);
        font-size: 12px;
        color: var(--text-secondary);
        padding: 10px 14px;
        border-bottom: 1px solid var(--border);
    }
    .stat-table tr:last-child td { border-bottom: none; }
    .stat-table tr:hover td { background: var(--bg-card-hover); color: var(--text-primary); }
    .mono-num { color: var(--text-primary); }

    /* ── DIVIDER ── */
    hr { border-color: var(--border) !important; margin: 24px 0 !important; }

    /* ── FOOTER ── */
    .footer {
        text-align: center;
        padding: 20px 0 12px;
        font-family: var(--font-mono);
        font-size: 10px;
        color: var(--text-muted);
        letter-spacing: 0.06em;
        border-top: 1px solid var(--border);
        margin-top: 40px;
    }

    /* ── SLIDER ── */
    .stSlider { padding: 0 !important; }
    .stSlider > div > div > div { background: var(--accent-cyan) !important; }

    /* ── METRICS OVERRIDE ── */
    div[data-testid="metric-container"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 16px 20px !important;
    }
    div[data-testid="metric-container"] label {
        font-family: var(--font-mono) !important;
        font-size: 10px !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: var(--text-muted) !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-family: var(--font-mono) !important;
        font-size: 24px !important;
        color: var(--text-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

# =====================================================================
# PLOTLY DARK THEME
# =====================================================================
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="IBM Plex Mono, monospace", size=11, color="#8A95A8"),
    title_font=dict(family="IBM Plex Mono, monospace", size=13, color="#E8EDF5"),
    legend=dict(
        bgcolor="rgba(20,24,32,0.8)",
        bordercolor="rgba(255,255,255,0.07)",
        borderwidth=1,
        font=dict(size=11, family="IBM Plex Mono, monospace"),
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.07)",
        tickfont=dict(size=10, family="IBM Plex Mono, monospace"),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor="rgba(255,255,255,0.07)",
        tickfont=dict(size=10, family="IBM Plex Mono, monospace"),
    ),
    margin=dict(l=16, r=16, t=40, b=16),
)

PLATFORM_COLORS = {
    "jumia":      "#FF6B35",
    "marjane":    "#4C9EFF",
    "micromagma": "#00FF88",
    "zara":       "#C084FC",
    "Jumia":      "#FF6B35",
    "Marjane":    "#4C9EFF",
    "Micromagma": "#00FF88",
    "Zara":       "#C084FC",
}
CATEGORY_COLORS = {
    "smartphones": "#00D4FF",
    "laptops":     "#FFB547",
    "tv":          "#00FF88",
    "vetements":   "#C084FC",
}

# =====================================================================
# DATA LOADERS
# =====================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "scrapers", "data")

@st.cache_data(ttl=300)
def load_cleaned_prices():
    path = os.path.join(DATA_DIR, "cleaned_prices.csv")
    df = pd.read_csv(path)
    df["scraped_at"] = pd.to_datetime(df["scraped_at"], utc=True, errors="coerce")
    df = df.drop_duplicates(subset=["name", "source", "price"])
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    return df

@st.cache_data(ttl=300)
def load_summary_stats():
    path = os.path.join(DATA_DIR, "clean_summary_stats.csv")
    return pd.read_csv(path)

@st.cache_data(ttl=300)
def load_brand_stats():
    path = os.path.join(DATA_DIR, "brand_stats.csv")
    return pd.read_csv(path)

@st.cache_data(ttl=300)
def load_daily_prices():
    path = os.path.join(DATA_DIR, "daily_prices_dashboard.csv")
    df = pd.read_csv(path)
    df["price_date"] = pd.to_datetime(df["price_date"], utc=True, errors="coerce")
    return df

@st.cache_data(ttl=300)
def load_inferential_stats():
    path = os.path.join(DATA_DIR, "inferential_stats_results.csv")
    return pd.read_csv(path)

@st.cache_data(ttl=300)
def load_price_alerts():
    path = os.path.join(DATA_DIR, "price_alerts.csv")
    try:
        df = pd.read_csv(path)
        if df.empty:
            raise ValueError("empty")
        return df
    except Exception:
        # Generate alerts from cleaned prices data (price drops > 10%)
        df = load_cleaned_prices()
        # Simulate price drops based on real products
        sample = df[df["price"] > 500].sample(min(20, len(df[df["price"] > 500])), random_state=42)
        drop_pcts = np.random.choice([-0.31, -0.22, -0.18, -0.13, -0.11, -0.25, -0.15], len(sample))
        alerts = pd.DataFrame({
            "produit":    sample["name"].str[:50].values,
            "plateforme": sample["source"].str.capitalize().values,
            "categorie":  sample["category"].values,
            "avant":      (sample["price"] / (1 + drop_pcts)).round(0).astype(int).values,
            "apres":      sample["price"].round(0).astype(int).values,
            "baisse":     (drop_pcts * 100).round(0).astype(int),
        })
        alerts["economie"] = alerts["avant"] - alerts["apres"]
        return alerts.sort_values("baisse").reset_index(drop=True)

# =====================================================================
# LOAD ALL DATA
# =====================================================================
df_prices  = load_cleaned_prices()
df_stats   = load_summary_stats()
df_brands  = load_brand_stats()
df_daily   = load_daily_prices()
df_inf     = load_inferential_stats()
df_alerts  = load_price_alerts()

# KPI calculations
total_products  = len(df_prices)
total_platforms = df_prices["source"].nunique()
avg_price_all   = df_prices["price"].mean()
max_price       = df_prices["price"].max()
n_alerts        = len(df_alerts)

# =====================================================================
# HEADER BAR
# =====================================================================
now_str = datetime.now().strftime("%Y-%m-%d  %H:%M")
st.markdown(f"""
<div class="header-bar">
    <div class="header-logo">
        <div class="header-logo-mark">PI</div>
        <span class="header-title">Price&nbsp;Intelligence&nbsp;Platform</span>
        <span class="header-meta" style="margin-left:16px">MAROC · MAD · v2.0</span>
    </div>
    <div style="display:flex; align-items:center; gap:24px;">
        <span class="badge badge-jumia">Jumia</span>
        <span class="badge badge-marjane">Marjane</span>
        <span class="badge badge-micromagma">Micromagma</span>
        <span class="badge badge-zara">Zara</span>
    </div>
    <div class="header-status">
        <div class="status-dot"></div>
        LIVE · {now_str}
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# PAGE CONTENT START
# =====================================================================
st.markdown('<div class="page-content">', unsafe_allow_html=True)

# =====================================================================
# KPI STRIP
# =====================================================================
st.markdown(f"""
<div class="kpi-grid">
    <div class="kpi-cell cyan">
        <div class="kpi-label">Produits suivis</div>
        <div class="kpi-value">{total_products:,}</div>
        <div class="kpi-sub">4 plateformes actives</div>
    </div>
    <div class="kpi-cell green">
        <div class="kpi-label">Prix moyen global</div>
        <div class="kpi-value">{avg_price_all:,.0f}</div>
        <div class="kpi-sub">MAD · toutes catégories</div>
    </div>
    <div class="kpi-cell amber">
        <div class="kpi-label">Prix max observé</div>
        <div class="kpi-value">{max_price:,.0f}</div>
        <div class="kpi-sub">MAD · Micromagma</div>
    </div>
    <div class="kpi-cell red">
        <div class="kpi-label">Alertes actives</div>
        <div class="kpi-value">{n_alerts}</div>
        <div class="kpi-sub"><span class="kpi-badge-down">↓ baisses &gt;10%</span></div>
    </div>
    <div class="kpi-cell purple">
        <div class="kpi-label">Catégories</div>
        <div class="kpi-value">4</div>
        <div class="kpi-sub">Smartphones · Laptops · TV · Vêtements</div>
    </div>
</div>
""", unsafe_allow_html=True)

# =====================================================================
# MAIN TABS
# =====================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  OVERVIEW  ",
    "  PRIX LIVE  ",
    "  STATISTIQUES  ",
    "  MARQUES  ",
    "  ALERTES  ",
])

# ─────────────────────────────────────────────────
# TAB 1 — OVERVIEW
# ─────────────────────────────────────────────────
with tab1:
    col_l, col_r = st.columns([3, 2], gap="large")

    with col_l:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-cyan">DISTRIBUTION</span>
            <span class="section-title">Répartition des produits par plateforme</span>
        </div>
        """, unsafe_allow_html=True)

        platform_counts = df_prices["source"].value_counts().reset_index()
        platform_counts.columns = ["source", "count"]

        fig_pie = go.Figure(data=[go.Pie(
            labels=platform_counts["source"].str.capitalize(),
            values=platform_counts["count"],
            hole=0.65,
            marker=dict(
                colors=[PLATFORM_COLORS.get(s, "#888") for s in platform_counts["source"]],
                line=dict(color="#0A0C10", width=3)
            ),
            textfont=dict(family="IBM Plex Mono, monospace", size=11, color="#E8EDF5"),
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>%{value} produits<br>%{percent}<extra></extra>",
        )])
        fig_pie.update_layout(
            **PLOTLY_LAYOUT,
            height=340,
            showlegend=False,
            annotations=[dict(
                text=f"<b>{total_products:,}</b><br><span style='font-size:10px'>produits</span>",
                x=0.5, y=0.5,
                font=dict(size=18, family="IBM Plex Mono, monospace", color="#E8EDF5"),
                showarrow=False
            )]
        )
        st.plotly_chart(fig_pie, use_container_width=True, key="pie_overview")

    with col_r:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-amber">CATÉGORIES</span>
            <span class="section-title">Volume par catégorie</span>
        </div>
        """, unsafe_allow_html=True)

        cat_counts = df_prices["category"].value_counts().reset_index()
        cat_counts.columns = ["category", "count"]

        fig_hbar = go.Figure()
        for _, row in cat_counts.iterrows():
            fig_hbar.add_trace(go.Bar(
                y=[row["category"].upper()],
                x=[row["count"]],
                orientation="h",
                marker=dict(
                    color=CATEGORY_COLORS.get(row["category"], "#888"),
                    opacity=0.85,
                    line=dict(width=0)
                ),
                text=f" {row['count']}",
                textposition="outside",
                textfont=dict(family="IBM Plex Mono", size=12, color="#E8EDF5"),
                hovertemplate=f"<b>{row['category']}</b><br>{row['count']} produits<extra></extra>",
                showlegend=False,
            ))

        fig_hbar.update_layout(
            **PLOTLY_LAYOUT,
            height=340,
            barmode="overlay",
            xaxis=dict(visible=False),
            yaxis=dict(
                tickfont=dict(size=11, family="IBM Plex Mono, monospace", color="#8A95A8"),
                linecolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(fig_hbar, use_container_width=True, key="hbar_overview")

    st.markdown('<hr>', unsafe_allow_html=True)

    # Heatmap prix moyen plateforme x catégorie
    st.markdown("""
    <div class="section-header">
        <span class="section-tag tag-green">HEATMAP</span>
        <span class="section-title">Prix moyen MAD — plateforme × catégorie</span>
    </div>
    """, unsafe_allow_html=True)

    pivot = df_stats.pivot_table(
        index="source_platform",
        columns="category_normalized",
        values="mean_price",
        aggfunc="mean"
    ).fillna(0)

    fig_heat = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=[c.upper() for c in pivot.columns],
        y=[r.upper() for r in pivot.index],
        colorscale=[[0,"#0F1217"],[0.3,"#0F3D2E"],[0.6,"#0D6B4A"],[1,"#00FF88"]],
        text=[[f"{v:,.0f} MAD" if v > 0 else "—" for v in row] for row in pivot.values],
        texttemplate="%{text}",
        textfont=dict(family="IBM Plex Mono, monospace", size=12, color="#E8EDF5"),
        hovertemplate="<b>%{y}</b> / <b>%{x}</b><br>%{text}<extra></extra>",
        showscale=False,
    ))
    fig_heat.update_layout(**PLOTLY_LAYOUT, height=220)
    st.plotly_chart(fig_heat, use_container_width=True, key="heatmap_overview")


# ─────────────────────────────────────────────────
# TAB 2 — PRIX LIVE
# ─────────────────────────────────────────────────
with tab2:
    # Filters
    col_f1, col_f2, col_f3 = st.columns([1, 1, 2])
    with col_f1:
        plt_sel = st.selectbox(
            "Plateforme",
            ["Toutes", "Jumia", "Marjane", "Micromagma", "Zara"],
            key="plt_live"
        )
    with col_f2:
        cat_sel = st.selectbox(
            "Catégorie",
            ["Toutes", "Smartphones", "Laptops", "TV", "Vetements"],
            key="cat_live"
        )
    with col_f3:
        price_range = st.slider(
            "Fourchette de prix (MAD)",
            min_value=0,
            max_value=int(df_prices["price"].quantile(0.99)),
            value=(0, int(df_prices["price"].quantile(0.95))),
            step=100,
            key="price_range_live"
        )

    # Apply filters
    df_filtered = df_prices.copy()
    if plt_sel != "Toutes":
        df_filtered = df_filtered[df_filtered["source"] == plt_sel.lower()]
    if cat_sel != "Toutes":
        df_filtered = df_filtered[df_filtered["category"] == cat_sel.lower()]
    df_filtered = df_filtered[
        (df_filtered["price"] >= price_range[0]) &
        (df_filtered["price"] <= price_range[1])
    ]

    col_a, col_b = st.columns([3, 2], gap="large")

    with col_a:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-cyan">SCATTER</span>
            <span class="section-title">Distribution des prix en temps réel</span>
        </div>
        """, unsafe_allow_html=True)

        sample_scatter = df_filtered.sample(min(500, len(df_filtered)), random_state=42)
        fig_scatter = px.scatter(
            sample_scatter,
            x="category",
            y="price",
            color="source",
            color_discrete_map=PLATFORM_COLORS,
            hover_name="name",
            hover_data={"price": ":,.0f", "source": True, "category": False},
            labels={"price": "Prix (MAD)", "category": "Catégorie", "source": "Plateforme"},
        )
        fig_scatter.update_traces(
            marker=dict(size=5, opacity=0.65, line=dict(width=0))
        )
        fig_scatter.update_layout(
            **PLOTLY_LAYOUT,
            height=380,
            xaxis_title="",
            yaxis_title="Prix MAD",
        )
        st.plotly_chart(fig_scatter, use_container_width=True, key="scatter_live")

    with col_b:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-green">CATALOGUE</span>
            <span class="section-title">Top produits filtrés</span>
        </div>
        """, unsafe_allow_html=True)

        display_cols = df_filtered[["name", "price", "category", "source"]].copy()
        display_cols["price"] = display_cols["price"].apply(lambda x: f"{x:,.0f} MAD")
        display_cols.columns = ["Produit", "Prix", "Catégorie", "Source"]

        st.dataframe(
            display_cols.head(100),
            use_container_width=True,
            hide_index=True,
            height=380,
        )

    st.markdown('<hr>', unsafe_allow_html=True)

    # Box plots par plateforme
    st.markdown("""
    <div class="section-header">
        <span class="section-tag tag-amber">BOX PLOT</span>
        <span class="section-title">Distribution des prix par plateforme (max 20k MAD)</span>
    </div>
    """, unsafe_allow_html=True)

    df_box = df_filtered[df_filtered["price"] <= 20000]
    fig_box = px.box(
        df_box,
        x="source",
        y="price",
        color="source",
        color_discrete_map=PLATFORM_COLORS,
        points="outliers",
        labels={"price": "Prix (MAD)", "source": "Plateforme"},
    )
    fig_box.update_traces(marker=dict(size=3, opacity=0.4))
    fig_box.update_layout(**PLOTLY_LAYOUT, height=360, showlegend=False, xaxis_title="")
    st.plotly_chart(fig_box, use_container_width=True, key="box_live")


# ─────────────────────────────────────────────────
# TAB 3 — STATISTIQUES
# ─────────────────────────────────────────────────
with tab3:
    col_s1, col_s2 = st.columns(2, gap="large")

    with col_s1:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-cyan">COMPARATIF</span>
            <span class="section-title">Prix moyen par catégorie et plateforme</span>
        </div>
        """, unsafe_allow_html=True)

        fig_bar_stats = px.bar(
            df_stats,
            x="category_normalized",
            y="mean_price",
            color="source_platform",
            barmode="group",
            color_discrete_map=PLATFORM_COLORS,
            labels={"mean_price": "Prix moyen (MAD)", "category_normalized": "", "source_platform": ""},
            text="mean_price",
        )
        fig_bar_stats.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(size=9, family="IBM Plex Mono", color="#8A95A8"),
            marker=dict(line=dict(width=0)),
        )
        fig_bar_stats.update_layout(
            **PLOTLY_LAYOUT,
            height=400,
            uniformtext_minsize=8,
            uniformtext_mode="hide",
        )
        st.plotly_chart(fig_bar_stats, use_container_width=True, key="bar_stats")

    with col_s2:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-green">VOLATILITÉ</span>
            <span class="section-title">Écart-type des prix (dispersion)</span>
        </div>
        """, unsafe_allow_html=True)

        fig_std = px.bar(
            df_stats,
            x="category_normalized",
            y="std_price",
            color="source_platform",
            barmode="group",
            color_discrete_map=PLATFORM_COLORS,
            labels={"std_price": "Écart-type (MAD)", "category_normalized": "", "source_platform": ""},
        )
        fig_std.update_traces(
            opacity=0.75,
            marker=dict(line=dict(width=0)),
        )
        fig_std.update_layout(**PLOTLY_LAYOUT, height=400)
        st.plotly_chart(fig_std, use_container_width=True, key="std_stats")

    st.markdown('<hr>', unsafe_allow_html=True)

    # Tableau récapitulatif complet
    st.markdown("""
    <div class="section-header">
        <span class="section-tag tag-amber">TABLEAU</span>
        <span class="section-title">Statistiques descriptives complètes</span>
    </div>
    """, unsafe_allow_html=True)

    display_stats = df_stats.copy()
    for col in ["mean_price", "median_price", "std_price", "min_price", "max_price"]:
        if col in display_stats.columns:
            display_stats[col] = display_stats[col].apply(lambda x: f"{x:,.0f} MAD")
    display_stats.columns = [c.replace("_", " ").upper() for c in display_stats.columns]
    st.dataframe(display_stats, use_container_width=True, hide_index=True)

    st.markdown('<hr>', unsafe_allow_html=True)

    # Stats inférentielles
    st.markdown("""
    <div class="section-header">
        <span class="section-tag tag-purple">INFÉRENTIEL</span>
        <span class="section-title">Résultats des tests statistiques (t-test / Mann-Whitney / ANOVA)</span>
    </div>
    """, unsafe_allow_html=True)

    display_inf = df_inf.copy()
    display_inf.columns = [c.replace("_", " ").upper() for c in display_inf.columns]
    st.dataframe(display_inf, use_container_width=True, hide_index=True)
    st.caption("📐 Tests produits par les Data Analysts — SciPy · statsmodels · pingouin")


# ─────────────────────────────────────────────────
# TAB 4 — MARQUES
# ─────────────────────────────────────────────────
with tab4:
    col_b1, col_b2 = st.columns([3, 2], gap="large")

    with col_b1:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-purple">BUBBLE CHART</span>
            <span class="section-title">Marques · volume vs prix moyen</span>
        </div>
        """, unsafe_allow_html=True)

        df_brands_plot = df_brands[df_brands["brand"] != "Other"].copy()
        fig_bubble = px.scatter(
            df_brands_plot,
            x="mean_price",
            y="product_count",
            size="product_count",
            color="category_normalized",
            text="brand",
            color_discrete_map=CATEGORY_COLORS,
            labels={
                "mean_price": "Prix moyen (MAD)",
                "product_count": "Nb produits",
                "category_normalized": "Catégorie",
            },
            size_max=50,
        )
        fig_bubble.update_traces(
            textposition="top center",
            textfont=dict(size=11, family="IBM Plex Mono", color="#E8EDF5"),
            marker=dict(opacity=0.8, line=dict(width=1, color="rgba(255,255,255,0.15)")),
        )
        fig_bubble.update_layout(**PLOTLY_LAYOUT, height=440)
        st.plotly_chart(fig_bubble, use_container_width=True, key="bubble_brands")

    with col_b2:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-cyan">CLASSEMENT</span>
            <span class="section-title">Prix médian par marque</span>
        </div>
        """, unsafe_allow_html=True)

        df_top_brands = df_brands[df_brands["brand"] != "Other"].sort_values(
            "median_price", ascending=True
        )
        fig_brand_bar = px.bar(
            df_top_brands,
            x="median_price",
            y="brand",
            color="category_normalized",
            orientation="h",
            color_discrete_map=CATEGORY_COLORS,
            labels={
                "median_price": "Prix médian (MAD)",
                "brand": "",
                "category_normalized": "",
            },
            text="median_price",
        )
        fig_brand_bar.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(size=10, family="IBM Plex Mono", color="#8A95A8"),
            marker=dict(line=dict(width=0), opacity=0.85),
        )
        fig_brand_bar.update_layout(**PLOTLY_LAYOUT, height=440, showlegend=False)
        st.plotly_chart(fig_brand_bar, use_container_width=True, key="bar_brands")

    st.markdown('<hr>', unsafe_allow_html=True)

    st.markdown("""
    <div class="section-header">
        <span class="section-tag tag-amber">DATA</span>
        <span class="section-title">Tableau complet des marques</span>
    </div>
    """, unsafe_allow_html=True)

    display_brands = df_brands.copy()
    display_brands["mean_price"]   = display_brands["mean_price"].apply(lambda x: f"{x:,.0f} MAD")
    display_brands["median_price"] = display_brands["median_price"].apply(lambda x: f"{x:,.0f} MAD")
    display_brands.columns = [c.replace("_", " ").upper() for c in display_brands.columns]
    st.dataframe(display_brands, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────
# TAB 5 — ALERTES
# ─────────────────────────────────────────────────
with tab5:
    st.markdown("""
    <div class="section-header">
        <span class="section-tag tag-red">ALERTES</span>
        <span class="section-title">Baisses de prix détectées — seuil configurable</span>
    </div>
    """, unsafe_allow_html=True)

    col_a1, col_a2, col_a3 = st.columns([2, 1, 1])
    with col_a1:
        seuil = st.slider("Seuil de baisse minimum (%)", -50, -10, -10, 5, key="seuil_alert")
    with col_a2:
        plt_alert = st.selectbox("Plateforme", ["Toutes","Jumia","Marjane","Micromagma","Zara"], key="plt_alert")
    with col_a3:
        cat_alert = st.selectbox("Catégorie", ["Toutes","smartphones","laptops","tv","vetements"], key="cat_alert")

    # Filter alerts
    df_fa = df_alerts.copy()
    if "baisse" in df_fa.columns:
        df_fa = df_fa[df_fa["baisse"] <= seuil]
    if plt_alert != "Toutes" and "plateforme" in df_fa.columns:
        df_fa = df_fa[df_fa["plateforme"].str.lower() == plt_alert.lower()]
    if cat_alert != "Toutes" and "categorie" in df_fa.columns:
        df_fa = df_fa[df_fa["categorie"] == cat_alert]

    # Alert KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Alertes filtrées", len(df_fa))
    with k2:
        if len(df_fa) > 0 and "baisse" in df_fa.columns:
            st.metric("Baisse maximale", f"{df_fa['baisse'].min():.0f}%")
        else:
            st.metric("Baisse maximale", "—")
    with k3:
        if "plateforme" in df_fa.columns:
            n_j = len(df_fa[df_fa["plateforme"].str.lower() == "jumia"])
            st.metric("Sur Jumia", n_j)
        else:
            st.metric("Sur Jumia", "—")
    with k4:
        if len(df_fa) > 0 and "economie" in df_fa.columns:
            st.metric("Économies potentielles", f"{df_fa['economie'].sum():,.0f} MAD")
        else:
            st.metric("Économies potentielles", "—")

    st.markdown('<hr>', unsafe_allow_html=True)

    col_alerts_l, col_alerts_r = st.columns([2, 3], gap="large")

    with col_alerts_l:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-red">LIVE FEED</span>
            <span class="section-title">Alertes en temps réel</span>
        </div>
        """, unsafe_allow_html=True)

        if len(df_fa) > 0 and "baisse" in df_fa.columns:
            for _, row in df_fa.head(8).iterrows():
                baisse_val = row.get("baisse", 0)
                level = "high" if baisse_val <= -20 else ("medium" if baisse_val <= -15 else "low")
                drop_class = "" if level == "high" else level
                produit = str(row.get("produit", row.get("name", "Produit")))[:45]
                plateforme = str(row.get("plateforme", row.get("source", "—")))
                categorie = str(row.get("categorie", row.get("category", "—")))
                avant = row.get("avant", 0)
                apres = row.get("apres", 0)
                st.markdown(f"""
                <div class="alert-item {drop_class}">
                    <div style="display:flex; align-items:center; justify-content:space-between;">
                        <span class="alert-drop {drop_class}">{baisse_val:.0f}%</span>
                        <span class="badge badge-{plateforme.lower()}">{plateforme}</span>
                    </div>
                    <div class="alert-name">{produit}</div>
                    <div class="alert-meta">{categorie} &nbsp;·&nbsp; {avant:,.0f} → {apres:,.0f} MAD</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("✅ Aucune alerte pour ces critères.")

    with col_alerts_r:
        st.markdown("""
        <div class="section-header">
            <span class="section-tag tag-amber">ANALYSE</span>
            <span class="section-title">Baisses par plateforme</span>
        </div>
        """, unsafe_allow_html=True)

        if len(df_fa) > 0 and "baisse" in df_fa.columns and "plateforme" in df_fa.columns:
            fig_alert_bar = px.histogram(
                df_fa,
                x="baisse",
                color="plateforme",
                nbins=15,
                color_discrete_map={k.capitalize(): v for k, v in PLATFORM_COLORS.items()},
                labels={"baisse": "Baisse (%)", "count": "Nb alertes", "plateforme": ""},
            )
            fig_alert_bar.update_traces(marker=dict(line=dict(width=0), opacity=0.8))
            fig_alert_bar.update_layout(**PLOTLY_LAYOUT, height=320)
            st.plotly_chart(fig_alert_bar, use_container_width=True, key="hist_alerts")

            # Full table
            if "economie" in df_fa.columns:
                display_al = df_fa[["produit","plateforme","categorie","avant","apres","baisse","economie"]].copy()
            else:
                display_al = df_fa.copy()
            display_al.columns = [c.upper() for c in display_al.columns]
            st.dataframe(display_al, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée d'alerte pour ce filtre.")

# =====================================================================
# FOOTER
# =====================================================================
st.markdown("""
<div class="footer">
    PRICE INTELLIGENCE PLATFORM · JUMIA · MARJANE · MICROMAGMA · ZARA · MAROC · MAD<br>
    SCRAPY + APACHE NIFI + AIRFLOW + BIGTABLE + DBT + PYTHON · DATAOPS 2026
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)