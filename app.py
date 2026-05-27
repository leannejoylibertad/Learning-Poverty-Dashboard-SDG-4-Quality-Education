import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Learning Poverty Dashboard | SDG 4",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:wght@400;500;600;700;800&display=swap');
:root {
    --bg:#0D1117; --surface:#161B22; --surface2:#1C2333; --border:#30363D;
    --accent1:#F78166; --accent2:#79C0FF; --accent3:#56D364; --accent4:#E3B341;
    --text:#E6EDF3; --muted:#8B949E;
    --grad1:linear-gradient(135deg,#F78166 0%,#FF9580 100%);
    --grad2:linear-gradient(135deg,#79C0FF 0%,#58A6FF 100%);
    --grad3:linear-gradient(135deg,#56D364 0%,#3FB950 100%);
    --grad4:linear-gradient(135deg,#E3B341 0%,#D29922 100%);
}
html,body,[class*="css"]{font-family:'Instrument Sans',sans-serif!important;background-color:var(--bg)!important;color:var(--text)!important;}
.main .block-container{padding:1.5rem 2rem 3rem 2rem;max-width:1400px;}
section[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border)!important;}
section[data-testid="stSidebar"] *{color:var(--text)!important;}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label,
section[data-testid="stSidebar"] .stSlider label{font-family:'Instrument Sans',sans-serif!important;font-size:13px!important;font-weight:600!important;letter-spacing:.07em!important;text-transform:uppercase!important;color:var(--muted)!important;}
.section-label{font-family:'Instrument Sans',sans-serif;font-size:11px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;}
.section-title{font-family:'Instrument Sans',sans-serif;font-size:24px;font-weight:700;color:var(--text);margin-bottom:20px;}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1rem;}
@media(max-width:900px){.kpi-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:500px){.kpi-grid{grid-template-columns:1fr;}}
.kpi-card{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:22px 20px;position:relative;overflow:hidden;transition:border-color .2s ease,transform .2s ease;box-sizing:border-box;min-height:175px;height:100%;display:flex;flex-direction:column;justify-content:space-between;}
.kpi-card:hover{border-color:rgba(247,129,102,0.4);transform:translateY(-2px);}
.kpi-card::before{content:'';position:absolute;top:0;left:0;right:0;height:4px;}
.kpi-red::before{background:var(--grad1);} .kpi-blue::before{background:var(--grad2);}
.kpi-green::before{background:var(--grad3);} .kpi-yellow::before{background:var(--grad4);}
.kpi-icon{font-size:26px;margin-bottom:8px;display:block;}
.kpi-label{font-size:11px;font-weight:600;letter-spacing:.10em;text-transform:uppercase;color:var(--muted);margin-bottom:6px;line-height:1.3;}
.kpi-value{font-family:'Instrument Sans',sans-serif;font-size:34px;font-weight:800;line-height:1.1;margin-bottom:8px;}
.kpi-red .kpi-value{color:var(--accent1);} .kpi-blue .kpi-value{color:var(--accent2);}
.kpi-green .kpi-value{color:var(--accent3);} .kpi-yellow .kpi-value{color:var(--accent4);}
.kpi-sub{font-size:11.5px;color:var(--muted);line-height:1.4;margin-top:auto;}
.stat-grid-container{display:grid;grid-template-columns:repeat(6,minmax(150px,1fr));gap:12px;width:100%;margin-bottom:20px;}
@media(max-width:1200px){.stat-grid-container{grid-template-columns:repeat(3,1fr);}}
@media(max-width:768px){.stat-grid-container{grid-template-columns:repeat(2,1fr);}}
.stat-pill{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:12px 16px;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;min-height:90px;}
.stat-pill-label{font-size:10px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin-bottom:4px;}
.stat-pill-value{font-family:'Instrument Sans',sans-serif;font-size:16px;font-weight:700;color:var(--text);}
.stat-pill-country{font-size:11px;color:var(--muted);margin-top:2px;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.chart-box{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:20px;margin-bottom:20px;}
.chart-title{font-family:'Instrument Sans',sans-serif;font-size:16px;font-weight:700;color:var(--text);margin-bottom:4px;}
.chart-desc{font-size:12px;color:var(--muted);margin-bottom:16px;}
.fancy-divider{border:none;height:1px;background:linear-gradient(90deg,transparent,var(--border),var(--accent1),var(--border),transparent);margin:32px 0;opacity:.6;}
.credits{text-align:center;padding:16px;font-size:12px;color:var(--muted);border-top:1px solid var(--border);margin-top:40px;}
.credits b{color:var(--accent2);}
.sb-info{background:var(--surface2);border:1px solid var(--border);border-radius:12px;padding:14px 16px;margin-bottom:16px;font-size:12px;color:var(--muted);line-height:1.7;}
.sb-info b{color:var(--text);}
::-webkit-scrollbar{width:6px;height:6px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:var(--muted);}
.insight-panel{background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:28px;margin-bottom:24px;}
.insight-headline{font-size:22px;font-weight:800;line-height:1.3;margin-bottom:6px;}
.insight-subline{font-size:13px;color:var(--muted);margin-bottom:24px;line-height:1.6;}
.insight-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-bottom:24px;}
.insight-card{border-radius:12px;padding:18px 20px;border-left:4px solid;}
.insight-card.red{background:rgba(247,129,102,0.08);border-color:#F78166;}
.insight-card.blue{background:rgba(121,192,255,0.08);border-color:#79C0FF;}
.insight-card.yellow{background:rgba(227,179,65,0.08);border-color:#E3B341;}
.insight-card.green{background:rgba(86,211,100,0.08);border-color:#56D364;}
.insight-card.purple{background:rgba(188,140,255,0.08);border-color:#BC8CFF;}
.insight-card-title{font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:8px;}
.insight-card.red .insight-card-title{color:#F78166;}
.insight-card.blue .insight-card-title{color:#79C0FF;}
.insight-card.yellow .insight-card-title{color:#E3B341;}
.insight-card.green .insight-card-title{color:#56D364;}
.insight-card.purple .insight-card-title{color:#BC8CFF;}
.insight-card-stat{font-size:28px;font-weight:800;color:var(--text);margin-bottom:6px;line-height:1.1;}
.insight-card-body{font-size:12.5px;color:var(--muted);line-height:1.6;}
.insight-card-body b{color:var(--text);}
.action-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin-top:20px;}
.action-item{background:var(--surface2);border:1px solid var(--border);border-radius:10px;padding:14px 16px;display:flex;align-items:flex-start;gap:12px;}
.action-icon{font-size:20px;margin-top:2px;flex-shrink:0;}
.action-text{font-size:12.5px;color:var(--muted);line-height:1.6;}
.action-text b{color:var(--text);display:block;font-size:13px;margin-bottom:2px;}
.urgency-bar{height:8px;border-radius:4px;background:var(--border);margin:8px 0;overflow:hidden;}
.urgency-fill{height:100%;border-radius:4px;}
.urgency-fill.red{background:linear-gradient(90deg,#E3B341,#F78166,#7a0f00);}
.proxy-box{background:rgba(188,140,255,0.06);border:1px solid rgba(188,140,255,0.25);border-radius:14px;padding:20px 24px;margin-top:20px;}
.proxy-box-title{font-size:13px;font-weight:700;color:#BC8CFF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:10px;}
.proxy-box-body{font-size:12.5px;color:var(--muted);line-height:1.8;}
.proxy-box-body b{color:var(--text);}
.proxy-tags{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px;}
.proxy-tag{background:rgba(188,140,255,0.12);border:1px solid rgba(188,140,255,0.3);border-radius:20px;padding:4px 12px;font-size:11px;color:#BC8CFF;font-weight:600;}
</style>
""", unsafe_allow_html=True)

# ── Plotly Theme ──────────────────────────────────────────────────────────────
PLOT_BG     = "#161B22"
PAPER_BG    = "#161B22"
GRID_COLOR  = "#21262D"
TEXT_COLOR  = "#8B949E"
FONT_FAMILY = "Instrument Sans, sans-serif"
PALETTE     = ["#F78166","#79C0FF","#56D364","#E3B341","#BC8CFF","#FF7B72","#58A6FF","#3FB950","#D29922"]

LAYOUT_BASE = dict(
    paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
    font=dict(family=FONT_FAMILY, color=TEXT_COLOR, size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    colorway=PALETTE,
    legend=dict(bgcolor="rgba(22,27,34,0.9)", bordercolor="#30363D", borderwidth=1,
                font=dict(size=11, color="#C9D1D9")),
)
AXIS_BASE = dict(
    showgrid=True, gridcolor=GRID_COLOR, gridwidth=1,
    linecolor="#30363D", linewidth=1,
    tickfont=dict(size=11, color=TEXT_COLOR),
    title_font=dict(size=12, color=TEXT_COLOR),
    zeroline=False,
)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("cleaned_dataset.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()
year_min, year_max = int(df["Year"].min()), int(df["Year"].max())

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='font-family:"Instrument Sans",sans-serif;font-size:20px;font-weight:800;color:#F78166;margin-bottom:4px;'>📚 SDG 4 Explorer</div>
    <div style='font-size:12px;color:#8B949E;margin-bottom:20px;line-height:1.6;'>Quality Education · Learning Poverty</div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    all_countries = sorted(df["Country Name"].unique())
    selected_countries = st.multiselect(
        "Filter Countries", options=all_countries, default=[],
        placeholder="All countries",
        help="Leave empty to include all countries"
    )

    st.markdown("---")

    driver_options = {
        "Pupil-Teacher Ratio"               : "pupil_teacher_ratio",
        "Trained Teachers (%)"              : "trained_teachers",
        "Gov. Education Expenditure (%)"    : "gov_expenditure",
        "Children Out of School (%)"        : "children_out_of_school",
        "Pupils Below Min. Proficiency (%)" : "pupils_below_min_proficiency",
        "Under-5 Mortality Rate"            : "u5_mortality",
    }
    selected_driver_label = st.selectbox(
        "Driver to Explore", list(driver_options.keys()), index=0,
        help="Driver vs Learning Poverty scatter plot"
    )
    selected_driver = driver_options[selected_driver_label]

    st.markdown("---")
    st.markdown("""
    <div class='sb-info'>
        <b>Response Variable</b><br>
        Learning Poverty — share of children unable to read a simple text by age 10.<br><br>
        <b>Model Used</b><br>
        Huber Robust Regression (statsmodels RLM)<br><br>
        <b>Significant Predictors</b><br>
        ✅ u5_mortality (β = +22.74)<br>
        ✅ gov_expenditure (β = −3.64)<br>
        ✅ trained_teachers (β = −2.82)<br>
        ✗ pupil_teacher_ratio (not significant)<br><br>
        <b>Data Coverage</b><br>
        75 countries · 2000–2023 (no 2021)
    </div>
    """, unsafe_allow_html=True)

# ── Header Banner ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div style='background:var(--surface);border:1px solid var(--border);padding:26px;border-radius:16px;margin-bottom:10px;'>
    <span style='font-size:10px;font-weight:800;color:var(--accent1);letter-spacing:.2em;'>UN SUSTAINABLE DEVELOPMENT GOAL 4</span>
    <h1 style='margin:4px 0 0 0;color:var(--text);font-weight:800;font-size:30px;'>Drivers of Learning Poverty</h1>
    <div style='font-size:13px;color:#8B949E;margin-top:6px;'>
        Huber Robust Regression Analysis · 75 Countries · 2000–2023 ·
        Response: <b style='color:#F78166'>learning_poverty</b>
    </div>
</div>
""", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── Year Slider ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-label">Spatial Distribution</div>
<div class="section-title">Global Analysis Engine Profile Matrix</div>
<div style="font-size:13.5px;color:#8B949E;line-height:1.8;margin-top:-12px;margin-bottom:20px;max-width:820px;">This dashboard tracks <b style="color:#E6EDF3;">learning poverty</b> — the share of children unable to read a simple text by age 10 — across 75 countries from 2000 to 2023. Use the year slider below to explore how key education indicators shift over time, and every chart, map, and metric on this page updates in sync.</div>
""", unsafe_allow_html=True)

selected_year = st.slider(
    "📅 Select Target Analytical Year", year_min, year_max, 2019,
    key="choro_year",
    help="Move this controller to update maps, metrics, indicators and regression charts across the environment."
)

# ── Filter Data ───────────────────────────────────────────────────────────────
working_df = df.copy()
if selected_countries:
    working_df = working_df[working_df["Country Name"].isin(selected_countries)]

filtered_df = working_df[working_df["Year"] == selected_year].copy()

if filtered_df.empty:
    st.warning(f"No data for year {selected_year} with the current country filter. Try year 2019 or 2015.")
    st.stop()

# ── KPI Row ───────────────────────────────────────────────────────────────────
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

st.markdown(
f'<div class="kpi-grid">'
f'<div class="kpi-card kpi-red"><div><span class="kpi-icon">📖</span><div class="kpi-label">Avg. Learning Poverty</div><div class="kpi-value">{avg_lp:.1f}%</div></div><div class="kpi-sub">Share of children below reading proficiency</div></div>'
f'<div class="kpi-card kpi-blue"><div><span class="kpi-icon">🏫</span><div class="kpi-label">Avg. Pupils per Teacher</div><div class="kpi-value">{avg_ptr:.1f}</div></div><div class="kpi-sub">Average pupil-to-teacher ratio, primary</div></div>'
f'<div class="kpi-card kpi-green"><div><span class="kpi-icon">🎓</span><div class="kpi-label">Avg. Trained Teachers</div><div class="kpi-value">{avg_tt:.1f}%</div></div><div class="kpi-sub">Teachers meeting national training standards</div></div>'
f'<div class="kpi-card kpi-yellow"><div><span class="kpi-icon">💰</span><div class="kpi-label">Avg. Gov. Expenditure</div><div class="kpi-value">{avg_ge:.1f}%</div></div><div class="kpi-sub">Govt. expenditure per student (% GDP per capita)</div></div>'
f'</div>', unsafe_allow_html=True
)

st.markdown("<br>", unsafe_allow_html=True)

# ── Stat Pills ─────────────────────────────────────────────────────────────────
n_countries = len(filtered_df)
avg_oos = filtered_df["children_out_of_school"].mean()
avg_u5  = filtered_df["u5_mortality"].mean()
avg_bmp = filtered_df["pupils_below_min_proficiency"].mean()

st.markdown(f"""
<div class="stat-grid-container">
    <div class="stat-pill"><div class="stat-pill-label">🔴 Highest LP</div><div class="stat-pill-value">{worst_v:.1f}%</div><div class="stat-pill-country">{worst}</div></div>
    <div class="stat-pill"><div class="stat-pill-label">🟢 Lowest LP</div><div class="stat-pill-value">{best_v:.1f}%</div><div class="stat-pill-country">{best}</div></div>
    <div class="stat-pill"><div class="stat-pill-label">🧒 Out of School</div><div class="stat-pill-value">{avg_oos:.1f}%</div><div class="stat-pill-country">Avg. children not enrolled</div></div>
    <div class="stat-pill"><div class="stat-pill-label">🏥 U5 Mortality</div><div class="stat-pill-value">{avg_u5:.1f}</div><div class="stat-pill-country">Avg. deaths per 1k births</div></div>
    <div class="stat-pill"><div class="stat-pill-label">📉 Below Min. Prof.</div><div class="stat-pill-value">{avg_bmp:.1f}%</div><div class="stat-pill-country">Avg. pupils below minimum</div></div>
    <div class="stat-pill"><div class="stat-pill-label">🌍 Countries</div><div class="stat-pill-value">{n_countries}</div><div class="stat-pill-country">In filtered dataset</div></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── ROW 1: Choropleth + Bar ───────────────────────────────────────────────────
col_map, col_bar = st.columns([3, 2])

with col_map:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title">🗺️ Global Learning Poverty Map — {selected_year}</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Darker shades = higher share of children below reading proficiency. Gray = no data for that year.</div>', unsafe_allow_html=True)
    fig_map = px.choropleth(
        filtered_df, locations="Country Code", color="learning_poverty",
        hover_name="Country Name",
        hover_data={"learning_poverty":":.1f","pupil_teacher_ratio":":.1f","trained_teachers":":.1f","Country Code":False},
        color_continuous_scale=[[0,"#1a3a2a"],[0.25,"#2d6a4f"],[0.5,"#E3B341"],[0.75,"#F78166"],[1.0,"#7a0f00"]],
        range_color=[0,100], labels={"learning_poverty":"Learning Poverty (%)"},
    )
    fig_map.update_layout(**LAYOUT_BASE)
    fig_map.update_layout(
        margin=dict(l=0,r=0,t=0,b=0), height=380,
        geo=dict(showframe=False,showcoastlines=True,coastlinecolor="#30363D",
                 showland=True,landcolor="#1C2333",showocean=True,oceancolor="#0D1117",
                 showlakes=False,bgcolor=PLOT_BG,projection_type="natural earth"),
    )
    st.plotly_chart(fig_map, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_bar:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📊 Top 15 Countries by Learning Poverty</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-desc">Highest LP rates in {selected_year}.</div>', unsafe_allow_html=True)
    if not filtered_df.empty:
        top15 = filtered_df.nlargest(15,"learning_poverty").sort_values("learning_poverty")
        colors_bar = ["#7a0f00" if v>=80 else "#F78166" if v>=60 else "#E3B341" if v>=40 else "#56D364" for v in top15["learning_poverty"]]
        fig_bar_chart = go.Figure(go.Bar(
            x=top15["learning_poverty"], y=top15["Country Name"], orientation="h",
            marker_color=colors_bar,
            text=[f"{v:.1f}%" for v in top15["learning_poverty"]],
            textposition="outside", textfont=dict(size=11,color=TEXT_COLOR),
            hovertemplate="<b>%{y}</b><br>Learning Poverty: %{x:.1f}%<extra></extra>",
        ))
        fig_bar_chart.update_layout(**LAYOUT_BASE)
        fig_bar_chart.update_layout(
            xaxis={**AXIS_BASE,"title_text":"Learning Poverty (%)","range":[0,115]},
            yaxis={**AXIS_BASE,"title_text":"","showgrid":False}, height=380
        )
        st.plotly_chart(fig_bar_chart, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── ROW 2: Trend + Driver Scatter ─────────────────────────────────────────────
st.markdown("""
<div class="section-label">Trends & Drivers</div>
<div class="section-title">How Learning Poverty Evolves & What Shapes It</div>
""", unsafe_allow_html=True)

col_trend, col_scatter = st.columns(2)

with col_trend:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📈 Learning Poverty Trend Over Time</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Global average trend with individual country lines in the background.</div>', unsafe_allow_html=True)
    trend_data = working_df.groupby("Year")["learning_poverty"].agg(["mean","min","max"]).reset_index()
    fig_trend  = go.Figure()
    countries_to_plot = selected_countries if selected_countries else all_countries[:25]
    for country in countries_to_plot[:20]:
        cdf = working_df[working_df["Country Name"]==country].sort_values("Year")
        if len(cdf) >= 3:
            fig_trend.add_trace(go.Scatter(x=cdf["Year"],y=cdf["learning_poverty"],mode="lines",
                line=dict(width=1,color="rgba(255,255,255,0.08)"),showlegend=False,hoverinfo="skip"))
    fig_trend.add_trace(go.Scatter(
        x=pd.concat([trend_data["Year"],trend_data["Year"][::-1]]),
        y=pd.concat([trend_data["max"],trend_data["min"][::-1]]),
        fill="toself",fillcolor="rgba(247,129,102,0.08)",
        line=dict(color="rgba(0,0,0,0)"),showlegend=False,hoverinfo="skip"))
    fig_trend.add_trace(go.Scatter(
        x=trend_data["Year"],y=trend_data["mean"],mode="lines+markers",
        name="Global Average",line=dict(color="#F78166",width=3),marker=dict(size=7,color="#F78166"),
        hovertemplate="<b>%{x}</b><br>Avg LP: %{y:.1f}%<extra></extra>"))
    fig_trend.add_vline(x=selected_year,line_dash="dash",line_color="#79C0FF",line_width=1.5,
        annotation_text=f"  {selected_year}",annotation_font=dict(color="#79C0FF",size=11))
    fig_trend.update_layout(**LAYOUT_BASE)
    fig_trend.update_layout(
        xaxis={**AXIS_BASE,"title_text":"Year"},
        yaxis={**AXIS_BASE,"title_text":"Learning Poverty (%)"},height=360)
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_scatter:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-title">🔍 Learning Poverty vs. {selected_driver_label}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-desc">Each dot = one country in {selected_year}. OLS trendline overlaid.</div>', unsafe_allow_html=True)
    if not filtered_df.empty and selected_driver in filtered_df.columns:
        scatter_df = filtered_df.dropna(subset=[selected_driver,"learning_poverty"])
        if len(scatter_df) >= 3:
            fig_scatter = px.scatter(
                scatter_df, x=selected_driver, y="learning_poverty",
                color="learning_poverty", hover_name="Country Name",
                hover_data={selected_driver:":.2f","learning_poverty":":.1f","Country Code":False},
                color_continuous_scale=[[0,"#56D364"],[0.5,"#E3B341"],[1,"#F78166"]],
                range_color=[0,100], trendline="ols", trendline_color_override="#79C0FF",
                labels={selected_driver:selected_driver_label,"learning_poverty":"Learning Poverty (%)"}
            )
            fig_scatter.update_traces(selector=dict(mode="markers"),
                marker=dict(size=10,line=dict(width=0.5,color="rgba(255,255,255,0.2)")))
            fig_scatter.update_layout(**LAYOUT_BASE)
            fig_scatter.update_layout(
                xaxis={**AXIS_BASE,"title_text":selected_driver_label},
                yaxis={**AXIS_BASE,"title_text":"Learning Poverty (%)"},
                coloraxis_showscale=False,height=360)
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info(f"Not enough data points for {selected_year}.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── ROW 3: Radar + U5 MORTALITY SCATTER ───────────────────────────────────────
st.markdown("""
<div class="section-label">Multi-Factor Analysis</div>
<div class="section-title">Driver Profiles & Strongest Regression Signal</div>
""", unsafe_allow_html=True)

col_radar, col_u5 = st.columns(2)

with col_radar:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🕸️ Driver Radar — Top 6 vs Bottom 6 Countries</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Normalized driver profiles of highest vs lowest LP countries.</div>', unsafe_allow_html=True)
    radar_vars   = ["pupil_teacher_ratio","trained_teachers","gov_expenditure",
                    "children_out_of_school","pupils_below_min_proficiency","u5_mortality"]
    radar_labels = ["Pupil-Teacher\nRatio","Trained\nTeachers","Gov.\nExpenditure",
                    "Out of\nSchool","Below Min.\nProficiency","U5\nMortality"]
    if len(filtered_df) >= 6:
        top6    = filtered_df.nlargest(6,"learning_poverty")[radar_vars].mean()
        bottom6 = filtered_df.nsmallest(6,"learning_poverty")[radar_vars].mean()
        df_norm = working_df[radar_vars]
        vmin, vmax = df_norm.min(), df_norm.max()
        top6_n    = (top6    - vmin) / (vmax - vmin + 1e-5)
        bottom6_n = (bottom6 - vmin) / (vmax - vmin + 1e-5)
        fig_radar = go.Figure()
        for vals, name, color, fcolor in [
            (top6_n,    "High LP Countries","#F78166","rgba(247,129,102,0.15)"),
            (bottom6_n, "Low LP Countries", "#56D364","rgba(86,211,100,0.15)")
        ]:
            r_vals = list(vals) + [vals.iloc[0]]
            theta  = radar_labels + [radar_labels[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=r_vals, theta=theta, fill="toself", name=name,
                line=dict(color=color,width=2), fillcolor=fcolor, marker=dict(size=6,color=color)))
        fig_radar.update_layout(**LAYOUT_BASE)
        fig_radar.update_layout(
            polar=dict(
                bgcolor=PLOT_BG,
                radialaxis=dict(visible=True,range=[0,1],tickfont=dict(size=9,color=TEXT_COLOR),
                                gridcolor=GRID_COLOR,linecolor=GRID_COLOR),
                angularaxis=dict(tickfont=dict(size=10,color=TEXT_COLOR),
                                 linecolor=GRID_COLOR,gridcolor=GRID_COLOR)),
            legend=dict(orientation="h",yanchor="bottom",y=-0.15,xanchor="center",x=0.5),
            height=380, margin=dict(l=50,r=50,t=30,b=60))
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Need at least 6 countries for radar chart.")
    st.markdown('</div>', unsafe_allow_html=True)

# ── U5 Mortality vs Learning Poverty scatter ──────────────────────────────────
with col_u5:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">🏥 Learning Poverty vs. Under-5 Mortality — Strongest Driver</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="chart-desc">'
        f'Under-5 mortality is the <b style="color:#BC8CFF">most influential predictor</b> in the Huber regression '
        f'(β = +22.74, p &lt; 0.001). It acts as a <b style="color:#BC8CFF">composite proxy</b> for poverty, '
        f'malnutrition, weak institutions, and poor health infrastructure — all conditions that also crush '
        f'children\'s ability to learn. Each dot = one country in {selected_year}.'
        f'</div>', unsafe_allow_html=True
    )
    u5_scatter_df = filtered_df.dropna(subset=["u5_mortality","learning_poverty"])
    if len(u5_scatter_df) >= 3:
        fig_u5 = px.scatter(
            u5_scatter_df,
            x="u5_mortality",
            y="learning_poverty",
            color="learning_poverty",
            hover_name="Country Name",
            hover_data={
                "u5_mortality"      : ":.1f",
                "learning_poverty"  : ":.1f",
                "trained_teachers"  : ":.1f",
                "gov_expenditure"   : ":.1f",
                "Country Code"      : False,
            },
            color_continuous_scale=[[0,"#56D364"],[0.5,"#E3B341"],[1,"#F78166"]],
            range_color=[0,100],
            trendline="ols",
            trendline_color_override="#BC8CFF",
            size_max=14,
            labels={
                "u5_mortality"    : "Under-5 Mortality Rate (per 1,000 live births)",
                "learning_poverty": "Learning Poverty (%)"
            }
        )
        fig_u5.update_traces(
            selector=dict(mode="markers"),
            marker=dict(size=10, line=dict(width=0.5, color="rgba(255,255,255,0.2)"))
        )
        fig_u5.update_layout(**LAYOUT_BASE)
        fig_u5.update_layout(
            xaxis={**AXIS_BASE, "title_text": "Under-5 Mortality Rate (per 1,000 live births)"},
            yaxis={**AXIS_BASE, "title_text": "Learning Poverty (%)"},
            coloraxis_showscale=False,
            height=380,
            annotations=[dict(
                x=0.98, y=0.04, xref="paper", yref="paper",
                text="<b>β = +22.74</b> · p < 0.001 · Huber RLM",
                showarrow=False,
                font=dict(size=11, color="#BC8CFF"),
                bgcolor="rgba(28,35,51,0.85)",
                bordercolor="#BC8CFF",
                borderwidth=1,
                borderpad=6,
                align="right"
            )]
        )
        st.plotly_chart(fig_u5, use_container_width=True)
    else:
        st.info("Not enough data points for this year.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── ROW 4: Country Trends + Box Plot ─────────────────────────────────────────
st.markdown("""
<div class="section-label">Country Deep Dive</div>
<div class="section-title">Individual Trajectories & Distributions Over Time</div>
""", unsafe_allow_html=True)

col_multi, col_box = st.columns(2)

with col_multi:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📉 Country-Level Learning Poverty Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">Select countries in the sidebar to compare trajectories.</div>', unsafe_allow_html=True)
    default_countries = ["India","Nigeria","Chad","Niger","Mali","Morocco","Colombia",
                         "Brazil","Korea, Rep.","Norway","Germany","United States"]
    plot_countries = selected_countries if selected_countries else default_countries
    plot_countries = [c for c in plot_countries if c in df["Country Name"].values][:12]
    fig_multi = go.Figure()
    for i, country in enumerate(plot_countries):
        cdf = working_df[working_df["Country Name"]==country].sort_values("Year")
        if not cdf.empty:
            fig_multi.add_trace(go.Scatter(
                x=cdf["Year"], y=cdf["learning_poverty"], mode="lines+markers",
                name=country, line=dict(width=2,color=PALETTE[i%len(PALETTE)]),
                marker=dict(size=6),
                hovertemplate=f"<b>{country}</b><br>Year: %{{x}}<br>LP: %{{y:.1f}}%<extra></extra>"))
    fig_multi.update_layout(**LAYOUT_BASE)
    fig_multi.update_layout(
        xaxis={**AXIS_BASE,"title_text":"Year"},
        yaxis={**AXIS_BASE,"title_text":"Learning Poverty (%)"},
        height=360,
        legend=dict(orientation="h",yanchor="top",y=-0.15,xanchor="center",x=0.5,font=dict(size=10)))
    st.plotly_chart(fig_multi, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_box:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    st.markdown('<div class="chart-title">📦 Distribution of Learning Poverty by Period</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-desc">How the spread of learning poverty has shifted across time periods.</div>', unsafe_allow_html=True)
    
    # Create periods for the box plot
    df_box = working_df.copy()
    df_box = df_box.dropna(subset=['learning_poverty'])
    
    if not df_box.empty:
        # Group years into periods
        bins = [1999, 2005, 2010, 2015, 2024]
        labels = ["2000-2005", "2006-2010", "2011-2015", "2016-2023"]
        df_box['Period'] = pd.cut(df_box['Year'], bins=bins, labels=labels)
        
        fig_box = px.box(
            df_box, x="Period", y="learning_poverty", 
            color="Period",
            color_discrete_sequence=["#79C0FF", "#56D364", "#E3B341", "#F78166"],
            labels={"learning_poverty": "Learning Poverty (%)"}
        )
        fig_box.update_layout(**LAYOUT_BASE)
        fig_box.update_layout(
            xaxis={**AXIS_BASE, "title_text": "Time Period"},
            yaxis={**AXIS_BASE, "title_text": "Learning Poverty (%)"},
            showlegend=False,
            height=360
        )
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.info("Not enough data to display distributions.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<hr class="fancy-divider">', unsafe_allow_html=True)

# ── Footer / Credits ──────────────────────────────────────────────────────────
st.markdown('''
<div class="credits">
    Dashboard developed for <b>SDG 4: Quality Education</b> analysis.<br>
    Data sourced from World Bank EdStats & Global Education Indicators.<br>
    Built with <b>Streamlit</b> and <b>Plotly</b>.
</div>
''', unsafe_allow_html=True)
