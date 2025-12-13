# econ8320-project-BLS-Labor-Statistics-Dashboard
A Streamlit dashboard that shows the latest labor statistics from the U.S. Bureau of Labor Statistics (BLS). 

# Setup (local)
1. Create a virtualenv:
   python -m venv .venv
   source .venv/bin/activate   # mac/linux
   .venv\Scripts\activate      # windows

2. Install:
   pip install pandas requests streamlit plotly

3. Set your BLS API key (one-time):
   export BLS_API_KEY="YOUR_BLS_KEY"   # mac/linux
   setx BLS_API_KEY "YOUR_BLS_KEY"     # windows (restart terminal)

4. Run the fetch script:
   python scripts/fetch_bls_data.py

5. Run the app:
   streamlit run app.py

# GitHub Actions
- Add a repo secret named `BLS_API_KEY` with your key value.
- The workflow `.github/workflows/update.yml` will run monthly and commit updated `data/bls_data.csv`.
