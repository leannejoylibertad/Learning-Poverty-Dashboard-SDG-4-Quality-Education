# 📚 Learning Poverty Dashboard — SDG 4: Quality Education

> **What factors significantly influence Learning Poverty across countries?**

An interactive, regression-powered dashboard built with Streamlit, analyzing the drivers of learning poverty across 75 countries (2000–2023) using World Bank Open Data.

---

## 🔗 Live Dashboard

[Open in Streamlit](https://learning-poverty-dashboard-sdg-4-quality-education-hcvgojhh2b8.streamlit.app/)

> Replace the link above with your actual Streamlit Cloud URL after deployment.

---

## 📌 What is Learning Poverty?

Learning Poverty is the share of children who **cannot read and understand a simple text by age 10**. It combines in-school reading proficiency with out-of-school rates to give a complete picture of educational exclusion — the SDG 4 flagship indicator.

---

## 🔬 Research Question

> *"What factors significantly influence Learning Poverty across countries over time?"*

---

## 📊 Dashboard Features

| Tab | What you can explore |
|---|---|
| 🗺️ **World Map** | Choropleth showing LP rate by country, animated by year slider |
| 📈 **Trends** | Multi-country time series for LP and all drivers |
| 🔍 **Drivers** | Scatter plots + correlation heatmap for each predictor |
| 📐 **Regression** | Coefficient chart, actual vs. predicted, residuals, diagnostics |
| 🧮 **Predictor** | Live sliders to estimate LP using the regression equation |
| ℹ️ **About** | Methodology, findings, data sources, literature references |

---

## 📐 Model

**Robust Linear Regression (Huber M-estimator / IRLS)**

All five OLS assumptions were violated (non-normal residuals, heteroscedasticity, autocorrelation, influential outliers), making Robust Regression the appropriate model.

### Regression Equation

```
Learning Poverty = 47.14
  + (−0.9790 × Pupil-Teacher Ratio)
  + (−2.8247 × Trained Teachers %)
  + (−3.6401 × Gov. Expenditure per Student)
  + (+22.741 × Under-5 Mortality)
```

### Key Findings

| Predictor | Coefficient | p-value | Significant |
|---|---|---|---|
| Intercept | +47.14 | <0.001 | ✅ |
| Pupil-Teacher Ratio | −0.98 | 0.595 | ❌ |
| Trained Teachers (%) | −2.82 | 0.011 | ✅ |
| Gov. Expenditure per Student | −3.64 | 0.001 | ✅ |
| Under-5 Mortality | +22.74 | <0.001 | ✅ |

**Under-5 Mortality** dominates — child health is inseparable from learning outcomes.

---

## 📁 Repository Structure

```
sdg4_dashboard/
│
├── app.py                    # Main Streamlit dashboard
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── .streamlit/
│   └── config.toml           # Streamlit theme configuration
│
└── data/
    ├── dashboard_data.csv     # LP actual, predicted, residuals (370 rows)
    ├── cleaned_dataset.csv    # All variables after cleaning (370 rows × 10 cols)
    ├── model_params.json      # Coefficients, p-values, confidence intervals
    ├── diagnostics_results.csv # OLS assumption test results
    └── correlation_results.csv # Pearson correlation matrix
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
| Under-5 Mortality (per 1,000) | SH.DYN.MORT |

**Source:** [World Bank Open Data](https://data.worldbank.org) — 75 countries, 2000–2023

---

## 📚 Literature References

| Variable | Reference |
|---|---|
| Pupil-Teacher Ratio | Hanushek, E. & Woessmann, L. (2010). *The Economics of International Differences in Educational Achievement.* NBER Working Paper 15949. |
| Trained Teachers | UNESCO (2022). *Global Education Monitoring Report.* Paris: UNESCO. |
| Gov. Expenditure | Psacharopoulos, G. & Patrinos, H.A. (2018). *Returns to investment in education.* Education Economics, 26(5), 445–458. |
| Under-5 Mortality | Grantham-McGregor, S. et al. (2007). *Developmental potential in the first 5 years for children in developing countries.* The Lancet, 369(9555), 60–70. |

---

## 🎓 Course

**Analytics Techniques and Tools — Finals**  
SDG 4: Quality Education  
World Bank Open Data Analysis
