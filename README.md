# 📚 Learning Poverty Dashboard — SDG 4: Quality Education

> **What factors significantly influence Learning Poverty across countries over time?**

An interactive, regression-powered dashboard built with Streamlit, analyzing the drivers of learning poverty across 75 countries (2000–2023) using World Bank Open Data and a Huber Robust Regression model.

---

## 🔗 Live Dashboard

[Open in Streamlit](https://learning-poverty-dashboard-sdg-4-quality-education-hcvgojhh2b8.streamlit.app/)

---

## 📌 What is Learning Poverty?

Learning Poverty is the share of children who **cannot read and understand a simple text by age 10**. It combines in-school reading proficiency with out-of-school rates to give a complete picture of educational exclusion — the SDG 4 flagship indicator jointly developed by the World Bank and UNESCO (2019).

---

## 🔬 Research Question

> *"What factors significantly influence Learning Poverty across countries over time?"*

---

## 📊 Dashboard Features

| Section | What you can explore |
|---|---|
| 🗺️ **Global Map** | Choropleth showing LP rate by country, updated by year slider |
| 📊 **Top 15 Bar Chart** | Highest LP countries ranked for the selected year |
| 📈 **Trend Over Time** | Global average trend with country-level trajectories in the background |
| 🔍 **Driver Scatter** | Selectable predictor vs. LP with OLS trendline |
| 🕸️ **Radar Chart** | Normalized driver profiles — top 6 vs. bottom 6 LP countries |
| 🏥 **U5 Mortality Scatter** | Dedicated view of the strongest regression signal (β = +22.74) |
| 📉 **Country Trends** | Individual LP trajectories for selected or default countries |
| 📦 **Period Box Plot** | LP distribution shift across 2000–2004, 2005–2009, 2010–2014, 2015–2023 |
| 💡 **Evidence-Based Insights** | Dynamic narrative: critical cases, trend signal, driver correlation, best performer |
| 🏥 **U5 Proxy Explanation** | Why child mortality predicts learning poverty — mechanism and literature |
| 🎯 **Policy Priority Cards** | 4 ranked, model-backed actions for policymakers |

> Every chart, metric, and insight card updates dynamically when the **year slider** is moved.

---

## 📐 Model

**Robust Linear Regression — Huber M-Estimator (statsmodels RLM / IRLS)**

OLS was tested first and rejected after diagnostic violations:

| OLS Diagnostic | Result |
|---|---|
| Residual Normality (Shapiro-Wilk & Jarque-Bera) | ❌ Violated |
| Homoscedasticity (Breusch-Pagan) | ❌ Violated |
| Autocorrelation (Durbin-Watson = 0.434) | ❌ Strong positive autocorrelation |
| Influential Observations (Cook's Distance) | ❌ Multiple detected |

Huber's M-estimator was selected over Tukey Biweight and Hampel for its principled down-weighting of large residuals while maintaining higher statistical efficiency at moderate outlier levels.

> ⚠️ **Note:** The Durbin-Watson statistic of 0.434 indicates strong panel autocorrelation, partly driven by missing data across years. Coefficient magnitudes should be interpreted directionally, not as precise causal estimates.

### Regression Equation (Standardized Predictors)

```
Learning Poverty = 47.14
  + (−0.98 × Pupil-Teacher Ratio)       [not significant, p = 0.595]
  + (−2.82 × Trained Teachers %)         [significant, p = 0.011]
  + (−3.64 × Gov. Expenditure/Student)   [significant, p = 0.001]
  + (+22.74 × Under-5 Mortality)         [highly significant, p < 0.001]
```

### Key Findings

| Predictor | Coefficient (β) | p-value | Significant |
|---|---|---|---|
| Intercept | +47.14 | < 0.001 | ✅ |
| Pupil-Teacher Ratio | −0.98 | 0.595 | ❌ |
| Trained Teachers (%) | −2.82 | 0.011 | ✅ |
| Gov. Expenditure per Student | −3.64 | 0.001 | ✅ |
| Under-5 Mortality | +22.74 | < 0.001 | ✅ |

**Under-5 Mortality dominates** — its coefficient is ~6× larger than the next strongest predictor, confirming that learning poverty is deeply embedded in broader health and socioeconomic conditions.

**Pupil-Teacher Ratio is non-significant** — class size alone has no independent linear effect once teacher quality and expenditure are accounted for. Hiring more teachers without training them is unlikely to improve outcomes.

> All findings reflect **statistical associations** from an observational dataset, not proven causal effects.

---

## 🎯 Policy Priorities (from the dashboard)

Ranked by model weight and policy feasibility:

1. **Attack the health-poverty trap first** — U5 mortality (β = +22.74, p < 0.001) is the strongest predictor. No education reform has historically closed the LP gap without parallel health investment.
2. **Set a teacher training floor, not a target** — Trained teacher share (β = −2.82, p = 0.011) is the most actionable within-school lever. Mandate ≥80% trained teacher coverage as a budget-protected baseline.
3. **Spend smarter, not just more** — Gov. expenditure (β = −3.64, p = 0.001) matters, but allocation quality matters as much as quantity. Redirect to foundational literacy in grades 1–3.
4. **Close the data gap before 2030** — Missing LP data across recent years required imputation and contributes to model autocorrelation. Mandate annual reading assessments aligned to PIRLS/EGRA standards.

---

## 📁 Repository Structure

```
sdg4_dashboard/
│
├── app.py                  # Main Streamlit dashboard
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── banner.png              # Header banner image
│
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
│
└── cleaned_dataset.csv     # Cleaned panel dataset (75 countries × 2000–2023)
```

---

## 🚀 Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/sdg4_dashboard.git
cd sdg4_dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. Push this repository to GitHub (public)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app**
4. Select your repository, branch (`main`), and set **Main file path** to `app.py`
5. Click **Deploy**

---

## 📦 Data Sources

| Indicator | World Bank Series Code |
|---|---|
| Learning Poverty Rate | SE.LPV.PRIM |
| Pupil-Teacher Ratio (Primary) | SE.PRM.ENRL.TC.ZS |
| Trained Teachers (Primary %) | SE.PRM.TCAQ.ZS |
| Gov. Expenditure per Student (% GDP/cap) | SE.XPD.PRIM.PC.ZS |
| Under-5 Mortality (per 1,000 live births) | SH.DYN.MORT |

**Source:** [World Bank Open Data — World Development Indicators](https://databank.worldbank.org/source/world-development-indicators)  
**Coverage:** 75 countries · 2000–2023 · Cleaned via forward/backward imputation (limit = 2 periods) + IQR winsorization

---

## 📚 Key Literature References

| Variable / Topic | Reference |
|---|---|
| Learning Poverty metric | World Bank & UNESCO. (2019). *Ending Learning Poverty: What Will It Take?* Washington, DC: World Bank. |
| Under-5 Mortality as proxy | Alderman, H., Hoddinott, J., & Kinsey, B. (2006). Long term consequences of early childhood malnutrition. *Oxford Economic Papers, 58*(3), 450–474. |
| Under-5 Mortality & learning | Glewwe, P., Jacoby, H., & King, E. (2001). Early childhood nutrition and academic achievement. *Journal of Public Economics, 81*(3), 345–368. |
| Trained teachers | Rivkin, S., Hanushek, E., & Kain, J. (2005). Teachers, schools, and academic achievement. *Econometrica, 73*(2), 417–458. |
| Gov. expenditure | Jackson, C.K., Johnson, R., & Persico, C. (2016). The effects of school spending on educational and economic outcomes. *Quarterly Journal of Economics, 131*(1), 157–218. |
| Child mortality & SDG interconnect | UNICEF, WHO & World Bank. (2023). *Levels & Trends in Child Mortality Report.* |
| Education outcomes in developing countries | Glewwe, P. & Muralidharan, K. (2016). Improving education outcomes in developing countries. *Handbook of the Economics of Education, 5*, 653–743. |

---

## 🎓 Course

**Analytics Techniques and Tools — Finals ALA**
**Leanne Joy P. Libertad · BSIS 3-B**
Submitted to: Prof. Paolo Hilado, MSc. (Data Science)
SDG 4: Quality Education · World Bank Open Data Analysis
