# 🇺🇸 U.S. Labor Statistics Dashboard (ECON 8320 Project)

This project creates an interactive, auto-updating web dashboard displaying key U.S. labor market metrics sourced directly from the Bureau of Labor Statistics (BLS) Public Data API. The dashboard is designed to showcase data cleaning, visualization, and automated workflow skills.

## ✨ Features

* **Data Source:** Live data retrieved from the BLS API (v2).
* **Automation:** Data is automatically updated monthly via a **GitHub Action** and committed back to the repository.
* **Visualization:** Interactive time-series charts powered by Plotly and presented via Streamlit.
* **Key Metrics:** Total Nonfarm Payrolls, Unemployment Rate, Labor Force Participation Rate, and Average Hourly Earnings.

## 🚀 Deployment

The dashboard is deployed on the Streamlit Community Cloud and runs directly from this repository. The dashboard automatically refreshes when the underlying `data/bls_data.csv` file is updated by the monthly GitHub Action.

## 🛠️ Setup (Local Development)

To run and test the data collection script or the dashboard locally:

1.  **Clone the Repository:**
    ```bash
    git clone [YOUR_REPO_URL]
    cd [YOUR_REPO_NAME]
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    .\venv\Scripts\activate   # Windows PowerShell
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set API Key (Crucial):** Set your BLS API key as an environment variable named `BLS_API_KEY`.
    ```bash
    # macOS/Linux (for current terminal session)
    export BLS_API_KEY="YOUR_API_KEY_HERE"

    # Windows PowerShell (use setx to set permanently)
    setx BLS_API_KEY "YOUR_API_KEY_HERE"
    ```

5.  **Run the Fetch Script (Initial Data Load):**
    ```bash
    python scripts/fetch_bls_data.py
    ```

6.  **Run the Dashboard:**
    ```bash
    streamlit run app.py
    ```

## 🔐 GitHub Secrets Configuration

To enable the monthly automation, the following secret must be set in your GitHub repository:

* **Secret Name:** `BLS_API_KEY`
* **Secret Value:** Your BLS Public Data API Key (`6960d3f0...`).
* *(Location: Repository Settings -> Secrets and variables -> Actions)*
