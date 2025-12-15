# U.S. Labor Structure Dashboard

## 🚀 Live Dashboard

You can try it live here:

**[Click here to view the interactive dashboard](https://econ8320-project-bls-labor-statistics-dashboard-i42zumaice6k9p.streamlit.app/)**


This project explores U.S. labor market trends using official data from the **Bureau of Labor Statistics (BLS)**. The dashboard is designed to clearly separate **short-run labor market conditions** from **long-run structural changes** in the economy.


The goal is to provide a simple, transparent, and interpretable view of how the U.S. labor market has evolved over time.

---

## 📊 What the Dashboard Shows

### 1. Time Series: Labor Market Conditions

The *Time Series* tab displays two key labor indicators side by side: The dashboard reports the total change (in percentage points) over the selected period. An up or down arrow (⬆️ / ⬇️) highlights the direction of change

* **Unemployment Rate**

  * Yearly U.S. unemployment rate
  * Users select a start year and end year

* **Labor Force Participation Rate**

  * Shows the share of the population that is working or actively looking for work
  * Provides important context for unemployment trends
    

Together, these series help distinguish between changes driven by job availability and changes driven by labor force participation.

---

### 2. Manufacturing Share of Employment

This tab focuses on long-run structural change in the U.S. economy:

* Calculates manufacturing employment as a share of total nonfarm payroll employment
* Highlights the long-term decline of manufacturing employment relative to the overall labor market
* The formula used for the calculation is shown directly in the dashboard for transparency

---

## 🧮 How Manufacturing Share Is Calculated

The manufacturing share of employment is calculated as:

[
\text{Manufacturing Share (%)} = \frac{\text{Manufacturing Employment}}{\text{Total Nonfarm Payrolls}} \times 100
]

All values come directly from official BLS employment series.

---

## 🎯 Purpose of the Project

This project is designed to:

* Demonstrate time-series data analysis
* Combine short-run labor market indicators with long-run structural trends
* Show how multiple labor statistics complement each other
* Provide a clean, interpretable dashboard using official government data

---

## 📝 Notes and Interpretation

* The **unemployment rate** reflects short-term economic conditions and business cycles
* The **labor force participation rate** provides context for changes in unemployment
* **Manufacturing’s share of employment** highlights long-term structural change in the U.S. economy

The dashboard separates these concepts to make interpretation clear, intuitive, and economically meaningful.

---

## 🔁 Data Source and Updates

* All data are sourced from the **Bureau of Labor Statistics (BLS) API**
* Data are collected and cleaned using a Python script
* The dataset is updated automatically using GitHub Actions

---

## ▶️ Running the Dashboard Locally

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
2. Fetch the latest data:

   ```bash
   python scripts/fetch_labor_data.py
   ```
3. Run the dashboard:

   ```bash
   streamlit run app/app.py
   ```



