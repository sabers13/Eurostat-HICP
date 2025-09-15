# filters.py — sidebar UI & filtering
from __future__ import annotations
import streamlit as st
import pandas as pd

ALLOWED = {"EU","France","Germany","Italy","Netherlands","Poland","Spain"}

def build_sidebar(df):
    with st.sidebar:
        st.header("Filters")
        months = df["date"].dt.to_period("M").astype(str).sort_values().unique().tolist()
        m_from, m_to = st.select_slider("Date range (month)", options=months, value=(months[0], months[-1]))
        dr_start = pd.Period(m_from, "M").to_timestamp(how="start")
        dr_end   = pd.Period(m_to,   "M").to_timestamp(how="end")

        geos_all = sorted(df["geo_name"].cat.categories.tolist())
        geos = [g for g in geos_all if g in ALLOWED]
        cats = sorted(df["coicop_name"].cat.categories.tolist())

        default_geo = ["EU"] if "EU" in geos else ([geos[0]] if geos else [])
        default_cat = ["All-items HICP"] if "All-items HICP" in cats else ([cats[0]] if cats else [])

        sel_geos = st.multiselect("Countries/Regions", geos, default=default_geo)
        sel_cats = st.multiselect("Categories (COICOP)", cats, default=default_cat)
        separate_countries  = st.checkbox("Separate by Country", value=False)
        separate_categories = st.checkbox("Separate by Category", value=False)

    eff_geos = sel_geos or geos
    eff_cats = sel_cats or cats

    return dict(
        dr_start=dr_start, dr_end=dr_end,
        eff_geos=eff_geos, eff_cats=eff_cats,
        separate_countries=separate_countries,
        separate_categories=separate_categories,
    )

def apply_filters(df, params):
    mask = (
        df["date"].between(params["dr_start"], params["dr_end"])
        & df["geo_name"].isin(params["eff_geos"])
        & df["coicop_name"].isin(params["eff_cats"])
    )
    return df.loc[mask].copy()
