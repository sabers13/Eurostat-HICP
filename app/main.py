# main.py — entry point
from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

from helpers import setup_theme, series_summary_table
from filters import build_sidebar, apply_filters
from tabs import (
    render_tab_annual, render_tab_monthly, render_tab_index,
    render_tab_latest_by_country, render_tab_by_category_latest
)

st.set_page_config(page_title="EU HICP Dashboard", layout="wide")
setup_theme()

DATA_PATH = Path("data") / "data hicp.csv"

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False, encoding="utf-8", on_bad_lines="skip")
    df = df.rename(columns={
        "[Year]":"year","[Month]":"month","[geo]":"geo","[GeoName]":"geo_name",
        "[COICOP]":"coicop","[COICOP_Name]":"coicop_name","[Value]":"index",
    })
    required = {"year","month","geo","geo_name","coicop","coicop_name","index"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {sorted(missing)}")

    df["year"]  = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["month"] = pd.to_numeric(df["month"], errors="coerce").astype("Int64")
    df["index"] = pd.to_numeric(df["index"], errors="coerce")
    df = df.dropna(subset=["year","month","index"]).copy()

    df["date"] = pd.to_datetime(dict(year=df["year"].astype(int),
                                     month=df["month"].astype(int), day=1))
    df = df.sort_values(["geo","coicop","date"]).reset_index(drop=True)
    g = df.groupby(["geo","coicop"], sort=False, dropna=False)
    prev1, prev12 = g["index"].shift(1), g["index"].shift(12)
    df["mom_%"] = (df["index"]/prev1 - 1.0) * 100.0
    df["yoy_%"] = (df["index"]/prev12 - 1.0) * 100.0
    df.loc[df["mom_%"].abs() > 500, "mom_%"] = np.nan
    df.loc[df["yoy_%"].abs() > 500, "yoy_%"] = np.nan

    for c in ["geo","geo_name","coicop","coicop_name"]:
        df[c] = df[c].astype("category")
    return df

df = load_data(DATA_PATH)

# ---- Page header ----
st.title("EU HICP Dashboard")
st.caption("Index 2015=100. Rates computed from index per (Country/Regions, Categories).")

# ---- Filters ----
params = build_sidebar(df)
f = apply_filters(df, params)
if f.empty:
    st.warning("No data for the selected filters.")
    st.stop()


f["Monthly inflation rate"] = f["mom_%"]
f["Annual inflation rate"]  = f["yoy_%"]

# ---- KPIs ----
latest_date = f["date"].max()
latest = f[f["date"] == latest_date]
kpi_annual  = latest["Annual inflation rate"].mean()
kpi_monthly = latest["Monthly inflation rate"].mean()

k1, k2, k3 = st.columns(3)
k1.metric("Latest month", latest_date.strftime("%Y-%m"))
k2.metric("Avg Annual inflation rate (selection)", f"{kpi_annual:,.2f}%")
k3.metric("Avg Monthly inflation rate (selection)", f"{kpi_monthly:,.2f}%")

# ---- Tabs ----
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Annual inflation rate by Date and Country",
    "Monthly inflation rate by Date and Country",
    "Index by Date and Country",
    "Latest annual rate by Country",
    "By Category (annual rate)",
    "Series table"
])

with tab1:
    render_tab_annual(f, params["eff_geos"], params["eff_cats"],
                      params["separate_countries"], params["separate_categories"])

with tab2:
    render_tab_monthly(f, params["eff_geos"], params["eff_cats"],
                       params["separate_countries"], params["separate_categories"])

with tab3:
    render_tab_index(f, params["eff_geos"], params["eff_cats"],
                     params["separate_countries"], params["separate_categories"])

with tab4:
    render_tab_latest_by_country(f)

with tab5:
    render_tab_by_category_latest(f)

# ---- Raw filtered table + download ----
st.subheader("Data (filtered)")
table = (
    f[["date","geo_name","coicop_name","index","Monthly inflation rate","Annual inflation rate"]]
      .rename(columns={"date":"Date","geo_name":"Country/Regions",
                       "coicop_name":"Categories","index":"Index (2015=100)"})
      .sort_values(["Date","Country/Regions","Categories"])
)
st.dataframe(table, use_container_width=True, hide_index=True)
st.download_button("Download filtered CSV",
                   data=table.to_csv(index=False).encode("utf-8"),
                   file_name="hicp_filtered.csv", mime="text/csv")
