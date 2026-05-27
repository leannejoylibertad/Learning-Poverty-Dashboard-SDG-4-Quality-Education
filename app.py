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

# ─── PREMIUM CUSTOM CSS ─────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Google Fonts ────────────────────────────────────────── */
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,400&family=DM+Mono:wght@400;500&display=swap');

  /* ── Design Tokens ───────────────────────────────────────── */
  :root {
    --brand-900: #062518;
    --brand-800: #0a3d2e;
    --brand-700: #0e5238;
    --brand-600: #1a6b4a;
    --brand-500: #27906a;
    --brand-400: #38b589;
    --brand-300: #5ecfa7;
    --brand-200: #99e6cc;
    --brand-100: #d1f7ec;
    --brand-50:  #f0fdf8;

    --accent-red:    #e63946;
    --accent-amber:  #f4a261;
    --accent-teal:   #2a9d8f;
    --accent-blue:   #457b9d;
    --accent-purple: #6a4c93;
    --accent-lime:   #57cc99;

    --surface-0:  #ffffff;
    --surface-1:  #f7f9fc;
    --surface-2:  #eef2f7;
    --surface-3:  #e2e8f0;
    --surface-4:  #cbd5e1;

    --text-primary:   #0f1923;
    --text-secondary: #3d5068;
    --text-tertiary:  #7089a8;
    --text-muted:     #9fb3c8;

    --border-subtle:  rgba(15,25,35,.07);
    --border-default: rgba(15,25,35,.12);
    --border-strong:  rgba(15,25,35,.22);

    --shadow-xs: 0 1px 2px rgba(15,25,35,.04);
    --shadow-sm: 0 2px 8px rgba(15,25,35,.06), 0 1px 2px rgba(15,25,35,.04);
    --shadow-md: 0 4px 16px rgba(15,25,35,.08), 0 2px 4px rgba(15,25,35,.05);
    --shadow-lg: 0 8px 32px rgba(15,25,35,.12), 0 4px 8px rgba(15,25,35,.06);
    --shadow-xl: 0 16px 48px rgba(15,25,35,.16), 0 6px 12px rgba(15,25,35,.08);

    --radius-sm:  6px;
    --radius-md:  10px;
    --radius-lg:  16px;
    --radius-xl:  22px;
    --radius-2xl: 30px;

    --font-display: 'Syne', 'Segoe UI', system-ui, sans-serif;
    --font-body:    'DM Sans', 'Segoe UI', system-ui, sans-serif;
    --font-mono:    'DM Mono', 'Cascadia Code', 'Consolas', monospace;

    --sidebar-bg:   #071f16;
    --sidebar-w:    300px;
  }

  /* ── Global Reset ─────────────────────────────────────────── */
  html, body, [class*="css"] {
    font-family: var(--font-body) !important;
    color: var(--text-primary);
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }

  #MainMenu { visibility: hidden; }
  footer    { visibility: hidden; }
  header    { visibility: hidden; }

  /* ── Main layout padding ──────────────────────────────────── */
  .main .block-container {
    padding: 1.5rem 2rem 3rem !important;
    max-width: 1480px !important;
  }

  /* ══════════════════════════════════════════════════════════
     HERO BANNER
  ══════════════════════════════════════════════════════════ */
  .hero {
    background:
      radial-gradient(ellipse 80% 60% at 10% 110%, rgba(56,181,137,.22) 0%, transparent 60%),
      radial-gradient(ellipse 60% 80% at 90% -10%, rgba(26,107,74,.35) 0%, transparent 55%),
      linear-gradient(145deg, #062518 0%, #0a3d2e 40%, #0e5238 70%, #113a2c 100%);
    border-radius: var(--radius-xl);
    padding: 44px 48px 36px;
    margin-bottom: 28px;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-xl);
    border: 1px solid rgba(255,255,255,.06);
  }
  .hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
      radial-gradient(circle at 70% 50%, rgba(56,181,137,.08) 0%, transparent 50%),
      url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    pointer-events: none;
  }
  .hero-eyebrow {
    font-family: var(--font-body);
    font-size: .7rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: var(--brand-300);
    margin-bottom: 10px;
    opacity: .9;
  }
  .hero h1 {
    font-family: var(--font-display) !important;
    font-size: 2.6rem !important;
    font-weight: 800 !important;
    color: #ffffff !important;
    margin: 0 0 10px !important;
    letter-spacing: -1px;
    line-height: 1.1 !important;
  }
  .hero .sub {
    font-size: 1rem;
    opacity: .78;
    margin: 0 0 22px;
    line-height: 1.65;
    font-weight: 400;
    max-width: 680px;
    color: rgba(255,255,255,.8);
  }
  .hero .badges {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
  .badge {
    background: rgba(255,255,255,.1);
    border: 1px solid rgba(255,255,255,.18);
    backdrop-filter: blur(10px);
    border-radius: 100px;
    padding: 5px 14px;
    font-size: .72rem;
    font-weight: 600;
    color: rgba(255,255,255,.9);
    letter-spacing: .3px;
    transition: background .15s;
  }
  .badge:hover {
    background: rgba(255,255,255,.16);
  }

  /* ══════════════════════════════════════════════════════════
     SIDEBAR — COMPLETE REDESIGN
  ══════════════════════════════════════════════════════════ */
  [data-testid="stSidebar"] {
    background: var(--sidebar-bg) !important;
    border-right: 1px solid rgba(255,255,255,.06) !important;
    box-shadow: 2px 0 24px rgba(0,0,0,.3) !important;
  }
  [data-testid="stSidebar"] > div {
    padding: 0 !important;
  }
  [data-testid="stSidebar"] .block-container {
    padding: 0 !important;
  }

  /* Sidebar inner scroll container */
  [data-testid="stSidebarContent"] {
    padding: 0 !important;
    background: var(--sidebar-bg) !important;
  }

  /* Sidebar header strip */
  .sb-header {
    background: linear-gradient(135deg, #0e5238 0%, #062518 100%);
    padding: 24px 20px 20px;
    border-bottom: 1px solid rgba(255,255,255,.06);
    margin-bottom: 0;
  }
  .sb-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
  }
  .sb-logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, var(--brand-400), var(--brand-600));
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem;
    box-shadow: 0 4px 12px rgba(56,181,137,.4);
    flex-shrink: 0;
  }
  .sb-logo-text {
    font-family: var(--font-display);
    font-size: .95rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.2;
  }
  .sb-logo-sub {
    font-size: .65rem;
    color: var(--brand-300);
    font-weight: 500;
    letter-spacing: .5px;
  }

  /* Sidebar section groups */
  .sb-group {
    padding: 16px 16px 12px;
    border-bottom: 1px solid rgba(255,255,255,.05);
  }
  .sb-group:last-child {
    border-bottom: none;
  }
  .sb-group-label {
    font-size: .62rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,.35);
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .sb-group-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,.08);
  }

  /* Sidebar control cards */
  .sb-card {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: var(--radius-md);
    padding: 12px 14px;
    margin-bottom: 10px;
    transition: border-color .15s, background .15s;
  }
  .sb-card:hover {
    background: rgba(255,255,255,.06);
    border-color: rgba(255,255,255,.12);
  }
  .sb-card-label {
    font-size: .7rem;
    font-weight: 600;
    color: rgba(255,255,255,.55);
    letter-spacing: .5px;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 5px;
  }

  /* Override Streamlit widget colors inside sidebar */
  [data-testid="stSidebar"] label,
  [data-testid="stSidebar"] .stSlider label,
  [data-testid="stSidebar"] .stMultiSelect label,
  [data-testid="stSidebar"] .stSelectbox label {
    color: rgba(255,255,255,.75) !important;
    font-size: .78rem !important;
    font-weight: 600 !important;
    font-family: var(--font-body) !important;
    letter-spacing: .2px !important;
  }
  [data-testid="stSidebar"] [data-testid="stSliderThumb"],
  [data-testid="stSidebar"] [data-testid="stSlider"] {
    color: var(--brand-300) !important;
  }
  [data-testid="stSidebar"] .stSlider [data-testid="stSliderLabel"] {
    color: rgba(255,255,255,.9) !important;
    font-size: .82rem !important;
    font-weight: 700 !important;
  }

  /* Slider track */
  [data-testid="stSidebar"] [role="slider"] {
    background: var(--brand-400) !important;
    border: 2px solid var(--brand-300) !important;
    box-shadow: 0 0 0 4px rgba(56,181,137,.2) !important;
  }
  [data-testid="stSidebar"] [data-baseweb="slider"] [role="progressbar"] {
    background: var(--brand-400) !important;
  }

  /* Selectbox & multiselect in sidebar */
  [data-testid="stSidebar"] [data-baseweb="select"] > div,
  [data-testid="stSidebar"] [data-baseweb="select"] > div > div {
    background: rgba(255,255,255,.06) !important;
    border-color: rgba(255,255,255,.12) !important;
    color: rgba(255,255,255,.9) !important;
    border-radius: var(--radius-sm) !important;
  }
  [data-testid="stSidebar"] [data-baseweb="select"] svg {
    fill: rgba(255,255,255,.5) !important;
  }
  [data-testid="stSidebar"] [data-baseweb="tag"] {
    background: var(--brand-700) !important;
    border: 1px solid var(--brand-500) !important;
    color: var(--brand-200) !important;
    border-radius: 4px !important;
    font-size: .7rem !important;
  }
  [data-testid="stSidebar"] [data-baseweb="tag"] span {
    color: var(--brand-200) !important;
  }

  /* Sidebar info panel */
  .sb-info-panel {
    background: rgba(56,181,137,.06);
    border: 1px solid rgba(56,181,137,.15);
    border-radius: var(--radius-md);
    padding: 14px 14px;
    margin-top: 4px;
  }
  .sb-info-row {
    display: flex;
    gap: 8px;
    margin-bottom: 8px;
    align-items: flex-start;
  }
  .sb-info-row:last-child { margin-bottom: 0; }
  .sb-info-dot {
    width: 6px; height: 6px;
    background: var(--brand-400);
    border-radius: 50%;
    flex-shrink: 0;
    margin-top: 5px;
  }
  .sb-info-text {
    font-size: .7rem;
    color: rgba(255,255,255,.6);
    line-height: 1.5;
  }
  .sb-info-text strong {
    color: rgba(255,255,255,.85);
    font-weight: 600;
  }

  /* Sidebar stat chips */
  .sb-stats {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 10px;
  }
  .sb-stat {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: var(--radius-sm);
    padding: 10px 10px;
    text-align: center;
  }
  .sb-stat-val {
    font-family: var(--font-display);
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--brand-300);
    line-height: 1;
    margin-bottom: 3px;
  }
  .sb-stat-label {
    font-size: .6rem;
    font-weight: 600;
    color: rgba(255,255,255,.4);
    text-transform: uppercase;
    letter-spacing: .8px;
  }

  /* ══════════════════════════════════════════════════════════
     KPI METRICS ROW
  ══════════════════════════════════════════════════════════ */
  [data-testid="metric-container"] {
    background: var(--surface-0) !important;
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    padding: 20px 22px !important;
    box-shadow: var(--shadow-sm) !important;
    transition: box-shadow .2s, transform .2s !important;
    position: relative;
    overflow: hidden;
  }
  [data-testid="metric-container"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--brand-400), var(--brand-300));
    opacity: 0;
    transition: opacity .2s;
  }
  [data-testid="metric-container"]:hover {
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
  }
  [data-testid="metric-container"]:hover::before {
    opacity: 1;
  }
  [data-testid="metric-container"] label {
    font-family: var(--font-body) !important;
    font-size: .68rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    color: var(--text-tertiary) !important;
  }
  [data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 1.7rem !important;
    font-weight: 800 !important;
    color: var(--text-primary) !important;
    line-height: 1.1 !important;
  }
  [data-testid="stMetricDelta"] {
    font-size: .75rem !important;
    font-weight: 600 !important;
    margin-top: 2px !important;
  }

  /* ══════════════════════════════════════════════════════════
     SECTION HEADERS
  ══════════════════════════════════════════════════════════ */
  .section-header {
    font-family: var(--font-display);
    font-size: .68rem;
    font-weight: 700;
    color: var(--text-tertiary);
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 0 0 14px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .section-header::before {
    content: '';
    width: 3px; height: 14px;
    background: linear-gradient(180deg, var(--brand-400), var(--brand-600));
    border-radius: 2px;
    flex-shrink: 0;
  }

  /* ══════════════════════════════════════════════════════════
     TABS
  ══════════════════════════════════════════════════════════ */
  .stTabs [data-baseweb="tab-list"] {
    gap: 2px !important;
    background: var(--surface-1) !important;
    border-radius: var(--radius-lg) !important;
    padding: 5px !important;
    border: 1px solid var(--border-subtle) !important;
    box-shadow: var(--shadow-xs) !important;
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: var(--radius-md) !important;
    padding: 9px 20px !important;
    font-size: .78rem !important;
    font-weight: 600 !important;
    font-family: var(--font-body) !important;
    color: var(--text-tertiary) !important;
    border: none !important;
    transition: all .15s !important;
    letter-spacing: .2px;
  }
  .stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary) !important;
    background: var(--surface-2) !important;
  }
  .stTabs [aria-selected="true"] {
    background: var(--surface-0) !important;
    color: var(--brand-700) !important;
    box-shadow: var(--shadow-sm) !important;
    font-weight: 700 !important;
  }

  /* ══════════════════════════════════════════════════════════
     INSIGHT BOXES
  ══════════════════════════════════════════════════════════ */
  .insight {
    background: linear-gradient(135deg, #f0fdf8 0%, #e8fdf5 100%);
    border: 1px solid rgba(26,107,74,.12);
    border-left: 4px solid var(--brand-500);
    border-radius: 0 var(--radius-md) var(--radius-md) 0;
    padding: 16px 20px;
    font-size: .84rem;
    color: var(--text-secondary);
    line-height: 1.7;
    margin-top: 14px;
    box-shadow: var(--shadow-xs);
  }
  .insight strong {
    color: var(--brand-800);
    font-weight: 700;
  }

  /* ══════════════════════════════════════════════════════════
     REGRESSION EQUATION CARD
  ══════════════════════════════════════════════════════════ */
  .eq-card {
    background: #0a1628;
    border: 1px solid rgba(56,181,137,.18);
    border-radius: var(--radius-lg);
    padding: 22px 26px;
    font-family: var(--font-mono);
    font-size: .8rem;
    color: #7ee8c8;
    line-height: 2.1;
    margin: 14px 0;
    box-shadow: 0 0 0 1px rgba(56,181,137,.05), var(--shadow-lg);
    position: relative;
    overflow: hidden;
  }
  .eq-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(56,181,137,.4), transparent);
  }
  .eq-card .eq-label {
    font-size: .6rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: rgba(255,255,255,.3);
    margin-bottom: 8px;
  }

  /* ══════════════════════════════════════════════════════════
     DATA TABLES
  ══════════════════════════════════════════════════════════ */
  [data-testid="stDataFrame"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
  }
  [data-testid="stDataFrame"] thead th {
    background: var(--surface-1) !important;
    font-family: var(--font-body) !important;
    font-size: .7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: var(--text-tertiary) !important;
    padding: 12px 14px !important;
    border-bottom: 1px solid var(--border-default) !important;
  }
  [data-testid="stDataFrame"] tbody tr {
    transition: background .1s !important;
  }
  [data-testid="stDataFrame"] tbody tr:hover {
    background: var(--surface-1) !important;
  }
  [data-testid="stDataFrame"] tbody td {
    font-size: .78rem !important;
    font-family: var(--font-body) !important;
    padding: 10px 14px !important;
    color: var(--text-secondary) !important;
    border-bottom: 1px solid var(--border-subtle) !important;
  }

  /* ══════════════════════════════════════════════════════════
     DIVIDERS
  ══════════════════════════════════════════════════════════ */
  hr {
    border: none !important;
    border-top: 1px solid var(--border-subtle) !important;
    margin: 24px 0 !important;
  }

  /* ══════════════════════════════════════════════════════════
     PREDICTOR PANEL
  ══════════════════════════════════════════════════════════ */
  .pred-result-card {
    background: var(--surface-0);
    border-radius: var(--radius-xl);
    padding: 32px 28px 24px;
    text-align: center;
    box-shadow: var(--shadow-lg);
    border: 1px solid var(--border-subtle);
    position: relative;
    overflow: hidden;
  }
  .pred-label {
    font-family: var(--font-body);
    font-size: .65rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 12px;
  }
  .pred-value {
    font-family: var(--font-display);
    font-size: 5rem;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -3px;
  }
  .pred-sub {
    font-size: .82rem;
    color: var(--text-tertiary);
    margin-top: 8px;
    line-height: 1.5;
  }
  .pred-badge {
    display: inline-block;
    margin-top: 14px;
    padding: 6px 18px;
    border-radius: 100px;
    font-size: .78rem;
    font-weight: 700;
    letter-spacing: .3px;
  }

  /* ══════════════════════════════════════════════════════════
     ABOUT TAB
  ══════════════════════════════════════════════════════════ */
  .about-card {
    background: var(--surface-0);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-xl);
    padding: 28px 30px;
    box-shadow: var(--shadow-sm);
    height: 100%;
  }
  .about-card h3 {
    font-family: var(--font-display) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    color: var(--brand-800) !important;
    margin-bottom: 14px !important;
    margin-top: 0 !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid var(--border-subtle) !important;
  }
  .about-card table {
    width: 100% !important;
    border-collapse: collapse !important;
    font-size: .78rem !important;
    margin: 12px 0 !important;
  }
  .about-card th {
    background: var(--surface-1) !important;
    padding: 8px 12px !important;
    text-align: left !important;
    font-size: .65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    color: var(--text-tertiary) !important;
    border-bottom: 1px solid var(--border-default) !important;
  }
  .about-card td {
    padding: 9px 12px !important;
    border-bottom: 1px solid var(--border-subtle) !important;
    color: var(--text-secondary) !important;
    line-height: 1.4 !important;
  }
  .about-card blockquote {
    background: var(--brand-50) !important;
    border-left: 3px solid var(--brand-400) !important;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0 !important;
    padding: 12px 16px !important;
    margin: 12px 0 16px !important;
    font-size: .84rem !important;
    color: var(--brand-800) !important;
    font-style: italic !important;
  }
  .about-card p {
    font-size: .82rem !important;
    line-height: 1.7 !important;
    color: var(--text-secondary) !important;
  }
  .about-card strong { color: var(--text-primary) !important; }

  /* ══════════════════════════════════════════════════════════
     DARK MODE OVERRIDES
  ══════════════════════════════════════════════════════════ */
  @media (prefers-color-scheme: dark) {
    :root {
      --surface-0:  #111827;
      --surface-1:  #1a2535;
      --surface-2:  #232f42;
      --surface-3:  #2d3b52;
      --surface-4:  #3d4f6a;

      --text-primary:   #f0f6ff;
      --text-secondary: #9fb3c8;
      --text-tertiary:  #6480a0;
      --text-muted:     #4a6280;

      --border-subtle:  rgba(255,255,255,.05);
      --border-default: rgba(255,255,255,.09);
      --border-strong:  rgba(255,255,255,.16);

      --shadow-sm: 0 2px 8px rgba(0,0,0,.25), 0 1px 2px rgba(0,0,0,.15);
      --shadow-md: 0 4px 16px rgba(0,0,0,.35), 0 2px 4px rgba(0,0,0,.2);
      --shadow-lg: 0 8px 32px rgba(0,0,0,.45), 0 4px 8px rgba(0,0,0,.25);
    }
    .hero {
      border-color: rgba(255,255,255,.04) !important;
    }
    .insight {
      background: linear-gradient(135deg, rgba(26,107,74,.12), rgba(26,107,74,.08)) !important;
      border-color: rgba(56,181,137,.15) !important;
      color: var(--text-secondary) !important;
    }
    .insight strong { color: var(--brand-300) !important; }
    .about-card {
      background: var(--surface-1) !important;
    }
    .about-card blockquote {
      background: rgba(26,107,74,.12) !important;
      color: var(--brand-200) !important;
    }
    .pred-result-card { background: var(--surface-1) !important; }
  }

  /* ══════════════════════════════════════════════════════════
     FOOTER
  ══════════════════════════════════════════════════════════ */
  .dashboard-footer {
    text-align: center;
    font-size: .7rem;
    color: var(--text-muted);
    padding: 16px 0;
    border-top: 1px solid var(--border-subtle);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-top: 12px;
  }
  .dashboard-footer .dot {
    width: 3px; height: 3px;
    background: var(--text-muted);
    border-radius: 50%;
    display: inline-block;
    vertical-align: middle;
  }

  /* ── Warnings & Info messages ─────────────────────────── */
  [data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    font-size: .82rem !important;
  }

  /* ── Plot container styling ──────────────────────────── */
  .js-plotly-plot {
    border-radius: var(--radius-md) !important;
  }

  /* ── Streamlit slider overrides (main area) ──────────── */
  .stSlider label {
    font-size: .78rem !important;
    font-weight: 600 !important;
    color: var(--text-secondary) !important;
  }
  .stSlider [data-testid="stSliderLabel"] {
    font-size: .85rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
  }

  /* Smooth column layout */
  [data-testid="column"] { padding: 0 6px !important; }
  [data-testid="column"]:first-child { padding-left: 0 !important; }
  [data-testid="column"]:last-child  { padding-right: 0 !important; }
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

# Plotly default layout for all charts
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="#f7f9fc",
    font=dict(family="DM Sans, Segoe UI, sans-serif", color="#3d5068", size=11),
    margin=dict(l=4, r=4, t=44, b=4),
    title_font=dict(family="Syne, Segoe UI, sans-serif", size=13, color="#0f1923"),
)

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
  <div class="hero-eyebrow">SDG 4 · Quality Education · Analytics Research</div>
  <h1>📚 Learning Poverty Dashboard</h1>
  <p class="sub">What factors drive the share of children who cannot read by end of primary school?<br>
  A robust regression analysis across 75 countries, 2000–2023</p>
  <div class="badges">
    <span class="badge">🌍 75 Countries</span>
    <span class="badge">📅 2000–2023</span>
    <span class="badge">📊 Robust Regression (Huber)</span>
    <span class="badge">🏦 World Bank Open Data</span>
    <span class="badge">🎯 SDG 4 — Quality Education</span>
    <span class="badge">N = 370 Observations</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════
# SIDEBAR — PREMIUM REDESIGN
# ════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sb-header">
      <div class="sb-logo">
        <div class="sb-logo-icon">📚</div>
        <div>
          <div class="sb-logo-text">Learning Poverty</div>
          <div class="sb-logo-sub">SDG 4 ANALYTICS</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FILTERS group ──────────────────────────────────────
    st.markdown("""
    <div class="sb-group">
      <div class="sb-group-label">📅 Time Filter</div>
    </div>
    """, unsafe_allow_html=True)

    sel_year = st.slider(
        "Select Year",
        min_value=int(min(YEARS)),
        max_value=int(max(YEARS)),
        value=2015, step=1,
        help="Filter the world map and driver scatter plots by year"
    )

    st.markdown("""
    <div class="sb-group">
      <div class="sb-group-label">🌍 Country Selection</div>
    </div>
    """, unsafe_allow_html=True)

    sel_countries = st.multiselect(
        "Compare Countries (Trends tab)",
        options=COUNTRIES,
        default=["Niger","Colombia","Spain","Korea, Rep."],
        help="Select multiple countries to compare their learning poverty trends over time"
    )

    focus_country = st.selectbox(
        "Focus Country (Predictor tab)",
        options=COUNTRIES,
        index=COUNTRIES.index("Colombia") if "Colombia" in COUNTRIES else 0,
        help="Default values in the Predictor tab will load from this country's latest data"
    )

    # ── Model Info ─────────────────────────────────────────
    st.markdown("""
    <div class="sb-group">
      <div class="sb-group-label">📐 Model Info</div>
      <div class="sb-info-panel">
        <div class="sb-info-row">
          <div class="sb-info-dot"></div>
          <div class="sb-info-text"><strong>Robust Linear Regression</strong><br>Huber M-estimator (IRLS)</div>
        </div>
        <div class="sb-info-row">
          <div class="sb-info-dot"></div>
          <div class="sb-info-text"><strong>4 Predictors:</strong> Pupil-teacher ratio, trained teachers, gov. expenditure, U5 mortality</div>
        </div>
        <div class="sb-info-row">
          <div class="sb-info-dot"></div>
          <div class="sb-info-text"><strong>Source:</strong> World Bank Open Data & UNESCO UIS</div>
        </div>
      </div>
      <div class="sb-stats">
        <div class="sb-stat">
          <div class="sb-stat-val">75</div>
          <div class="sb-stat-label">Countries</div>
        </div>
        <div class="sb-stat">
          <div class="sb-stat-val">370</div>
          <div class="sb-stat-label">Observations</div>
        </div>
        <div class="sb-stat">
          <div class="sb-stat-val">24yr</div>
          <div class="sb-stat-label">Time Span</div>
        </div>
        <div class="sb-stat">
          <div class="sb-stat-val">4</div>
          <div class="sb-stat-label">Predictors</div>
        </div>
      </div>
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
            "learning_poverty":           ":.1f",
            "predicted_learning_poverty": ":.1f",
            "pupil_teacher_ratio":        ":.1f",
            "trained_teachers":           ":.1f",
            "gov_expenditure":            ":.1f",
            "u5_mortality":               ":.1f",
            "Country Code":               False,
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
        margin=dict(l=0, r=0, t=48, b=0),
        coloraxis_colorbar=dict(
            title="LP (%)", thickness=14, len=0.6,
            tickvals=[0,25,50,75,100],
            tickfont=dict(family="DM Sans", size=11),
            title_font=dict(family="Syne", size=12),
        ),
        geo=dict(
            showframe=False, showcoastlines=True,
            coastlinecolor="#d1dce8", showland=True,
            landcolor="#eef2f7", showocean=True,
            oceancolor="#e2ecf5",
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        title_font=dict(family="Syne, Segoe UI, sans-serif", size=14, color="#0f1923"),
        font=dict(family="DM Sans, sans-serif", color="#3d5068"),
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
    addressable factors. Use the year slider in the sidebar to see how this has changed over time.
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
            height=380,
            **CHART_LAYOUT,
            xaxis=dict(gridcolor="#e2e8f0", title_font=dict(size=11)),
            yaxis=dict(gridcolor="#e2e8f0", range=[0,105], title_font=dict(size=11)),
            legend=dict(
                orientation="h", yanchor="bottom", y=1.02,
                font=dict(family="DM Sans", size=11),
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(fig_lp, use_container_width=True)

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
                    height=280,
                    **CHART_LAYOUT,
                    xaxis=dict(gridcolor="#e2e8f0"),
                    yaxis=dict(gridcolor="#e2e8f0"),
                    showlegend=False,
                    margin=dict(l=0, r=0, t=40, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# TAB 3: DRIVERS
# ════════════════════════════════════════════════════════════════════
with tab_drivers:
    st.markdown(f'<div class="section-header">What Drives Learning Poverty? — {sel_year}</div>',
                unsafe_allow_html=True)

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
            height=360,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar=dict(title="r", thickness=12, len=0.8),
            margin=dict(l=0, r=0, t=48, b=0),
            font=dict(family="DM Sans, sans-serif", color="#3d5068"),
            title_font=dict(family="Syne", size=13, color="#0f1923"),
        )
        fig_corr.update_traces(textfont_size=11, textfont_family="DM Mono, monospace")
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
            fig_sc.update_traces(marker_size=9, marker_opacity=0.72)
            fig_sc.update_layout(
                height=320,
                **CHART_LAYOUT,
                xaxis=dict(gridcolor="#e2e8f0"),
                yaxis=dict(gridcolor="#e2e8f0", range=[0,105]),
                margin=dict(l=0, r=0, t=44, b=0),
            )
            st.plotly_chart(fig_sc, use_container_width=True)


# ════════════════════════════════════════════════════════════════════
# TAB 4: REGRESSION RESULTS
# ════════════════════════════════════════════════════════════════════
with tab_regression:
    st.markdown('<div class="section-header">Robust Regression Results (Huber M-estimator)</div>',
                unsafe_allow_html=True)

    col_coef, col_fit = st.columns([1, 1])

    with col_coef:
        coef_names  = [k for k in COEFS if k != "const"]
        coef_vals   = [COEFS[k] for k in coef_names]
        ci_lo       = [CI[k]["0"] for k in coef_names]
        ci_hi       = [CI[k]["1"] for k in coef_names]
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
                marker_opacity=0.85,
                name=sig_label,
                showlegend=False,
                error_x=dict(
                    type="data", symmetric=False,
                    array=[hi - val], arrayminus=[val - lo],
                    color="#555555", thickness=2, width=6,
                ),
                customdata=[[name, val, pv, lo, hi]],
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Coefficient: %{x:.3f}<br>"
                    "95% CI: [%{customdata[3]:.3f}, %{customdata[4]:.3f}]<br>"
                    "p-value: %{customdata[2]:.4f}<extra></extra>"
                ),
            ))

        fig_coef.add_vline(x=0, line_color="#334155", line_width=1.5)
        fig_coef.update_layout(
            title="Regression Coefficients (raw scale)",
            height=320,
            **CHART_LAYOUT,
            xaxis=dict(title="Coefficient (per unit change in predictor)",
                       gridcolor="#e2e8f0", zeroline=False),
            yaxis=dict(gridcolor="#e2e8f0"),
            margin=dict(l=0, r=20, t=44, b=0),
        )
        st.plotly_chart(fig_coef, use_container_width=True)

        sig_rows = []
        for k in coef_names:
            p = PVALS[k]
            c = COEFS[k]
            direction = "↑ Increases LP" if c > 0 else "↓ Decreases LP"
            sig_rows.append({
                "Variable":    IND_LABELS.get(k, k),
                "Coef":        f"{c:+.4f}",
                "p-value":     f"{p:.4f}",
                "Direction":   direction,
                "Significant": "✅ Yes" if p < 0.05 else "❌ No",
            })
        st.dataframe(pd.DataFrame(sig_rows), hide_index=True, use_container_width=True)

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
                "learning_poverty":           "Actual Learning Poverty (%)",
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
        fig_fit.update_traces(marker_size=8, marker_opacity=0.72)
        fig_fit.update_layout(
            height=320,
            **CHART_LAYOUT,
            xaxis=dict(range=[0,105], gridcolor="#e2e8f0"),
            yaxis=dict(range=[0,105], gridcolor="#e2e8f0"),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=44, b=0),
        )
        st.plotly_chart(fig_fit, use_container_width=True)

        fig_res = px.histogram(
            fit_data, x="huber_residuals",
            nbins=30,
            labels={"huber_residuals": "Huber Residual"},
            title="Distribution of Huber Residuals",
            color_discrete_sequence=["#457b9d"],
        )
        fig_res.update_layout(
            height=240,
            **CHART_LAYOUT,
            xaxis=dict(gridcolor="#e2e8f0"),
            yaxis=dict(gridcolor="#e2e8f0", title="Count"),
            margin=dict(l=0, r=0, t=44, b=0),
            bargap=0.06,
        )
        st.plotly_chart(fig_res, use_container_width=True)

    st.markdown("---")
    st.markdown('<div class="section-header">Regression Equation</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="eq-card">
      <div class="eq-label">Estimated Model · Huber M-estimator</div>
      <span style="color:#ffd700;font-weight:700;font-size:.9rem">Learning Poverty</span>
      <span style="color:#ffffff"> = </span>
      <span style="color:#7ee8c8">{COEFS['const']:.4f}</span>
      <span style="color:#ffffff"> +</span>
      <br>
      <span style="color:#a8d8ea">&nbsp;&nbsp;&nbsp;{COEFS['pupil_teacher_ratio']:+.4f} × Pupil-Teacher Ratio</span>
      <br>
      <span style="color:#a8d8ea">&nbsp;&nbsp;&nbsp;{COEFS['trained_teachers']:+.4f} × Trained Teachers (%)</span>
      <br>
      <span style="color:#a8d8ea">&nbsp;&nbsp;&nbsp;{COEFS['gov_expenditure']:+.4f} × Gov. Expenditure (% GDP/cap)</span>
      <br>
      <span style="color:#ffb3b3">&nbsp;&nbsp;&nbsp;{COEFS['u5_mortality']:+.4f} × Under-5 Mortality (per 1,000)</span>
    </div>
    """, unsafe_allow_html=True)

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
    st.markdown(f"Adjust the sliders below to estimate learning poverty for any scenario. "
                f"Defaults loaded from **{focus_country}** (latest available data).")

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
        st.markdown('<div class="section-header">Input Parameters</div>', unsafe_allow_html=True)
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

        # Badge background colors per severity
        badge_bg = ("#ffe4e6" if lp_pred > 75 else
                    "#ffedd5" if lp_pred > 50 else
                    "#fef9c3" if lp_pred > 25 else
                    "#dcfce7")

        st.markdown(f"""
        <div class="pred-result-card" style="border: 2px solid {color}20; box-shadow: 0 8px 32px {color}18;">
          <div style="position:absolute;top:0;left:0;right:0;height:4px;
                      background:linear-gradient(90deg,{color},{color}88);"></div>
          <div class="pred-label">Estimated Learning Poverty</div>
          <div class="pred-value" style="color:{color}">{lp_pred:.1f}%</div>
          <div class="pred-sub">of children leave primary school<br>unable to read at grade level</div>
          <div class="pred-badge" style="background:{badge_bg};color:{color};
               border:1.5px solid {color}40;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=lp_pred,
            number={"suffix": "%", "font": {"size": 28, "family": "Syne, sans-serif", "color": color}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1,
                         "tickfont": {"family": "DM Sans", "size": 10}},
                "bar":  {"color": color, "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
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
            height=220,
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=20, r=20, t=20, b=10),
            font=dict(family="DM Sans, sans-serif"),
        )
        st.plotly_chart(fig_gauge, use_container_width=True)

    strongest_k = max(IND_VARS, key=lambda k: abs(COEFS[k]))
    st.markdown(f"""
    <div class="insight">
    <strong>How to read this:</strong> At the input values above, the model estimates
    <strong>{lp_pred:.1f}%</strong> learning poverty — rated as <strong>{label}</strong>.
    The single strongest driver in this model is
    <strong>{IND_LABELS[strongest_k]}</strong> with a coefficient of
    <strong>{COEFS[strongest_k]:+.4f}</strong>, meaning each additional unit of this variable
    shifts predicted learning poverty by {abs(COEFS[strongest_k]):.2f} percentage points.
    This tool lets policymakers ask: <em>"If we reduce class sizes or train more teachers,
    by how much does learning poverty fall?"</em>
    </div>
    """, unsafe_allow_html=True)

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
        <div class="about-card">
        <h3>📌 Research Question</h3>
        <blockquote>"What factors significantly influence Learning Poverty across countries?"</blockquote>
        <p>Learning Poverty — the share of children who cannot read and understand a simple
        text by age 10 — is the SDG 4 flagship indicator. It combines in-school proficiency
        with out-of-school rates to give a complete picture of educational exclusion.</p>

        <h3>🔬 Methodology</h3>
        <p><strong>Model:</strong> Robust Linear Regression (Huber M-estimator) — chosen because
        all five OLS assumptions were violated in this dataset.</p>

        <p><strong>Explanatory variables (literature-backed):</strong></p>

        | Variable | Source |
        |---|---|
        | Pupil-Teacher Ratio | Hanushek & Woessmann (2010) |
        | Trained Teachers (%) | UNESCO (2022) |
        | Gov. Expenditure per Student | Psacharopoulos & Patrinos (2018) |
        | Under-5 Mortality | Grantham-McGregor et al. (2007) |

        <h3>📊 Dataset</h3>
        <p>
        <strong>Source:</strong> World Bank Open Data<br>
        <strong>Coverage:</strong> 75 countries, 2000–2023<br>
        <strong>Observations:</strong> 370 (after cleaning)<br>
        <strong>Cleaning:</strong> Forward/back-fill (max 2 steps), no mean imputation
        </p>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="about-card">
        <h3>📐 Model Results Summary</h3>

        | Predictor | Coefficient | p-value | Significant? |
        |---|---|---|---|
        | Intercept | +47.14 | < 0.001 | ✅ |
        | Pupil-Teacher Ratio | −0.98 | 0.595 | ❌ |
        | Trained Teachers (%) | −2.82 | 0.011 | ✅ |
        | Gov. Expenditure | −3.64 | 0.001 | ✅ |
        | Under-5 Mortality | +22.74 | < 0.001 | ✅ |

        <h3>🔑 Key Findings</h3>
        <p><strong>Under-5 Mortality</strong> is the dominant driver (coef = +22.74, p < 0.001).
        Countries with high child mortality — a proxy for poor nutrition, healthcare,
        and early childhood development — have dramatically higher learning poverty.
        This underscores that education outcomes are inseparable from health outcomes.</p>

        <p><strong>Trained Teachers (%)</strong> (coef = −2.82, p = 0.011) — every percentage
        point increase in professionally trained teachers reduces learning poverty
        by 2.8 percentage points on average.</p>

        <p><strong>Government Expenditure per Student</strong> (coef = −3.64, p < 0.001) —
        the strongest purely educational lever: investing more per student
        drives measurable reductions in learning poverty.</p>

        <p><strong>Pupil-Teacher Ratio</strong> was not statistically significant in the
        robust model (p = 0.595), suggesting that class size alone may matter
        less than <em>teacher quality</em> and <em>investment</em> per student.</p>

        <h3>🏦 Data Sources</h3>
        <p>
        World Bank Open Data — <a href="https://data.worldbank.org">data.worldbank.org</a><br>
        UNESCO UIS — <a href="https://uis.unesco.org">uis.unesco.org</a>
        </p>

        <h3>🎓 Course</h3>
        <p><strong>Analytics Techniques and Tools — Finals</strong><br>
        SDG 4: Quality Education</p>
        </div>
        """, unsafe_allow_html=True)


# ─── FOOTER ─────────────────────────────────────────────────────────
st.markdown("""
<div class="dashboard-footer">
  <span>Built with Streamlit</span>
  <span class="dot"></span>
  <span>Data: World Bank Open Data</span>
  <span class="dot"></span>
  <span>Model: Robust Regression (Huber M-estimator)</span>
  <span class="dot"></span>
  <span>SDG 4 — Quality Education</span>
  <span class="dot"></span>
  <span>Analytics Techniques and Tools</span>
</div>
""", unsafe_allow_html=True)
