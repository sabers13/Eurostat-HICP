# EU HICP Dashboard (Streamlit + Plotly)

Interactive dashboard to explore **HICP** (Harmonised Index of Consumer Prices) across EU countries and COICOP categories.  
The app reads a monthly index CSV (2015=100), computes **Monthly** and **Annual** inflation rates, and renders responsive, scrollable visualizations with **flag-inspired country colors** and optional **country flags**.

`app/sample.png`

---

## ✨ Features

- **Automatic rate calculations**
  - Monthly inflation rate: `(I_t / I_{t-1} - 1) * 100`
  - Annual inflation rate:  `(I_t / I_{t-12} - 1) * 100`
- **Powerful filtering**
  - Month range, Countries/Regions, COICOP Categories
  - “Separate by Country” / “Separate by Category” facetting
- **Smart coloring & legend**
  - Countries colored using **flag palette**
  - Multiple categories → distinct palette + line dashes per country
  - Compact legend **table** under charts (columns = countries, rows = categories)
- **Scrollable facet grids**
  - Large Country × Category grids render in a scrollable container
- **Helpful summaries**
  - KPIs (latest month, average rates)
  - “Latest annual rate by Country” and “By Category (latest)” comparisons
  - **Series table** with latest MoM/YoY per (Country, Category)

---

## 🗂 Project Structure

    hicp_app/
    ├─ main.py          # Entry point: page setup, data loading, KPIs, tab wiring
    ├─ helpers.py       # Theme, palettes, flags, legend table, scrollable plot helper
    ├─ filters.py       # Sidebar UI + filtering logic
    ├─ tabs.py          # All chart/tab rendering functions
    ├─ data/
    │  └─ data hicp.csv # Your CSV (see format below)
    ├─ flags/           # Optional country PNGs: eu.png, germany.png, italy.png, ...
    ├─ requirements.txt
    └─ README.md

> If you rename the CSV, update `DATA_PATH` in `main.py`.

---

## 📦 Requirements & Setup

**requirements.txt**
    
    streamlit>=1.34
    pandas>=2.0
    numpy>=1.24
    plotly>=5.20
    pillow>=10.0   # optional, only for embedding flag PNGs

**Install**

    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # macOS/Linux
    source .venv/bin/activate

    pip install -r requirements.txt

---

## 📑 CSV Format (required columns)

The app expects **monthly index** data (2015=100) with these exact columns:

| Column          | Meaning                                |
|-----------------|----------------------------------------|
| `[Year]`        | Year (e.g., 2024)                      |
| `[Month]`       | Month number (1–12)                    |
| `[geo]`         | Country/region code                    |
| `[GeoName]`     | Country/region display name            |
| `[COICOP]`      | COICOP code                            |
| `[COICOP_Name]` | COICOP display name                    |
| `[Value]`       | HICP Index (2015=100)                  |

`main.py` renames them to: `year, month, geo, geo_name, coicop, coicop_name, index` and builds a MonthStart `date`.  
Extreme rates are nulled (guardrails): `abs(mom) > 500` or `abs(yoy) > 500`.

---

## ▶️ Run

    streamlit run main.py

Open the printed local URL (usually http://localhost:8501).

---

## 🧭 How to Use

1. Pick a **date range**, **countries**, and **categories** from the sidebar.
2. Toggle **Separate by Country** / **Separate by Category**:
   - **Both ON** → **Columns = Categories**, **Rows = Countries** (scrollable if large)
   - **Country only** → Facet by Country
   - **Category only** → Facet by Category
   - **Both OFF** → Single overlay; multiple categories use category colors + dashes by country
3. Review **KPIs**, switch tabs for **Monthly**, **Annual**, **Index**, and **Latest** views.
4. Use the **Series table** and **Download** buttons to export data.


---


## 🚀 Quick Start

    git clone https://github.com/<your-user>/<your-repo>.git
    cd <your-repo>
    python -m venv .venv && . .venv/Scripts/activate  # Windows
    # or: source .venv/bin/activate                    # macOS/Linux
    pip install -r requirements.txt
    # Put your CSV at: data/data hicp.csv
    streamlit run main.py

Enjoy exploring EU inflation!
