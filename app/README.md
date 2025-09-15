
# HICP Dashboard — Streamlit App

This app mirrors a Power BI dashboard (HICP EU27) with filters for Country, Category, and Date. 
It reads a CSV and computes MoM% and YoY% if they are missing.

## How to run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

Open the printed local URL in your browser.

## How to deploy (Streamlit Cloud)
1. Push this folder to a GitHub repo, e.g., `hicp-streamlit-app`.
2. Go to https://streamlit.io → Sign in with GitHub → New App.
3. Select your repo/branch → Deploy. You’ll get a public URL you can put on your résumé.

## Data
- Put your CSV at `data/data.csv`. The loader tries to detect these columns:
  - **date / yearmonth** (monthly)
  - **country** (or **geo**)
  - **category** (or **coicop**)
  - **index** (or **value**)
  - optional **mom_%** and **yoy_%** (computed if missing)

## Notes
- The app uses Plotly for interactive charts.
- The data table can be downloaded as a filtered CSV for sharing.
