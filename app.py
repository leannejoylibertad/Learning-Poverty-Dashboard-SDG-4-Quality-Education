"""
╔══════════════════════════════════════════════════════════════════════╗
║   LEARNING POVERTY DASHBOARD — SDG 4: Quality Education             ║
║   What drives the share of children who cannot read by end          ║
║   of primary school?                                                ║
║                                                                      ║
║   UPDATED LAYOUT:                                                    ║
║   ✓ Combined related graphs into unified dashboard sections          ║
║   ✓ Better screen-space efficiency                                   ║
║   ✓ Cleaner visual hierarchy                                         ║
║   ✓ Reduced scrolling                                                ║
║   ✓ More professional analytics layout                               ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ─────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Learning Poverty | SDG 4",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}

.block-container{
    padding-top:1.5rem;
    padding-bottom:1rem;
}

/* HERO */
.hero {
    background: linear-gradient(135deg,#0a3d2e 0%,#1a6b4a 50%,#2d9e6b 100%);
    border-radius:18px;
    padding:34px 40px 28px;
    margin-bottom:24px;
    color:white;
}

.hero h1{
    font-size:2.3rem;
    font-weight:800;
    margin:0;
    letter-spacing:-0.5px;
}

.hero .sub{
    margin-top:10px;
    opacity:0.9;
    font-size:1rem;
    line-height:1.6;
}

.badges{
    display:flex;
    gap:10px;
    flex-wrap:wrap;
    margin-top:18px;
}

.badge{
    background:rgba(255,255,255,0.16);
    border:1px solid rgba(255,255,255,0.25);
    padding:6px 14px;
    border-radius:999px;
    font-size:0.78rem;
    font-weight:600;
}

/* KPI */
[data-testid="metric-container"]{
    background:white;
    border:1px solid #e5e7eb;
    border-radius:14px;
    padding:12px 16px;
    box-shadow:0 2px 8px rgba(0,0,0,0.04);
}

/* SECTION */
.section-header{
    font-size:0.72rem;
    font-weight:700;
    color:#6b7280;
    letter-spacing:1px;
    text-transform:uppercase;
    border-bottom:2px solid #eef2f7;
    padding-bottom:6px;
    margin-bottom:14px;
    margin-top:4px;
}

/* INSIGHT */
.insight{
    background:#f0fdf4;
    border-left:4px solid #1a6b4a;
    padding:14px 18px;
    border-radius:0 10px 10px 0;
    font-size:0.88rem;
    line-height:1.7;
    color:#1f2937;
}

/* TABS */
.stTabs [data-baseweb="tab-list"]{
    gap:4px;
    background:#f8fafc;
    padding:5px;
    border-radius:12px;
}

.stTabs [data-baseweb="tab"]{
    border-radius:10px;
    padding:10px 18px;
    font-size:0.83rem;
    font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    dd = pd.read_csv("dashboard_data.csv")
    cd = pd.read_csv("cleaned_dataset.csv")
    diag = pd.read_csv("diagnostics_results.csv")

    with open("model_params.json") as f:
        mp = json.load(f)

    full = cd.merge(
        dd[[
            "Country Name",
            "Country Code",
            "Year",
            "predicted_learning_poverty",
            "huber_residuals"
        ]],
        on=["Country Name", "Country Code", "Year"],
        how="left"
    )

    return full, diag, mp

full, diag, mp = load_data()

COEFS = mp["coefficients"]
PVALS = mp["p_values"]
CI = mp["confidence_intervals"]

YEARS = sorted(full["Year"].unique().tolist())
COUNTRIES = sorted(full["Country Name"].unique().tolist())

IND_VARS = [
    "pupil_teacher_ratio",
    "trained_teachers",
    "gov_expenditure",
    "u5_mortality"
]

IND_LABELS = {
    "pupil_teacher_ratio": "Pupil-Teacher Ratio",
    "trained_teachers": "Trained Teachers (%)",
    "gov_expenditure": "Gov. Expenditure (% GDP/cap)",
    "u5_mortality": "Under-5 Mortality"
}

PALETTE = [
    "#1a6b4a",
    "#e63946",
    "#457b9d",
    "#f4a261",
    "#6a4c93"
]

# ─────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────
def lp_color(v):
    if v < 15:
        return "#2a9d8f"
    elif v < 35:
        return "#57cc99"
    elif v < 55:
        return "#e9c46a"
    elif v < 75:
        return "#f4a261"
    return "#e63946"


def predict(ptr, tt, ge, um):
    val = (
        COEFS["const"]
        + COEFS["pupil_teacher_ratio"] * ptr
        + COEFS["trained_teachers"] * tt
        + COEFS["gov_expenditure"] * ge
        + COEFS["u5_mortality"] * um
    )
    return max(0.0, min(100.0, val))


# ─────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>📚 Learning Poverty Dashboard</h1>

    <div class="sub">
        What factors drive the share of children unable to read by the end of primary school?<br>
        Robust regression analysis across 75 countries (2000–2023)
    </div>

    <div class="badges">
        <span class="badge">🌍 75 Countries</span>
        <span class="badge">📅 2000–2023</span>
        <span class="badge">📊 Robust Regression</span>
        <span class="badge">🏦 World Bank Open Data</span>
        <span class="badge">🎯 SDG 4</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown("### ⚙️ Dashboard Controls")

    sel_year = st.slider(
        "📅 Select Year",
        min_value=int(min(YEARS)),
        max_value=int(max(YEARS)),
        value=2015,
        step=1
    )

    sel_countries = st.multiselect(
        "🌍 Compare Countries",
        options=COUNTRIES,
        default=["Niger", "Colombia", "Spain", "Korea, Rep."]
    )

    focus_country = st.selectbox(
        "🔎 Focus Country",
        options=COUNTRIES,
        index=COUNTRIES.index("Colombia") if "Colombia" in COUNTRIES else 0
    )

# ─────────────────────────────────────────────────────────────────────
# KPI ROW
# ─────────────────────────────────────────────────────────────────────
yr_data = full[full["Year"] == sel_year].dropna(
    subset=["learning_poverty"]
)

avg_lp = yr_data["learning_poverty"].mean()
n_cntry = len(yr_data)

worst_r = yr_data.loc[
    yr_data["learning_poverty"].idxmax()
]

best_r = yr_data.loc[
    yr_data["learning_poverty"].idxmin()
]

pct_50 = (yr_data["learning_poverty"] > 50).mean() * 100

k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.metric("🌍 Avg LP", f"{avg_lp:.1f}%")

with k2:
    st.metric("📊 Countries", n_cntry)

with k3:
    st.metric(
        "⚠️ Highest",
        worst_r["Country Name"].split(",")[0],
        f"{worst_r['learning_poverty']:.1f}%"
    )

with k4:
    st.metric(
        "✅ Lowest",
        best_r["Country Name"].split(",")[0],
        f"{best_r['learning_poverty']:.1f}%"
    )

with k5:
    st.metric("📈 Above 50%", f"{pct_50:.0f}%")

st.markdown("---")

# ─────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ Global Overview",
    "📈 Trends & Drivers",
    "📐 Regression Analysis",
    "🧮 Predictor",
    "ℹ️ About"
])

# ═════════════════════════════════════════════════════════════════════
# TAB 1 — GLOBAL OVERVIEW
# ═════════════════════════════════════════════════════════════════════
with tab1:

    st.markdown(
        f'<div class="section-header">Global Learning Poverty Overview — {sel_year}</div>',
        unsafe_allow_html=True
    )

    # ─────────────────────────────────────────────────────────────
    # MAP
    # ─────────────────────────────────────────────────────────────
    fig_map = px.choropleth(
        yr_data,
        locations="Country Code",
        color="learning_poverty",
        hover_name="Country Name",
        hover_data={
            "learning_poverty":":.1f",
            "predicted_learning_poverty":":.1f",
            "Country Code":False
        },
        color_continuous_scale=[
            [0.00, "#2a9d8f"],
            [0.25, "#57cc99"],
            [0.50, "#e9c46a"],
            [0.75, "#f4a261"],
            [1.00, "#e63946"]
        ],
        range_color=[0,100]
    )

    fig_map.update_layout(
        height=520,
        margin=dict(l=0,r=0,t=10,b=0),
        paper_bgcolor="white",
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#cccccc",
            showland=True,
            landcolor="#f8fafc",
            showocean=True,
            oceancolor="#edf6f9"
        )
    )

    st.plotly_chart(fig_map, use_container_width=True)

    # ─────────────────────────────────────────────────────────────
    # COMBINED GRAPHS UNDER MAP
    # ─────────────────────────────────────────────────────────────
    st.markdown(
        '<div class="section-header">Combined Analytics Overview</div>',
        unsafe_allow_html=True
    )

    col_left, col_right = st.columns([1.2,1])

    # ───────────────────────── LEFT : CORRELATION
    with col_left:

        corr_vars = ["learning_poverty"] + IND_VARS
        corr_matrix = full[corr_vars].corr()

        fig_corr = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1,
            zmax=1
        )

        fig_corr.update_layout(
            title="Correlation Matrix",
            height=420,
            margin=dict(l=0,r=0,t=40,b=0),
            paper_bgcolor="white"
        )

        st.plotly_chart(fig_corr, use_container_width=True)

    # ───────────────────────── RIGHT : DISTRIBUTION
    with col_right:

        fig_hist = px.histogram(
            yr_data,
            x="learning_poverty",
            nbins=20,
            color_discrete_sequence=["#1a6b4a"]
        )

        fig_hist.update_layout(
            title="Distribution of Learning Poverty",
            height=200,
            margin=dict(l=0,r=0,t=40,b=0),
            paper_bgcolor="white",
            plot_bgcolor="#f8fafc"
        )

        st.plotly_chart(fig_hist, use_container_width=True)

        top10 = yr_data.nlargest(
            10,
            "learning_poverty"
        )[
            ["Country Name","learning_poverty"]
        ]

        fig_bar = px.bar(
            top10,
            x="learning_poverty",
            y="Country Name",
            orientation="h",
            color="learning_poverty",
            color_continuous_scale="Reds"
        )

        fig_bar.update_layout(
            title="Highest Learning Poverty",
            height=200,
            margin=dict(l=0,r=0,t=40,b=0),
            paper_bgcolor="white"
        )

        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown(f"""
    <div class="insight">
    <strong>Key Insight:</strong>
    {pct_50:.0f}% of reporting countries exceed 50% learning poverty in {sel_year}.
    Countries with higher under-5 mortality and lower educational investment consistently
    show the worst reading outcomes.
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# TAB 2 — TRENDS & DRIVERS
# ═════════════════════════════════════════════════════════════════════
with tab2:

    trend_data = full[
        full["Country Name"].isin(sel_countries)
    ].sort_values("Year")

    st.markdown(
        '<div class="section-header">Learning Poverty Trends + Drivers</div>',
        unsafe_allow_html=True
    )

    # ─────────────────────────────────────────────────────────────
    # COMBINED MULTI-PANEL FIGURE
    # ─────────────────────────────────────────────────────────────
    fig = make_subplots(
        rows=3,
        cols=2,
        subplot_titles=(
            "Learning Poverty",
            "Pupil-Teacher Ratio",
            "Trained Teachers (%)",
            "Government Expenditure",
            "Under-5 Mortality",
            ""
        ),
        vertical_spacing=0.12
    )

    for i, country in enumerate(sel_countries):

        cdata = trend_data[
            trend_data["Country Name"] == country
        ]

        color = PALETTE[i % len(PALETTE)]

        # Learning Poverty
        fig.add_trace(
            go.Scatter(
                x=cdata["Year"],
                y=cdata["learning_poverty"],
                mode="lines+markers",
                name=country,
                line=dict(width=2.5,color=color)
            ),
            row=1,col=1
        )

        # PTR
        fig.add_trace(
            go.Scatter(
                x=cdata["Year"],
                y=cdata["pupil_teacher_ratio"],
                mode="lines",
                showlegend=False,
                line=dict(color=color)
            ),
            row=1,col=2
        )

        # TT
        fig.add_trace(
            go.Scatter(
                x=cdata["Year"],
                y=cdata["trained_teachers"],
                mode="lines",
                showlegend=False,
                line=dict(color=color)
            ),
            row=2,col=1
        )

        # GE
        fig.add_trace(
            go.Scatter(
                x=cdata["Year"],
                y=cdata["gov_expenditure"],
                mode="lines",
                showlegend=False,
                line=dict(color=color)
            ),
            row=2,col=2
        )

        # U5
        fig.add_trace(
            go.Scatter(
                x=cdata["Year"],
                y=cdata["u5_mortality"],
                mode="lines",
                showlegend=False,
                line=dict(color=color)
            ),
            row=3,col=1
        )

    fig.update_layout(
        height=950,
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02
        )
    )

    st.plotly_chart(fig, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════
# TAB 3 — REGRESSION
# ═════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown(
        '<div class="section-header">Regression Diagnostics & Model Performance</div>',
        unsafe_allow_html=True
    )

    # ─────────────────────────────────────────────────────────────
    # COMBINED REGRESSION DASHBOARD
    # ─────────────────────────────────────────────────────────────
    reg_fig = make_subplots(
        rows=2,
        cols=2,
        subplot_titles=(
            "Regression Coefficients",
            "Actual vs Predicted",
            "Residual Distribution",
            "Coefficient Magnitudes"
        ),
        vertical_spacing=0.16
    )

    # Coefficients
    coef_names = [k for k in COEFS if k != "const"]
    coef_vals = [COEFS[k] for k in coef_names]

    reg_fig.add_trace(
        go.Bar(
            x=coef_vals,
            y=[IND_LABELS[k] for k in coef_names],
            orientation="h",
            marker_color=[
                "#e63946" if v > 0 else "#1a6b4a"
                for v in coef_vals
            ]
        ),
        row=1,col=1
    )

    # Actual vs Predicted
    fit_data = full.dropna(
        subset=[
            "learning_poverty",
            "predicted_learning_poverty"
        ]
    )

    reg_fig.add_trace(
        go.Scatter(
            x=fit_data["learning_poverty"],
            y=fit_data["predicted_learning_poverty"],
            mode="markers",
            marker=dict(
                size=7,
                color=fit_data["learning_poverty"],
                colorscale="RdYlGn_r",
                opacity=0.7
            )
        ),
        row=1,col=2
    )

    # Residuals
    reg_fig.add_trace(
        go.Histogram(
            x=fit_data["huber_residuals"],
            marker_color="#457b9d"
        ),
        row=2,col=1
    )

    # Absolute coefficient magnitudes
    reg_fig.add_trace(
        go.Bar(
            x=[IND_LABELS[k] for k in coef_names],
            y=[abs(v) for v in coef_vals],
            marker_color="#1a6b4a"
        ),
        row=2,col=2
    )

    reg_fig.update_layout(
        height=820,
        paper_bgcolor="white",
        plot_bgcolor="#f8fafc",
        showlegend=False
    )

    st.plotly_chart(reg_fig, use_container_width=True)

    st.markdown("""
    <div class="insight">
    <strong>Why Robust Regression?</strong>
    OLS assumptions were violated due to heteroscedasticity,
    non-normal residuals, autocorrelation, and influential outliers.
    The Huber estimator provides more stable coefficient estimates
    by down-weighting extreme observations.
    </div>
    """, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════
# TAB 4 — PREDICTOR
# ═════════════════════════════════════════════════════════════════════
with tab4:

    st.markdown(
        '<div class="section-header">Interactive Learning Poverty Predictor</div>',
        unsafe_allow_html=True
    )

    fc_data = full[
        full["Country Name"] == focus_country
    ].sort_values("Year").dropna(
        subset=IND_VARS
    ).tail(1)

    def_vals = {
        "pupil_teacher_ratio":
            float(fc_data["pupil_teacher_ratio"].values[0]),

        "trained_teachers":
            float(fc_data["trained_teachers"].values[0]),

        "gov_expenditure":
            float(fc_data["gov_expenditure"].values[0]),

        "u5_mortality":
            float(fc_data["u5_mortality"].values[0])
    }

    c1, c2 = st.columns([1.1,1])

    with c1:

        ptr = st.slider(
            "Pupil-Teacher Ratio",
            5.0,80.0,
            round(def_vals["pupil_teacher_ratio"],1)
        )

        tt = st.slider(
            "Trained Teachers (%)",
            0.0,100.0,
            round(def_vals["trained_teachers"],1)
        )

        ge = st.slider(
            "Gov. Expenditure",
            0.0,50.0,
            round(def_vals["gov_expenditure"],1)
        )

        um = st.slider(
            "Under-5 Mortality",
            2.0,75.0,
            round(def_vals["u5_mortality"],1)
        )

    lp_pred = predict(ptr,tt,ge,um)
    color = lp_color(lp_pred)

    with c2:

        st.markdown(f"""
        <div style="
            background:white;
            border:3px solid {color};
            border-radius:18px;
            padding:28px;
            text-align:center;
            box-shadow:0 4px 16px rgba(0,0,0,0.06);
        ">
            <div style="
                font-size:0.75rem;
                font-weight:700;
                color:#6b7280;
                text-transform:uppercase;
                letter-spacing:1px;
            ">
                Predicted Learning Poverty
            </div>

            <div style="
                font-size:5rem;
                font-weight:900;
                color:{color};
                line-height:1;
                margin-top:10px;
            ">
                {lp_pred:.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=lp_pred,
            gauge={
                "axis":{"range":[0,100]},
                "bar":{"color":color}
            }
        ))

        gauge.update_layout(height=260)

        st.plotly_chart(gauge, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════
# TAB 5 — ABOUT
# ═════════════════════════════════════════════════════════════════════
with tab5:

    st.markdown("""
    ### 📌 Research Objective

    Investigate the socioeconomic and educational factors associated with
    learning poverty across countries using robust regression methods.

    ---

    ### 🔬 Methodology

    **Model:** Robust Linear Regression (Huber M-estimator)

    **Variables Included**
    - Pupil-Teacher Ratio
    - Trained Teachers (%)
    - Government Expenditure
    - Under-5 Mortality

    ---

    ### 🌍 Dataset

    - Source: World Bank Open Data
    - Coverage: 75 countries
    - Years: 2000–2023
    - Final observations: 370

    ---

    ### 🎯 Key Finding

    Under-5 mortality is the strongest predictor of learning poverty,
    suggesting that education outcomes are deeply interconnected with
    public health and early childhood development.

    ---
    """)

# ─────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────
st.markdown("---")

st.markdown("""
<div style="
    text-align:center;
    font-size:0.75rem;
    color:#9ca3af;
    padding-bottom:12px;
">
Built with Streamlit · SDG 4 — Quality Education ·
World Bank Open Data · Robust Regression (Huber)
</div>
""", unsafe_allow_html=True)
