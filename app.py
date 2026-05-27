import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & THEME
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Learning Poverty Dashboard | SDG 4",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for uniform card metric styling & layout corrections
st.markdown("""
    <style>
        /* Container background styling */
        .stApp {
            background-color: #0D1117;
            color: #E6EDF3;
        }
        /* Make KPI metric boxes have uniform structural heights and alignments */
        [data-testid="stMetricValue"] {
            font-size: 28px !important;
            font-weight: 700 !important;
            color: #79C0FF !important;
        }
        [data-testid="stMetricLabel"] {
            font-size: 13px !important;
            color: #8B949E !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        /* Custom card background styling */
        div[data-testid="stMetric"] {
            background-color: #161B22 !important;
            border: 1px solid #30363D !important;
            border-radius: 10px !important;
            padding: 15px 20px !important;
        }
    </style>
""", unsafe_html=True)

# -----------------------------------------------------------------------------
# 2. BANNER INSERTION
# -----------------------------------------------------------------------------
# Display your customized banner image right at the top
st.image("banner.png", use_container_width=True)
st.markdown("<br>", unsafe_html=True)

# -----------------------------------------------------------------------------
# 3. DATA RECOVERY & FILTERING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_dataset.csv')
    return df

df = load_data()

# Sidebar Interactive Controls
st.sidebar.header("Global Filters")
available_years = sorted(df['Year'].unique())
selected_year = st.sidebar.selectbox("Select Target Evaluation Year", available_years, index=len(available_years)-1)

countries = sorted(df['Country Name'].unique())
selected_countries = st.sidebar.multiselect("Select Countries to Monitor", countries, default=["Albania", "United States"] if "United States" in countries else [countries[0]])

# Filter Data
filtered_df = df[df['Year'] == selected_year]
if selected_countries:
    display_df = df[(df['Country Name'].isin(selected_countries)) & (df['Year'] == selected_year)]
else:
    display_df = filtered_df

# -----------------------------------------------------------------------------
# 4. UNIFORM KEY PERFORMANCE INDICATORS (KPIs)
# -----------------------------------------------------------------------------
# Creating 4 equal columns ensures 'Avg. Pupils per Teacher' has the exact same block size as the others.
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

with kpi_col1:
    avg_lp = filtered_df['learning_poverty'].mean()
    st.metric(
        label="Avg. Learning Poverty",
        value=f"{avg_lp:.1f}%" if not pd.isna(avg_lp) else "N/A",
        help="Percentage of children unable to read and understand a simple text by age 10."
    )

with kpi_col2:
    # Synchronized exactly with the other 3 metric cards
    avg_ptr = filtered_df['pupil_teacher_ratio'].mean()
    st.metric(
        label="Avg. Pupils per Teacher",
        value=f"{avg_ptr:.1f}" if not pd.isna(avg_ptr) else "N/A",
        help="Primary school pupil-teacher ratio."
    )

with kpi_col3:
    avg_trained = filtered_df['trained_teachers'].mean()
    st.metric(
        label="Trained Teachers",
        value=f"{avg_trained:.1f}%" if not pd.isna(avg_trained) else "N/A",
        help="Percentage of primary school teachers who have received at least the minimum organized pedagogical teacher training."
    )

with kpi_col4:
    avg_gov = filtered_df['gov_expenditure'].mean()
    st.metric(
        label="Govt. Expenditure",
        value=f"{avg_gov:.1f}%" if not pd.isna(avg_gov) else "N/A",
        help="Government expenditure on education as a percentage of total government expenditure."
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. DATA VISUALIZATION SECTION
# -----------------------------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Learning Poverty vs. Pupil-Teacher Ratio")
    if not filtered_df.empty:
        fig_scatter = px.scatter(
            filtered_df,
            x="pupil_teacher_ratio",
            y="learning_poverty",
            hover_name="Country Name",
            size="u5_mortality",
            color="gov_expenditure",
            labels={
                "pupil_teacher_ratio": "Pupils per Teacher Ratio",
                "learning_poverty": "Learning Poverty Index (%)",
                "gov_expenditure": "Gov. Budget %"
            },
            template="plotly_dark"
        )
        fig_scatter.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#E6EDF3"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("No data available for the selected filters.")

with col_right:
    st.subheader("Country Comparison Metrics Tracker")
    if not display_df.empty:
        fig_bar = px.bar(
            display_df,
            x="Country Name",
            y=["learning_poverty", "pupil_teacher_ratio", "trained_teachers"],
            barmode="group",
            labels={"value": "Scale Value", "variable": "Core Metrics"},
            template="plotly_dark",
            color_discrete_sequence=["#F78166", "#79C0FF", "#56D364"]
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color="#E6EDF3"
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Select countries from the sidebar to view detailed comparison graphs.")
