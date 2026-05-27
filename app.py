"""
╔══════════════════════════════════════════════════════════════════════╗
║   LEARNING POVERTY DASHBOARD — SDG 4: Quality Education             ║
║   What drives the share of children who cannot read by end          ║
║   of primary school?                                                ║
║                                                                      ║
║   Model: Robust Regression (Huber M-estimator / IRLS)               ║
║   Data:  World Bank Open Data, 75 countries, 2000–2023              ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import json
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ─── PAGE CONFIG ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Learning Poverty | SDG 4",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Global */
  html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

  /* Hide default streamlit header decoration */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }
  header { visibility: hidden; }

  /* Hero banner */
  .hero {
    background: linear-gradient(135deg, #0a3d2e 0%, #1a6b4a 50%, #2d9e6b 100%);
    border-radius: 16px;
    padding: 36px 40px 28px;
    margin-bottom: 24px;
    color: white;
  }
  .hero h1 {
    font-size: 2.2rem; font-weight: 800;
    margin: 0 0 8px; color: white; letter-spacing: -0.5px;
  }
  .hero .sub {
    font-size: 1.05rem; opacity: 0.85; margin: 0 0 18px;
  }
  .hero .badges { display: flex; gap: 10px; flex-wrap: wrap; }
  .badge {
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px; padding: 4px 14px;
    font-size: 0.78rem; font-weight: 600; color: white;
  }

  /* KPI cards */
  .kpi-row { display: flex; gap: 14px; margin-bottom: 20px; flex-wrap: wrap; }
  .kpi {
    flex: 1; min-width: 140px;
    background: white;
    border: 1px solid #e8ecf0;
    border-radius: 14px;
    padding: 18px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,.05);
  }
  .kpi-label {
    font-size: 0.72rem; font-weight: 700; color: #6b7280;
    text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;
  }
  .kpi-val { font-size: 2rem; font-weight: 800; line-height: 1; }
  .kpi-sub { font-size: 0.72rem; color: #9ca3af; margin-top: 4px; }

  /* Section headers */
  .section-header {
    font-size: 0.7rem; font-weight: 700; color: #6b7280;
    text-transform: uppercase; letter-spacing: 1.2px;
    margin: 0 0 10px; border-bottom: 2px solid #f0f4f8; padding-bottom: 6px;
  }

  /* Insight box */
  .insight {
    background: #f0fdf4;
    border-left: 4px solid #1a6b4a;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    font-size: 0.87rem;
    color: #1a3a2e;
    line-height: 1.65;
    margin-top: 12px;
  }
  .insight strong { color: #0a3d2e; }

  /* Equation card */
  .eq-card {
    background: #1a1a2e;
    border-radius: 12px;
    padding: 18px 22px;
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    color: #7ee8c8;
    line-height: 1.8;
    margin: 12px 0;
  }

  /* Significance pill */
  .sig { background: #d1fae5; color: #065f46; padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; }
  .nsig { background: #fee2e2; color: #991b1b; padding: 2px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; }

  /* Tab styling override */
  .stTabs [data-baseweb="tab-list"] {
    gap: 4px; background: #f8f9fa;
    border-radius: 12px; padding: 4px;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 9px; padding: 8px 18px;
    font-size: 0.83rem; font-weight: 600;
  }

  /* Metric delta */
  [data-testid="metric-container"] { background: white; border-radius: 12px; padding: 16px; border: 1px solid #e8ecf0; }
</style>
""", unsafe_allow_html=True)


# ─── DATA LOADING ────────────────────────────────────────────────────
@st.cache_data
def load_data():
    dd   = pd.read_csv("dashboard_data.csv")
    cd   = pd.read_csv("cleaned_dataset.csv")
    diag = pd.read_csv("diagnostics_results.csv")
    corr = pd.read_csv("correlation_results.csv")
    with open("model_params.json") as f:
        mp = json.load(f)
    full = cd.merge(
        dd[["Country Name","Country Code","Year",
            "predicted_learning_poverty","huber_residuals"]],
        on=["Country Name","Country Code","Year"], how="left"
    )
    return full, diag, corr, mp

full, diag, corr_df, mp = load_data()

COEFS   = mp["coefficients"]
PVALS   = mp["p_values"]
CI      = mp["confidence_intervals"]
YEARS   = sorted(full["Year"].unique().tolist())
COUNTRIES = sorted(full["Country Name"].unique().tolist())

IND_VARS = ["pupil_teacher_ratio","trained_teachers",
            "gov_expenditure","u5_mortality"]
IND_LABELS = {
    "pupil_teacher_ratio":  "Pupil-Teacher Ratio",
    "trained_teachers":     "Trained Teachers (%)",
    "gov_expenditure":      "Gov. Expenditure per Student (% GDP/cap)",
    "u5_mortality":         "Under-5 Mortality (per 1,000 live births)",
}

PALETTE = ["#1a6b4a","#e63946","#457b9d","#f4a261","#6a4c93","#2a9d8f"]

# ─── COLOR HELPER ───────────────────────────────────────────────────
def lp_color(v):
    if v is None or np.isnan(v): return "#cccccc"
    if v < 15:  return "#2a9d8f"
    if v < 35:  return "#57cc99"
    if v < 55:  return "#e9c46a"
    if v < 75:  return "#f4a261"
    return "#e63946"

def predict(ptr, tt, ge, um):
    val = (COEFS["const"]
           + COEFS["pupil_teacher_ratio"] * ptr
           + COEFS["trained_teachers"]    * tt
           + COEFS["gov_expenditure"]     * ge
           + COEFS["u5_mortality"]        * um)
    return max(0.0, min(100.0, val))


# ════════════════════════════════════════════════════════════════════
# HERO BANNER
# ════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <h1>📚 Learning Poverty Dashboard</h1>
  <p class="sub">What factors drive the share of children who cannot read by end of primary school?<br>
  A regression-based analysis across 75 countries, 2000–2023 — SDG 4: Quality Education</p>
  <div class="badges">
    <span class="badge">🌍 75 Countries</span>
    <span class="badge">📅 2000–2023</span>
    <span class="badge">📊 Robust Regression (Huber)</span>
    <span class="badge">🏦 World Bank Open Data</span>
    <span class="badge">🎯 SDG 4 — Quality Education</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# SIDEBAR CONTROLS
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    st.markdown("---")

    sel_year = st.slider(
        "📅 Select Year",
        min_value=int(min(YEARS)),
        max_value=int(max(YEARS)),
        value=2015, step=1,
    )

    st.markdown("---")
    sel_countries = st.multiselect(
        "🌍 Compare Countries",
        options=COUNTRIES,
        default=["Niger","Colombia","Spain","Korea, Rep."],
    )

    st.markdown("---")
    focus_country = st.selectbox(
        "🔎 Focus Country (Predictor Tab)",
        options=COUNTRIES,
        index=COUNTRIES.index("Colombia") if "Colombia" in COUNTRIES else 0,
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem;color:#9ca3af;line-height:1.6'>
    <strong>Model:</strong> Robust Linear Regression<br>
    (Huber M-estimator, IRLS)<br><br>
    <strong>Predictors:</strong><br>
    • Pupil-teacher ratio<br>
    • Trained teachers (%)<br>
    • Gov. expenditure per student<br>
    • Under-5 mortality<br><br>
    <strong>Source:</strong> World Bank Open Data<br>
    <strong>SDG:</strong> Goal 4 — Quality Education
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# KPI ROW
# ════════════════════════════════════════════════════════════════════
yr_data = full[full["Year"] == sel_year].dropna(subset=["learning_poverty"])

avg_lp   = yr_data["learning_poverty"].mean()
n_cntry  = len(yr_data)
worst_r  = yr_data.loc[yr_data["learning_poverty"].idxmax()]
best_r   = yr_data.loc[yr_data["learning_poverty"].idxmin()]
pct_50   = (yr_data["learning_poverty"] > 50).mean() * 100

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🌍 Avg. Learning Poverty", f"{avg_lp:.1f}%",
              help="Average across all countries with data for selected year")
with col2:
    st.metric("📊 Countries Reporting", str(n_cntry),
              help="Countries with learning poverty data in selected year")
with col3:
    st.metric("⚠️ Highest LP", worst_r["Country Name"].split(",")[0],
              delta=f"{worst_r['learning_poverty']:.1f}%", delta_color="inverse")
with col4:
    st.metric("✅ Lowest LP", best_r["Country Name"].split(",")[0],
              delta=f"{best_r['learning_poverty']:.1f}%", delta_color="normal")
with col5:
    st.metric("📈 Above 50%", f"{pct_50:.0f}%",
              help="Share of reporting countries exceeding 50% learning poverty")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════
tab_map, tab_trends, tab_drivers, tab_regression, tab_predictor, tab_about = st.tabs([
    "🗺️  World Map",
    "📈  Trends",
    "🔍  Drivers",
    "📐  Regression",
    "🧮  Predictor",
    "ℹ️  About",
])


# ════════════════════════════════════════════════════════════════════
# TAB 1: WORLD MAP
# ════════════════════════════════════════════════════════════════════
with tab_map:
    st.markdown(f'<div class="section-header">Learning Poverty Rate by Country — {sel_year}</div>',
                unsafe_allow_html=True)

    fig_map = px.choropleth(
        yr_data,
        locations="Country Code",
        color="learning_poverty",
        hover_name="Country Name",
        hover_data={
            "learning_poverty":       ":.1f",
            "predicted_learning_poverty": ":.1f",
            "pupil_teacher_ratio":    ":.1f",
            "trained_teachers":       ":.1f",
            "gov_expenditure":        ":.1f",
            "u5_mortality":           ":.1f",
            "Country Code":           False,
        },
        labels={
            "learning_poverty":           "Learning Poverty (%)",
            "predicted_learning_poverty": "Predicted LP (%)",
            "pupil_teacher_ratio":        "Pupil-Teacher Ratio",
            "trained_teachers":           "Trained Teachers (%)",
            "gov_expenditure":            "Gov. Expenditure (% GDP/cap)",
            "u5_mortality":               "Under-5 Mortality (per 1,000)",
        },
        color_continuous_scale=[
            [0.00, "#2a9d8f"], [0.15, "#57cc99"],
            [0.35, "#e9c46a"], [0.55, "#f4a261"],
            [0.75, "#e63946"], [1.00, "#6b0000"],
        ],
        range_color=[0, 100],
        title=f"Learning Poverty Rate (%) — {sel_year}",
    )
    fig_map.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(
            title="LP (%)", thickness=14, len=0.6,
            tickvals=[0,25,50,75,100],
        ),
        geo=dict(
            showframe=False, showcoastlines=True,
            coastlinecolor="#cccccc", showland=True,
            landcolor="#f0f4f8", showocean=True,
            oceancolor="#e8f4f8",
        ),
        paper_bgcolor="white", plot_bgcolor="white",
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown(f"""
    <div class="insight">
    <strong>What this map reveals in {sel_year}:</strong> Of {n_cntry} countries with data,
    <strong>{pct_50:.0f}%</strong> have learning poverty above 50%, meaning more than half of children
    leave primary school without basic reading ability. The highest rate is
    <strong>{worst_r['Country Name']} ({worst_r['learning_poverty']:.1f}%)</strong>,
    while the lowest is <strong>{best_r['Country Name']} ({best_r['learning_poverty']:.1f}%)</strong>.
    This gap reveals that learning poverty is not a fixed condition — it is driven by measurable,
    addressable factors. Use the year slider to see how this has changed over time.
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# TAB 2: TRENDS
# ════════════════════════════════════════════════════════════════════
with tab_trends:
    if not sel_countries:
        st.warning("Select at least one country from the sidebar to view trends.")
    else:
        st.markdown('<div class="section-header">Learning Poverty Over Time</div>',
                    unsafe_allow_html=True)

        trend_data = full[full["Country Name"].isin(sel_countries)].sort_values("Year")

        # LP trend line chart
        fig_lp = px.line(
            trend_data.dropna(subset=["learning_poverty"]),
            x="Year", y="learning_poverty",
            color="Country Name",
            markers=True,
            labels={"learning_poverty": "Learning Poverty (%)", "Country Name": "Country"},
            color_discrete_sequence=PALETTE,
            title="Learning Poverty Rate Over Time",
        )
        fig_lp.update_traces(line_width=2.5, marker_size=7)
        fig_lp.update_layout(
            height=380, paper_bgcolor="white", plot_bgcolor="#f8f9fa",
            xaxis=dict(gridcolor="#e8ecf0"), yaxis=dict(gridcolor="#e8ecf0", range=[0,105]),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_lp, use_container_width=True)

        # Predictor trends — 2 x 2 grid
        st.markdown('<div class="section-header">Driver Trends for Selected Countries</div>',
                    unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        driver_pairs = [
            ("pupil_teacher_ratio", "Pupil-Teacher Ratio", c1),
            ("trained_teachers",    "Trained Teachers (%)", c2),
            ("gov_expenditure",     "Gov. Expenditure (% GDP/cap)", c1),
            ("u5_mortality",        "Under-5 Mortality (per 1,000)", c2),
        ]
        for var, title, col in driver_pairs:
            with col:
                fig = px.line(
                    trend_data.dropna(subset=[var]),
                    x="Year", y=var,
                    color="Country Name",
                    markers=True,
                    labels={var: title, "Country Name": ""},
                    color_discrete_sequence=PALETTE,
                    title=title,
                )
                fig.update_traces(line_width=2, marker_size=5)
                fig.update_layout(
                    height=280, paper_bgcolor="white", plot_bgcolor="#f8f9fa",
                    xaxis=dict(gridcolor="#e8ecf0"),
                    yaxis=dict(gridcolor="#e8ecf0"),
                    showlegend=False,
                    margin=dict(l=0, r=0, t=36, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# TAB 3: DRIVERS (scatter plots)
# ════════════════════════════════════════════════════════════════════
with tab_drivers:
    st.markdown(f'<div class="section-header">What Drives Learning Poverty? — {sel_year}</div>',
                unsafe_allow_html=True)

    # Correlation heatmap
    c_left, c_right = st.columns([1.2, 1])
    with c_left:
        corr_vars = ["learning_poverty"] + IND_VARS
        corr_matrix = full[corr_vars].corr()
        labels_short = {
            "learning_poverty":     "Learning Poverty",
            "pupil_teacher_ratio":  "Pupil-Teacher Ratio",
            "trained_teachers":     "Trained Teachers",
            "gov_expenditure":      "Gov. Expenditure",
            "u5_mortality":         "U5 Mortality",
        }
        corr_renamed = corr_matrix.rename(columns=labels_short, index=labels_short)
        fig_corr = px.imshow(
            corr_renamed,
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            text_auto=".2f",
            title="Pearson Correlation Matrix",
            aspect="auto",
        )
        fig_corr.update_layout(
            height=360, paper_bgcolor="white",
            coloraxis_colorbar=dict(title="r", thickness=12, len=0.8),
            margin=dict(l=0, r=0, t=40, b=0),
        )
        fig_corr.update_traces(textfont_size=11)
        st.plotly_chart(fig_corr, use_container_width=True)

    with c_right:
        st.markdown("""
        <div class="insight">
        <strong>Correlation Highlights:</strong><br><br>
        🔴 <strong>Under-5 Mortality</strong> has the strongest positive correlation
        with learning poverty (r = 0.86) — countries with poor child health outcomes
        also have the worst reading proficiency.<br><br>
        🔴 <strong>Pupil-Teacher Ratio</strong> (r = 0.68) — overcrowded classrooms
        strongly associate with higher learning poverty.<br><br>
        🟢 <strong>Trained Teachers</strong> (r = −0.45) — more professionally trained
        teachers correlate with lower learning poverty.<br><br>
        🟢 <strong>Gov. Expenditure</strong> (r = −0.32) — higher investment per student
        links to lower rates.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f'<div class="section-header">Scatter Plots — Each Driver vs. Learning Poverty ({sel_year})</div>',
                unsafe_allow_html=True)

    yr_scatter = full[full["Year"] == sel_year].dropna(subset=["learning_poverty"])
    col1, col2 = st.columns(2)
    scatter_pairs = [
        ("pupil_teacher_ratio", "Pupil-Teacher Ratio",          col1, PALETTE[0]),
        ("trained_teachers",    "Trained Teachers (%)",          col2, PALETTE[1]),
        ("gov_expenditure",     "Gov. Expenditure (% GDP/cap)",  col1, PALETTE[2]),
        ("u5_mortality",        "Under-5 Mortality (per 1,000)", col2, PALETTE[3]),
    ]
    for var, label, col, color in scatter_pairs:
        d_sc = yr_scatter.dropna(subset=[var])
        with col:
            fig_sc = px.scatter(
                d_sc, x=var, y="learning_poverty",
                hover_name="Country Name",
                hover_data={"learning_poverty": ":.1f", var: ":.1f"},
                labels={var: label, "learning_poverty": "Learning Poverty (%)"},
                trendline="ols",
                trendline_color_override="#e63946",
                title=f"{label} vs. Learning Poverty",
                color_discrete_sequence=[color],
            )
            fig_sc.update_traces(marker_size=9, marker_opacity=0.7)
            fig_sc.update_layout(
                height=320, paper_bgcolor="white", plot_bgcolor="#f8f9fa",
                xaxis=dict(gridcolor="#e8ecf0"),
                yaxis=dict(gridcolor="#e8ecf0", range=[0,105]),
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig_sc, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# TAB 4: REGRESSION RESULTS
# ════════════════════════════════════════════════════════════════════
with tab_regression:
    st.markdown('<div class="section-header">Robust Regression Results (Huber M-estimator)</div>',
                unsafe_allow_html=True)

    col_coef, col_fit = st.columns([1, 1])

    # ── Coefficient plot
    with col_coef:
        coef_names = [k for k in COEFS if k != "const"]
        coef_vals  = [COEFS[k] for k in coef_names]
        ci_lo      = [CI[k]["0"] for k in coef_names]
        ci_hi      = [CI[k]["1"] for k in coef_names]
        p_vals_list = [PVALS[k] for k in coef_names]
        bar_colors  = ["#e63946" if v > 0 else "#1a6b4a" for v in coef_vals]

        fig_coef = go.Figure()
        for i, (name, val, lo, hi, pv, col) in enumerate(
                zip(coef_names, coef_vals, ci_lo, ci_hi, p_vals_list, bar_colors)):
            sig_label = "★ Significant" if pv < 0.05 else "✗ Not significant"
            fig_coef.add_trace(go.Bar(
                x=[val], y=[IND_LABELS.get(name, name)],
                orientation="h",
                marker_color=col,
                name=sig_label,
                showlegend=False,
                error_x=dict(
                    type="data",
                    symmetric=False,
                    array=[hi - val],
                    arrayminus=[val - lo],
                    color="#555555",
                    thickness=2, width=6,
                ),
                customdata=[[name, val, pv, lo, hi]],
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Coefficient: %{x:.3f}<br>"
                    "95% CI: [%{customdata[3]:.3f}, %{customdata[4]:.3f}]<br>"
                    "p-value: %{customdata[2]:.4f}<extra></extra>"
                ),
            ))

        fig_coef.add_vline(x=0, line_color="#333333", line_width=1.5)
        fig_coef.update_layout(
            title="Regression Coefficients (raw scale)",
            height=320, paper_bgcolor="white", plot_bgcolor="#f8f9fa",
            xaxis=dict(title="Coefficient (per unit change in predictor)",
                       gridcolor="#e8ecf0", zeroline=False),
            yaxis=dict(gridcolor="#e8ecf0"),
            margin=dict(l=0, r=20, t=40, b=0),
            barmode="overlay",
        )
        st.plotly_chart(fig_coef, use_container_width=True)

        # Significance table
        sig_rows = []
        for k in coef_names:
            p = PVALS[k]
            c = COEFS[k]
            direction = "↑ Increases LP" if c > 0 else "↓ Decreases LP"
            sig_rows.append({
                "Variable":  IND_LABELS.get(k, k),
                "Coef":      f"{c:+.4f}",
                "p-value":   f"{p:.4f}",
                "Direction": direction,
                "Significant": "✅ Yes" if p < 0.05 else "❌ No",
            })
        st.dataframe(pd.DataFrame(sig_rows), hide_index=True, use_container_width=True)

    # ── Actual vs Predicted
    with col_fit:
        fit_data = full.dropna(subset=["learning_poverty","predicted_learning_poverty"])
        fig_fit = px.scatter(
            fit_data,
            x="learning_poverty",
            y="predicted_learning_poverty",
            hover_name="Country Name",
            hover_data={"Year": True, "learning_poverty": ":.1f",
                        "predicted_learning_poverty": ":.1f"},
            labels={
                "learning_poverty": "Actual Learning Poverty (%)",
                "predicted_learning_poverty": "Predicted (%)",
            },
            color="learning_poverty",
            color_continuous_scale=[
                [0,"#2a9d8f"],[0.5,"#e9c46a"],[1,"#e63946"]
            ],
            title="Actual vs. Predicted Learning Poverty",
        )
        fig_fit.add_shape(
            type="line", x0=0, y0=0, x1=100, y1=100,
            line=dict(color="#e63946", dash="dash", width=1.5),
        )
        fig_fit.update_traces(marker_size=8, marker_opacity=0.7)
        fig_fit.update_layout(
            height=320, paper_bgcolor="white", plot_bgcolor="#f8f9fa",
            xaxis=dict(range=[0,105], gridcolor="#e8ecf0"),
            yaxis=dict(range=[0,105], gridcolor="#e8ecf0"),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_fit, use_container_width=True)

        # Residual histogram
        fig_res = px.histogram(
            fit_data, x="huber_residuals",
            nbins=30,
            labels={"huber_residuals": "Huber Residual"},
            title="Distribution of Huber Residuals",
            color_discrete_sequence=["#457b9d"],
        )
        fig_res.update_layout(
            height=240, paper_bgcolor="white", plot_bgcolor="#f8f9fa",
            xaxis=dict(gridcolor="#e8ecf0"),
            yaxis=dict(gridcolor="#e8ecf0", title="Count"),
            margin=dict(l=0, r=0, t=40, b=0),
            bargap=0.05,
        )
        st.plotly_chart(fig_res, use_container_width=True)

    # ── Regression Equation
    st.markdown("---")
    eq_parts = " + ".join([
        f"({COEFS[k]:+.4f} × {IND_LABELS.get(k,k)})" for k in coef_names
    ])
    st.markdown(f"""
    <div class="section-header">Regression Equation</div>
    <div class="eq-card">
      <span style="color:#ffd700;font-weight:700">Learning Poverty</span>
      <span style="color:#ffffff"> = </span>
      <span style="color:#7ee8c8">{COEFS['const']:.4f}</span>
      <span style="color:#ffffff"> + </span>
      <span style="color:#a8d8ea">{COEFS['pupil_teacher_ratio']:+.4f} × Pupil-Teacher Ratio</span>
      <span style="color:#ffffff"> + </span>
      <span style="color:#a8d8ea">{COEFS['trained_teachers']:+.4f} × Trained Teachers (%)</span>
      <span style="color:#ffffff"> + </span>
      <span style="color:#a8d8ea">{COEFS['gov_expenditure']:+.4f} × Gov. Expenditure</span>
      <span style="color:#ffffff"> + </span>
      <span style="color:#ffb3b3">{COEFS['u5_mortality']:+.4f} × Under-5 Mortality</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Diagnostics
    st.markdown("---")
    st.markdown('<div class="section-header">OLS Assumption Diagnostics — Why Robust Regression?</div>',
                unsafe_allow_html=True)

    diag_display = diag.copy()
    diag_display["Violation Status"] = diag_display["Violation Status"].apply(
        lambda x: "🔴 " + x if x == "Violated" else "🟢 " + x
    )
    st.dataframe(diag_display, hide_index=True, use_container_width=True)
    st.markdown("""
    <div class="insight">
    <strong>Why Robust Regression?</strong> All five OLS assumptions were violated in this dataset —
    residuals are non-normal, heteroscedastic, and autocorrelated, with 25 influential outliers.
    These violations make OLS estimates unreliable. The <strong>Huber M-estimator</strong> down-weights
    influential observations and produces stable, unbiased coefficient estimates even when OLS fails,
    making it the correct choice for this analysis.
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# TAB 5: LIVE PREDICTOR
# ════════════════════════════════════════════════════════════════════
with tab_predictor:
    st.markdown('<div class="section-header">Estimate Learning Poverty Using the Regression Model</div>',
                unsafe_allow_html=True)
    st.markdown(f"Adjust the inputs below to estimate learning poverty for any scenario. "
                f"Defaults loaded from **{focus_country}** (latest available data).")

    # Load defaults from focus country
    fc_data = full[full["Country Name"] == focus_country].sort_values("Year").dropna(
        subset=IND_VARS).tail(1)
    def_vals = {
        "pupil_teacher_ratio": float(fc_data["pupil_teacher_ratio"].values[0]) if len(fc_data) else 25.0,
        "trained_teachers":    float(fc_data["trained_teachers"].values[0])    if len(fc_data) else 80.0,
        "gov_expenditure":     float(fc_data["gov_expenditure"].values[0])     if len(fc_data) else 14.0,
        "u5_mortality":        float(fc_data["u5_mortality"].values[0])        if len(fc_data) else 30.0,
    }

    col_in, col_out = st.columns([1.2, 1])

    with col_in:
        ptr = st.slider("👨‍🏫 Pupil-Teacher Ratio (students per teacher)",
                        min_value=5.0, max_value=80.0,
                        value=round(def_vals["pupil_teacher_ratio"], 1), step=0.5)
        tt  = st.slider("🎓 Trained Teachers (%)",
                        min_value=0.0, max_value=100.0,
                        value=round(def_vals["trained_teachers"], 1), step=0.5)
        ge  = st.slider("💰 Gov. Expenditure per Student (% of GDP/cap)",
                        min_value=0.0, max_value=50.0,
                        value=round(def_vals["gov_expenditure"], 1), step=0.5)
        um  = st.slider("👶 Under-5 Mortality (per 1,000 live births)",
                        min_value=2.0, max_value=75.0,
                        value=round(min(def_vals["u5_mortality"], 75.0), 1), step=0.5)

    with col_out:
        lp_pred = predict(ptr, tt, ge, um)
        color   = lp_color(lp_pred)
        label   = ("🔴 Critical" if lp_pred > 75 else
                   "🟠 High"     if lp_pred > 50 else
                   "🟡 Moderate" if lp_pred > 25 else
                   "🟢 Low"      if lp_pred > 10 else
                   "🟢 Very Low")

        st.markdown(f"""
        <div style="background:white;border:2px solid {color};border-radius:16px;
                    padding:28px;text-align:center;box-shadow:0 4px 16px {color}33;">
          <div style="font-size:0.75rem;font-weight:700;color:#6b7280;
                      text-transform:uppercase;letter-spacing:1px;margin-bottom:12px">
            Estimated Learning Poverty
          </div>
          <div style="font-size:4.5rem;font-weight:900;color:{color};line-height:1">
            {lp_pred:.1f}%
          </div>
          <div style="font-size:0.9rem;color:#6b7280;margin-top:8px">
            of children leave primary school<br>unable to read at grade level
          </div>
          <div style="margin-top:16px;font-size:1rem;font-weight:700;color:{color}">
            {label}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=lp_pred,
            number={"suffix": "%", "font": {"size": 28}},
            gauge={
                "axis":      {"range": [0, 100], "tickwidth": 1},
                "bar":       {"color": color, "thickness": 0.25},
                "bgcolor":   "white",
                "steps": [
                    {"range": [0,  15], "color": "#d1fae5"},
                    {"range": [15, 35], "color": "#fef3c7"},
                    {"range": [35, 55], "color": "#fed7aa"},
                    {"range": [55, 75], "color": "#fecaca"},
                    {"range": [75,100], "color": "#fee2e2"},
                ],
                "threshold": {"line": {"color": color, "width": 3},
                              "thickness": 0.75, "value": lp_pred},
            },
        ))
        fig_gauge.update_layout(
            height=220, paper_bgcolor="white",
            margin=dict(l=20, r=20, t=20, b=10),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    # Insight
    strongest_k = max(IND_VARS, key=lambda k: abs(COEFS[k]))
    st.markdown(f"""
    <div class="insight">
    <strong>How to read this:</strong> At the input values above, the model estimates
    <strong>{lp_pred:.1f}%</strong> learning poverty — rated as <strong>{label}</strong>.
    The single strongest driver in this model is
    <strong>{IND_LABELS[strongest_k]}</strong> with a coefficient of
    <strong>{COEFS[strongest_k]:+.4f}</strong>, meaning each additional unit of this variable
    shifts predicted learning poverty by {abs(COEFS[strongest_k]):.2f} percentage points.
    This tool lets policymakers ask: "If we reduce class sizes or train more teachers,
    by how much does learning poverty fall?"
    </div>
    """, unsafe_allow_html=True)

    # Country comparison table
    st.markdown("---")
    st.markdown('<div class="section-header">Country Snapshot — Latest Available Data</div>',
                unsafe_allow_html=True)
    latest = full.sort_values("Year").groupby("Country Name").last().reset_index()
    snap = latest[["Country Name","Year","learning_poverty","predicted_learning_poverty",
                   "pupil_teacher_ratio","trained_teachers","gov_expenditure","u5_mortality"]].copy()
    snap.columns = ["Country","Year","Actual LP (%)","Predicted LP (%)",
                    "P-T Ratio","Trained Teachers (%)","Gov. Exp. (% GDP/cap)","U5 Mortality"]
    snap = snap.sort_values("Actual LP (%)", ascending=False).reset_index(drop=True)
    st.dataframe(
        snap.style.background_gradient(subset=["Actual LP (%)"], cmap="RdYlGn_r")
                  .format({"Actual LP (%)":":.1f","Predicted LP (%)":":.1f",
                           "P-T Ratio":":.1f","Trained Teachers (%)":":.1f",
                           "Gov. Exp. (% GDP/cap)":":.1f","U5 Mortality":":.1f"}),
        use_container_width=True, height=400,
    )


# ════════════════════════════════════════════════════════════════════
# TAB 6: ABOUT
# ════════════════════════════════════════════════════════════════════
with tab_about:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        ### 📌 Research Question
        > *"What factors significantly influence Learning Poverty across countries?"*

        Learning Poverty — the share of children who cannot read and understand a simple
        text by age 10 — is the SDG 4 flagship indicator. It combines in-school proficiency
        with out-of-school rates to give a complete picture of educational exclusion.

        ---
        ### 🔬 Methodology

        **Model:** Robust Linear Regression (Huber M-estimator)
        — chosen because all five OLS assumptions were violated in this dataset.

        **Response variable:**
        - Learning Poverty Rate (%) — World Bank / UNESCO

        **Explanatory variables (literature-backed):**

        | Variable | Source |
        |---|---|
        | Pupil-Teacher Ratio | Hanushek & Woessmann (2010) |
        | Trained Teachers (%) | UNESCO (2022) |
        | Gov. Expenditure per Student | Psacharopoulos & Patrinos (2018) |
        | Under-5 Mortality | Grantham-McGregor et al. (2007) |

        ---
        ### 📊 Dataset
        - **Source:** World Bank Open Data
        - **Coverage:** 75 countries, 2000–2023
        - **Observations:** 370 (after cleaning)
        - **Cleaning:** Forward/back-fill (max 2 steps), no mean imputation
        """)

    with col_b:
        st.markdown("""
        ### 📐 Model Results Summary

        | Predictor | Coefficient | p-value | Significant? |
        |---|---|---|---|
        | Intercept | +47.14 | < 0.001 | ✅ |
        | Pupil-Teacher Ratio | −0.98 | 0.595 | ❌ |
        | Trained Teachers (%) | −2.82 | 0.011 | ✅ |
        | Gov. Expenditure | −3.64 | 0.001 | ✅ |
        | Under-5 Mortality | +22.74 | < 0.001 | ✅ |

        ---
        ### 🔑 Key Findings

        **Under-5 Mortality** is the dominant driver (coef = +22.74, p < 0.001).
        Countries with high child mortality — a proxy for poor nutrition, healthcare,
        and early childhood development — have dramatically higher learning poverty.
        This underscores that education outcomes are inseparable from health outcomes.

        **Trained Teachers (%)** (coef = −2.82, p = 0.011) — every percentage
        point increase in professionally trained teachers reduces learning poverty
        by 2.8 percentage points on average.

        **Government Expenditure per Student** (coef = −3.64, p < 0.001) —
        the strongest purely educational lever: investing more per student
        drives measurable reductions in learning poverty.

        **Pupil-Teacher Ratio** was not statistically significant in the
        robust model (p = 0.595), suggesting that class size alone may matter
        less than *teacher quality* and *investment* per student.

        ---
        ### 🏦 Data Sources
        - World Bank Open Data — [data.worldbank.org](https://data.worldbank.org)
        - UNESCO UIS — [uis.unesco.org](https://uis.unesco.org)

        ---
        ### 🎓 Course
        **Analytics Techniques and Tools — Finals**
        SDG 4: Quality Education
        """)


# ─── FOOTER ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;font-size:0.75rem;color:#9ca3af;padding:12px 0">
  Built with Streamlit · Data: World Bank Open Data ·
  Model: Robust Regression (Huber M-estimator) ·
  SDG 4 — Quality Education · Analytics Techniques and Tools
</div>
""", unsafe_allow_html=True)
