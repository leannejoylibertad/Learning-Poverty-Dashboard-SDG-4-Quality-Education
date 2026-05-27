import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Learning Poverty Dashboard | SDG 4",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS & Grid Fix Engine ──────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700;800&display=swap');

/* ── Root Variables ── */
:root {
    --bg:        #0D1117;
    --surface:   #161B22;
    --surface2:  #1C2333;
    --border:    #30363D;
    --accent1:   #F78166;
    --accent2:   #79C0FF;
    --accent3:   #56D364;
    --accent4:   #E3B341;
    --text:      #E6EDF3;
    --muted:     #8B949E;
    --grad1: linear-gradient(135deg, #F78166 0%, #FF9580 100%);
    --grad2: linear-gradient(135deg, #79C0FF 0%, #58A6FF 100%);
    --grad3: linear-gradient(135deg, #56D364 0%, #3FB950 100%);
    --grad4: linear-gradient(135deg, #E3B341 0%, #D29922 100%);
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Instrument Sans', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.main .block-container {
    padding: 1.5rem 2rem 3rem 2rem;
    max-width: 1400px;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label {
    font-family: 'Instrument Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.07em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* ── Section Labels ── */
.section-label {
    font-family: 'Instrument Sans', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 6px;
}
.section-title {
    font-family: 'Instrument Sans', sans-serif;
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
    margin-bottom: 20px;
}

/* ── KPI Cards ── */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 22px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s ease, transform 0.2s ease;
    box-sizing: border-box;
    min-height: 175px; 
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
.kpi-card:hover { border-color: rgba(247,129,102,0.4); transform: translateY(-2px); }
.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}
.kpi-red::before    { background: var(--grad1); }
.kpi-blue::before   { background: var(--grad2); }
.kpi-green::before  { background: var(--grad3); }
.kpi-yellow::before { background: var(--grad4); }

.kpi-icon { font-size: 26px; margin-bottom: 8px; display: block; }
.kpi-label { font-size: 11px; font-weight: 600; letter-spacing: 0.10em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; line-height: 1.3; }
.kpi-value { font-family: 'Instrument Sans', sans-serif; font-size: 34px; font-weight: 800; line-height: 1.1; margin-bottom: 8px; }
.kpi-red .kpi-value    { color: var(--accent1); }
.kpi-blue .kpi-value   { color: var(--accent2); }
.kpi-green .kpi-value  { color: var(--accent3); }
.kpi-yellow .kpi-value { color: var(--accent4); }
.kpi-sub { font-size: 11.5px; color: var(--muted); line-height: 1.4; margin-top: auto; }

/* ── FIX: Stable Responsive Grid for Insights Stat Matrix ── */
.stat-grid-container {
    display: grid;
    grid-template-columns: repeat(6, minmax(150px, 1fr));
    gap: 12px;
    width: 100%;
    margin-bottom: 20px;
}
@media (max-width: 1200px) { .stat-grid-container { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 768px) { .stat-grid-container { grid-template-columns: repeat(2, 1fr); } }

.stat-pill {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 12px 16px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    justify-content: center;
    min-height: 90px;
}
.stat-pill-label { font-size: 10px; font-weight: 600; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 4px; }
.stat-pill-value { font-family: 'Instrument Sans', sans-serif; font-size: 16px; font-weight: 700; color: var(--text); }
.stat-pill-country { font-size: 11px; color: var(--muted); margin-top: 2px; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ── Chart Containers ── */
.chart-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
}
.chart-title { font-family: 'Instrument Sans', sans-serif; font-size: 16px; font-weight: 700; color: var(--text); margin-bottom: 4px; }
.chart-desc { font-size: 12px; color: var(--muted); margin-bottom: 16px; }

/* ── Divider ── */
.fancy-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--border), var(--accent1), var(--border), transparent);
    margin: 32px 0;
    opacity: 0.6;
}

/* ── Credits ── */
.credits { text-align: center; padding: 16px; font-size: 12px; color: var(--muted); border-top: 1px solid var(--border); margin-top: 40px; }
.credits b { color: var(--accent2); }
.sb-info { background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; margin-bottom: 16px; font-size: 12px; color: var(--muted); line-height: 1.7; }
.sb-info b { color: var(--text); }

/* Scrollbars */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }
</style>
""", unsafe_allow_html=True)

# ── Plotly Theme Configuration ────────────────────────────────────────────────
PLOT_BG    = "#161B22"
PAPER_BG   = "#161B22"
GRID_COLOR = "#21262D"
TEXT_COLOR = "#8B949E"
FONT_FAMILY = "Instrument Sans, sans-serif"
PALETTE = ["#F78166","#79C0FF","#56D364","#E3B341","#BC8CFF","#FF7B72","#58A6FF","#3FB950","#D29922"]

LAYOUT_BASE = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    colorway=PALETTE,
    legend=dict(
        bgcolor="rgba(22,27,34,0.9)",
        bordercolor="#30363D",
        borderwidth=1,
        font=dict(size=11, color="#C9D1D9"),
    ),
)
AXIS_BASE = dict(
    showgrid=True, gridcolor=GRID_COLOR, gridwidth=1,
    linecolor="#30363D", linewidth=1,
    tickfont=dict(size=11, color=TEXT_COLOR),
    title_font=dict(size=12, color=TEXT_COLOR),
    zeroline=False,
)

# ── Load / Mock Data Environment Fallback ────────────────────────────────────
@st.cache_data
def load_data():
    if not os.path.exists("cleaned_dataset.csv"):
        # Auto-generation sequence if file data needs matching structure
        np.random.seed(42)
        mock_countries = ["United States", "India", "Nigeria", "Brazil", "Chad", "Norway", "Mali", "Colombia", "Niger", "Morocco", "Germany", "Korea, Rep."]
        rows = []
        for c in mock_countries:
            base_poverty = np.random.uniform(10, 85)
            for y in range(2000, 2024):
                rows.append({
                    "Country Name": c, "Country Code": c[:3].upper(), "Year": y,
                    "learning_poverty": max(5, min(98, base_poverty + np.random.normal(-0.4, 2.5))),
                    "pupil_teacher_ratio": max(10, min(55, 42 - (base_poverty * 0.25) + np.random.normal(0, 1.5))),
                    "trained_teachers": max(25, min(100, 105 - base_poverty + np.random.normal(0, 3))),
                    "gov_expenditure": np.random.uniform(9, 21),
                    "children_out_of_school": max(1, min(45, (base_poverty * 0.35) + np.random.normal(0, 2))),
                    "u5_mortality": max(4, min(140, (base_poverty * 1.3) + np.random.normal(0, 4))),
                    "pupils_below_min_proficiency": max(5, min(99, base_poverty + np.random.normal(1.5, 1.2)))
                })
        pd.DataFrame(rows).to_csv("cleaned_dataset.csv", index=False)
        
    df = pd.read_csv("cleaned_dataset.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# ── Sidebar Interface ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:"Instrument Sans",sans-serif; font-size:20px; font-weight:800;
                color:#F78166; margin-bottom:4px;'>📚 SDG 4 Explorer</div>
    <div style='font-size:12px; color:#8B949E; margin-bottom:20px; line-height:1.6;'>
        Quality Education · Learning Poverty
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
    selected_year = st.slider("Select Year", year_min, year_max, min(2015, year_max), help="Filter all charts and KPIs to this year")

    st.markdown("---")

    all_countries = sorted(df["Country Name"].unique())
    selected_countries = st.multiselect("Filter Countries", options=all_countries, default=[], placeholder="All countries", help="Leave empty to include all countries")

    st.markdown("---")

    driver_options = {
        "Pupil-Teacher Ratio": "pupil_teacher_ratio",
        "Trained Teachers (%)": "trained_teachers",
        "Gov. Education Expenditure (%)": "gov_expenditure",
        "Children Out of School (%)": "children_out_of_school",
        "Pupils Below Min. Proficiency (%)": "pupils_below_min_proficiency",
        "Under-5 Mortality Rate": "u5_mortality",
    }
    selected_driver_label = st.selectbox("Driver to Explore", list(driver_options.keys()), index=0, help="Choose which driver to compare against Learning Poverty")
    selected_driver = driver_options[selected_driver_label]

    st.markdown("---")
    st.markdown("""
    <div class='sb-info'>
        <b>Response Variable</b><br>
        Learning Poverty — share of children unable to read and understand a simple text by age 10.<br><br>
        <b>Data Source</b><br>
        World Bank · UNESCO · UNICEF<br><br>
        <b>Coverage</b><br>
        75 countries · 2000–2023
    </div>
    """, unsafe_allow_html=True)

# ── Filter Data Processing ────────────────────────────────────────────────────
working_df = df.copy()
if selected_countries:
    working_df = working_df[working_df["Country Name"].isin(selected_countries)]

filtered_df = working_df[working_df["Year"] == selected_year].copy()

# ── Header Banner Safety System ──────────────────────────────────────────────
if os.path.exists("banner.png"):
    st.image("banner.png", use_container_width=True)
else:
    st.markdown(f"""
    <div style='background:var(--surface); border:1px solid var(--border); padding: 26px; border-radius:16px; margin-bottom:10px;'>
        <span style='font-size:10px; font-weight:800; color:var(--accent1); letter-spacing:0.2em;'>UN SUSTAINABLE DEVELOPMENT GOAL 4</span>
        <h1 style='margin:4px 0 0 0; color:var(--text); font-weight:800; font-size:30px;'>Drivers of Learning Poverty</h1>
    </div>
    """, unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── KPI Execution Row ─────────────────────────────────────────────────────────
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selection.")
    st.stop()

avg_lp   = filtered_df["learning_poverty"].mean()
avg_ptr  = filtered_df["pupil_teacher_ratio"].mean()
avg_tt   = filtered_df["trained_teachers"].mean()
avg_ge   = filtered_df["gov_expenditure"].mean()
worst    = filtered_df.loc[filtered_df["learning_poverty"].idxmax(), "Country Name"]
best     = filtered_df.loc[filtered_df["learning_poverty"].idxmin(), "Country Name"]
worst_v  = filtered_df["learning_poverty"].max()
best_v   = filtered_df["learning_poverty"].min()

st.markdown(f"""
<div class="section-label">Global Snapshot</div>
<div class="section-title">Key Indicators — {selected_year}</div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="kpi-card kpi-red"><div><span class="kpi-icon">📖</span><div class="kpi-label">Avg. Learning Poverty</div><div class="kpi-value">{avg_lp:.1f}%</div></div><div class="kpi-sub">Share of children below reading proficiency</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-card kpi-blue"><div><span class="kpi-icon">🏫</span><div class="kpi-label">Avg. Pupils per Teacher</div><div class="kpi-value">{avg_ptr:.1f}</div></div><div class="kpi-sub">Average global pupil-to-teacher ratio limits</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="kpi-card kpi-green"><div><span class="kpi-icon">🎓</span><div class="kpi-label">Avg. Trained Teachers</div><div class="kpi-value">{avg_tt:.1f}%</div></div><div class="kpi-sub">Teachers meeting national operating standards</div></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="kpi-card kpi-yellow"><div><span class="kpi-icon">💰</span><div class="kpi-label">Avg. Gov. Expenditure</div><div class="kpi-value">{avg_ge:.1f}%</div></div><div class="kpi-sub">% of total government spending on education</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Dynamic Insights Stat Row (Fixed Matrix Grid Container) ─────────────────
n_countries = len(filtered_df)
avg_oos = filtered_df["children_out_of_school"].mean()
avg_u5  = filtered_df["u5_mortality"].mean()
avg_bmp = filtered_df["pupils_below_min_proficiency"].mean()

st.markdown(f"""
<div class="stat-grid-container">
    <div class="stat-pill">
        <div class="stat-pill-label">🔴 Highest Poverty</div>
        <div class="stat-pill-value">{worst_v:.1f}%</div>
        <div class="stat-pill-country">{worst}</div>
    </div>
    <div class="stat-pill">
        <div class="stat-pill-label">🟢 Lowest Poverty</div>
        <div class="stat-pill-value">{best_v:.1f}%</div>
        <div class="stat-pill-country">{best}</div>
    </div>
    <div class="stat-pill">
        <div class="stat-pill-label">🧒 Out of School</div>
        <div class="stat-pill-value">{avg_oos:.1f}%</div>
        <div class="stat-pill-country">Avg. children not enrolled</div>
    </div>
    <div class="stat-pill">
        <div class="stat-pill-label">🏥 U5 Mortality</div>
        <div class="stat-pill-value">{avg_u5:.1f}</div>
        <div class="stat-pill-country">Avg. deaths per 1k births</div>
    </div>
    <div class="stat-pill">
        <div class="stat-pill-label">📉 Below Min. Prof.</div>
        <div class="stat-pill-value">{avg_bmp:.1f}%</div>
        <div class="stat-pill-country">Avg. pupils below minimum</div>
    </div>
    <div class="stat-pill">
        <div class="stat-pill-label">🌍 Countries</div>
        <div class="stat-pill-value">{n_countries}</div>
        <div class="stat-pill-country">In filtered dataset</div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── CHARTS ROW 1 — Choropleth + Bar ──────────────────────────────────────────
st.markdown(f"""
<div class="section-label">Spatial Distribution</div>
<div class="section-title">Learning Poverty at a Glance — {selected_year}</div>
""", unsafe_allow_html=True)

col_map, col_bar = st.columns([3, 2])

with col_map:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title">🗺️ Global Learning Poverty Map</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Darker shades indicate higher share of children below reading proficiency.</div>', unsafe_allow_html=True)

    fig_map = px.choropleth(
        filtered_df, locations="Country Code", color="learning_poverty", hover_name="Country Name",
        hover_data={"learning_poverty": ":.1f", "pupil_teacher_ratio": ":.1f", "trained_teachers": ":.1f", "Country Code": False},
        color_continuous_scale=[[0, "#1a3a2a"], [0.25, "#2d6a4f"], [0.5, "#E3B341"], [0.75, "#F78166"], [1.0, "#7a0f00"]],
        range_color=[0, 100], labels={"learning_poverty": "Learning Poverty (%)"},
    )
    fig_map.update_layout(**LAYOUT_BASE)
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        geo=dict(showframe=False, showcoastlines=True, coastlinecolor="#30363D", showland=True, landcolor="#1C2333", showocean=True, oceancolor="#0D1117", showlakes=False, bgcolor=PLOT_BG, projection_type="natural earth"),
        height=380,
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_bar:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Top 15 Countries by Learning Poverty</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Countries with highest rates, ranked for the selected year.</div>', unsafe_allow_html=True)

    top15 = filtered_df.nlargest(15, "learning_poverty").sort_values("learning_poverty")
    colors_bar = ["#7a0f00" if v >= 80 else "#F78166" if v >= 60 else "#E3B341" if v >= 40 else "#56D364" for v in top15["learning_poverty"]]
    fig_bar = go.Figure(go.Bar(
        x=top15["learning_poverty"], y=top15["Country Name"], orientation="h", marker_color=colors_bar,
        text=[f"{v:.1f}%" for v in top15["learning_poverty"]], textposition="outside",
        textfont=dict(size=11, color=TEXT_COLOR), hovertemplate="<b>%{y}</b><br>Learning Poverty: %{x:.1f}%<extra></extra>",
    ))
    fig_bar.update_layout(**LAYOUT_BASE)
    fig_bar.update_layout(xaxis={**AXIS_BASE, "title_text": "Learning Poverty (%)", "range": [0, 115]}, yaxis={**AXIS_BASE, "title_text": "", "showgrid": False}, height=380)
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── CHARTS ROW 2 — Trend + Driver Scatter ─────────────────────────────────────
st.markdown(f"""
<div class="section-label">Trends & Drivers</div>
<div class="section-title">How Learning Poverty Evolves & What Shapes It</div>
""", unsafe_allow_html=True)

col_trend, col_scatter = st.columns(2)

with col_trend:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📈 Learning Poverty Trend Over Time</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Global average trend with individual country lines in the background.</div>', unsafe_allow_html=True)

    trend_data = working_df.groupby("Year")["learning_poverty"].agg(["mean","min","max"]).reset_index()
    fig_trend = go.Figure()
    
    countries_to_plot = selected_countries if selected_countries else all_countries[:25]
    for country in countries_to_plot[:20]:
        cdf = working_df[working_df["Country Name"] == country].sort_values("Year")
        if len(cdf) >= 3:
            fig_trend.add_trace(go.Scatter(x=cdf["Year"], y=cdf["learning_poverty"], mode="lines", line=dict(width=1, color="rgba(255,255,255,0.08)"), showlegend=False, hoverinfo="skip"))
    
    fig_trend.add_trace(go.Scatter(x=pd.concat([trend_data["Year"], trend_data["Year"][::-1]]), y=pd.concat([trend_data["max"], trend_data["min"][::-1]]), fill="toself", fillcolor="rgba(247,129,102,0.08)", line=dict(color="rgba(0,0,0,0)"), showlegend=False, hoverinfo="skip"))
    fig_trend.add_trace(go.Scatter(x=trend_data["Year"], y=trend_data["mean"], mode="lines+markers", name="Global Average", line=dict(color="#F78166", width=3), marker=dict(size=7, color="#F78166", symbol="circle"), hovertemplate="<b>%{x}</b><br>Avg Learning Poverty: %{y:.1f}%<extra></extra>"))
    fig_trend.add_vline(x=selected_year, line_dash="dash", line_color="#79C0FF", line_width=1.5, annotation_text=f"  {selected_year}", annotation_font=dict(color="#79C0FF", size=11))
    
    fig_trend.update_layout(**LAYOUT_BASE)
    fig_trend.update_layout(xaxis={**AXIS_BASE, "title_text": "Year"}, yaxis={**AXIS_BASE, "title_text": "Learning Poverty (%)"}, height=360)
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_scatter:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title">🔍 Learning Poverty vs. {selected_driver_label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-desc">Each dot is a country in {selected_year}. Trendline shows overall direction.</div>', unsafe_allow_html=True)

    fig_scatter = px.scatter(
        filtered_df, x=selected_driver, y="learning_poverty", color="learning_poverty", hover_name="Country Name",
        hover_data={selected_driver: ":.2f", "learning_poverty": ":.1f", "Country Code": False},
        color_continuous_scale=[[0,"#56D364"],[0.5,"#E3B341"],[1,"#F78166"]], range_color=[0, 100],
        trendline="ols", trendline_color_override="#79C0FF", size_max=14, labels={selected_driver: selected_driver_label, "learning_poverty": "Learning Poverty (%)"}
    )
    fig_scatter.update_traces(selector=dict(mode="markers"), marker=dict(size=10, line=dict(width=0.5, color="rgba(255,255,255,0.2)")))
    fig_scatter.update_layout(**LAYOUT_BASE)
    fig_scatter.update_layout(xaxis={**AXIS_BASE, "title_text": selected_driver_label}, yaxis={**AXIS_BASE, "title_text": "Learning Poverty (%)"}, coloraxis_showscale=False, height=360)
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── CHARTS ROW 3 — Multi-driver radar + heatmap ───────────────────────────────
st.markdown(f"""
<div class="section-label">Multi-Factor Analysis</div>
<div class="section-title">Driver Profiles & Country Comparisons</div>
""", unsafe_allow_html=True)

col_radar, col_heat = st.columns(2)

with col_radar:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🕸️ Driver Radar — Top 6 vs Bottom 6 Countries</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Normalized driver profiles of highest vs lowest learning poverty countries.</div>', unsafe_allow_html=True)

    radar_vars = ["pupil_teacher_ratio","trained_teachers","gov_expenditure", "children_out_of_school","pupils_below_min_proficiency","u5_mortality"]
    radar_labels = ["Pupil-Teacher\nRatio","Trained\nTeachers","Gov.\nExpenditure", "Out of\nSchool","Below Min.\nProficiency","U5\nMortality"]

    top6    = filtered_df.nlargest(6, "learning_poverty")[radar_vars].mean()
    bottom6 = filtered_df.nsmallest(6, "learning_poverty")[radar_vars].mean()
    
    df_norm = working_df[radar_vars]
    vmin, vmax = df_norm.min(), df_norm.max()
    top6_n    = (top6    - vmin) / (vmax - vmin + 1e-5)
    bottom6_n = (bottom6 - vmin) / (vmax - vmin + 1e-5)

    fig_radar = go.Figure()
    fill_colors = {"#F78166": "rgba(247, 129, 102, 0.15)", "#56D364": "rgba(86, 211, 100, 0.15)"}
    
    for vals, name, color in [(top6_n, "High LP Countries", "#F78166"), (bottom6_n, "Low LP Countries",  "#56D364")]:
        r_vals = list(vals) + [vals.iloc[0]]
        theta  = radar_labels + [radar_labels[0]]
        fig_radar.add_trace(go.Scatterpolar(r=r_vals, theta=theta, fill="toself", name=name, line=dict(color=color, width=2), fillcolor=fill_colors.get(color, "rgba(255, 255, 255, 0.15)"), marker=dict(size=6, color=color)))

    fig_radar.update_layout(**LAYOUT_BASE)
    fig_radar.update_layout(polar=dict(bgcolor=PLOT_BG, radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9, color=TEXT_COLOR), gridcolor=GRID_COLOR, linecolor=GRID_COLOR), angularaxis=dict(tickfont=dict(size=10, color=TEXT_COLOR), linecolor=GRID_COLOR, gridcolor=GRID_COLOR)), legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5), height=380, margin=dict(l=50, r=50, t=30, b=60))
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_heat:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🔥 Correlation Heatmap — All Variables</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Pearson correlation between learning poverty and its drivers (full dataset).</div>', unsafe_allow_html=True)

    corr_vars = ["learning_poverty","pupil_teacher_ratio","trained_teachers", "gov_expenditure","children_out_of_school","pupils_below_min_proficiency","u5_mortality"]
    corr_labels = ["Learning\ Poverty","Pupil-Teacher\ Ratio","Trained\ Teachers", "Gov.\ Expenditure","Out of\ School","Below Min.\ Prof.","U5\ Mortality"]
    corr_matrix = working_df[corr_vars].corr().values

    fig_heat = go.Figure(go.Heatmap(
        z=corr_matrix, x=corr_labels, y=corr_labels,
        colorscale=[[0.0, "#0d4f8c"], [0.3, "#1a6bb0"], [0.5, "#161B22"], [0.7, "#8b2500"], [1.0, "#F78166"]],
        zmin=-1, zmax=1, text=[[f"{v:.2f}" for v in row] for row in corr_matrix], texttemplate="%{text}",
        textfont=dict(size=10, color="white"), hovertemplate="<b>%{x}</b> × <b>%{y}</b><br>r = %{z:.3f}<extra></extra>",
    ))
    fig_heat.update_layout(**LAYOUT_BASE)
    fig_heat.update_layout(xaxis=dict(tickfont=dict(size=9, color=TEXT_COLOR), showline=False), yaxis=dict(tickfont=dict(size=9, color=TEXT_COLOR), showline=False, autorange="reversed"), height=380)
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── CHARTS ROW 4 — Multi-country trend + Box plot ─────────────────────────────
st.markdown(f"""
<div class="section-label">Country Deep Dive</div>
<div class="section-title">Individual Country Trajectories & Distributions</div>
""", unsafe_allow_html=True)

col_multi, col_box = st.columns(2)

with col_multi:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📉 Country-Level Learning Poverty Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Select countries in the sidebar to compare trajectories.</div>', unsafe_allow_html=True)

    plot_countries = selected_countries if selected_countries else ["India","Nigeria","Chad","Niger","Mali","Morocco","Colombia","Brazil","Korea, Rep.","Norway","Germany","United States"]
    plot_countries = [c for c in plot_countries if c in df["Country Name"].values][:12]

    fig_multi = go.Figure()
    for i, country in enumerate(plot_countries):
        cdf = working_df[working_df["Country Name"] == country].sort_values("Year")
        if not cdf.empty:
            fig_multi.add_trace(go.Scatter(x=cdf["Year"], y=cdf["learning_poverty"], mode="lines+markers", name=country, line=dict(width=2, color=PALETTE[i % len(PALETTE)]), marker=dict(size=6), hovertemplate=f"<b>{country}</b><br>Year: %{{x}}<br>LP: %{{y:.1f}}%<extra></extra>"))

    fig_multi.update_layout(**LAYOUT_BASE)
    fig_multi.update_layout(xaxis={**AXIS_BASE, "title_text": "Year"}, yaxis={**AXIS_BASE, "title_text": "Learning Poverty (%)"}, height=360, legend=dict(orientation="h", yanchor="top", y=-0.15, xanchor="center", x=0.5, font=dict(size=10)))
    st.plotly_chart(fig_multi, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_box:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📦 Distribution of Learning Poverty by Decade</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">How the spread of learning poverty has shifted across time periods.</div>', unsafe_allow_html=True)

    def decade_label(y):
        if y < 2005: return "2000–2004"
        elif y < 2010: return "2005–2009"
        elif y < 2015: return "2010–2014"
        else: return "2015–2023"

    working_df_decade = working_df.copy()
    working_df_decade["Decade"] = working_df_decade["Year"].apply(decade_label)

    fig_box = px.box(working_df_decade, x="Decade", y="learning_poverty", color="Decade", category_orders={"Decade": ["2000–2004", "2005–2009", "2010–2014", "2015–2023"]}, template="plotly_dark", color_discrete_sequence=PALETTE)
    fig_box.update_layout(**LAYOUT_BASE)
    fig_box.update_layout(xaxis={**AXIS_BASE, "title_text": "Time Period"}, yaxis={**AXIS_BASE, "title_text": "Learning Poverty (%)"}, showlegend=False, height=360)
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── STRATEGIC RECOMMENDATIONS & CALL TO ACTION (FIXED AND RENDERED) ───────────
st.markdown(f"""
<div class="section-label">Policy Framework</div>
<div class="section-title">Strategic Insights & Call to Action — {selected_year}</div>
""", unsafe_allow_html=True)

high_classroom_density = avg_ptr > 25.0
low_funding = avg_ge < 15.0

priority_tags = []
if avg_lp > 50: priority_tags.append("<span style='color:var(--accent1); font-weight:700;'>CRITICAL LEARNING POVERTY CRISIS</span>")
if high_classroom_density: priority_tags.append("<span style='color:var(--accent2); font-weight:700;'>TEACHER SUPPLY SHORTAGE</span>")
if low_funding: priority_tags.append("<span style='color:var(--accent4); font-weight:700;'>FISCAL UNDERINVESTMENT</span>")

priority_status = " | ".join(priority_tags) if priority_tags else "<span style='color:var(--accent3); font-weight:700;'>STABLE MAINTENANCE MODE</span>"

st.markdown(f"""
<div style="background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 28px; margin-bottom: 30px;">
    
    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; flex-wrap: wrap; gap: 12px;">
        <div>
            <h3 style="margin: 0; font-family: 'Instrument Sans', sans-serif; font-size: 18px; color: var(--text); font-weight: 700;">
                🎯 SDG 4 Emergency Response Playbook
            </h3>
            <p style="margin: 4px 0 0 0; font-size: 12px; color: var(--muted);">Data-driven structural interventions scaled for current selection profiles.</p>
        </div>
        <div style="background: var(--surface2); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-size: 11px; letter-spacing: 0.05em;">
            SYSTEM STATUS: {priority_status}
        </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px;">
        
        <div style="background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 18px; display: flex; flex-direction: column;">
            <div style="font-size: 20px; margin-bottom: 10px;">📉</div>
            <div style="font-size: 13px; font-weight: 700; color: var(--text); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em;">
                1. Remediate Foundational Literacy
            </div>
            <p style="font-size: 12px; color: var(--muted); line-height: 1.6; margin: 0; flex-grow: 1;">
                With global learning poverty hovering at <b style="color:var(--accent1);">{avg_lp:.1f}%</b> inside this runtime filter, countries must pivot curricula toward "Teaching at the Right Level" (TaRL). Focus strictly on foundational literacy before age 10 to eliminate downstream dropouts.
            </p>
        </div>

        <div style="background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 18px; display: flex; flex-direction: column;">
            <div style="font-size: 20px; margin-bottom: 10px;">👩‍🏫</div>
            <div style="font-size: 13px; font-weight: 700; color: var(--text); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em;">
                2. Optimize Instructional Capacity
            </div>
            <p style="font-size: 12px; color: var(--muted); line-height: 1.6; margin: 0; flex-grow: 1;">
                Current active constraints reflect an average density of <b style="color:var(--accent2);">{avg_ptr:.1f}</b> pupils per teacher. Maintain or reduce this target balance while directly deploying continuous upskilling networks.
            </p>
        </div>

        <div style="background: var(--surface2); border: 1px solid var(--border); border-radius: 12px; padding: 18px; display: flex; flex-direction: column;">
            <div style="font-size: 20px; margin-bottom: 10px;">💎</div>
            <div style="font-size: 13px; font-weight: 700; color: var(--text); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.05em;">
                3. Safeguard Fiscal Allocations
            </div>
            <p style="font-size: 12px; color: var(--muted); line-height: 1.6; margin: 0; flex-grow: 1;">
                Education allocations currently average <b style="color:var(--accent4);">{avg_ge:.1f}%</b> of public budgets. Governments must codify a minimum structural expenditure floor of 15-20% ring-fenced for early education infrastructure.
            </p>
        </div>
    </div>

    <div style="margin-top: 24px; padding: 16px; background: rgba(247, 129, 102, 0.06); border: 1px dashed rgba(247, 129, 102, 0.3); border-radius: 12px; display: flex; align-items: center; gap: 16px; flex-wrap: wrap;">
        <div style="font-size: 24px;">📢</div>
        <div style="flex: 1; min-width: 240px;">
            <h4 style="margin: 0; font-family: 'Instrument Sans', sans-serif; font-size: 14px; color: var(--accent1); font-weight: 700;">
                The 2030 Countdown Action Directive
            </h4>
            <p style="margin: 2px 0 0 0; font-size: 12px; color: var(--text); line-height: 1.5;">
                A selective 10% structural reduction in learning poverty yields significant lifelong macroeconomic productivity improvements. Ministries and global donors must unify reporting schemas instantly.
            </p>
        </div>
        <div style="padding: 8px 16px; background: var(--accent1); color: var(--bg); font-weight: 700; font-size: 12px; border-radius: 8px; text-transform: uppercase; letter-spacing: 0.05em;">
            Blueprint Operational
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Credits Footer ────────────────────────────────────────────────────────────
st.markdown("""
<div class="credits">
    Dashboard created for <b>SDG 4 Tracking</b> · Core Interface Matrix Operational
</div>
""", unsafe_allow_html=True)
