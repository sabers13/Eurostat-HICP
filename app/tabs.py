# tabs.py — all charts
from __future__ import annotations
import plotly.express as px
import streamlit as st
from helpers import (
    country_color_map,
    CATEGORY_COLOR_SEQ,
    legend_bottom,
    render_country_category_matrix,
    with_flag,
    COUNTRY_FLAG_COLORS,
    plot_scrollable,
    _facet_grid_dims,
)


def _line_chart_logic(f, ycol, title, separate_countries, separate_categories, eff_geos, eff_cats):
    f_plot = f.copy()
    cmap_countries = country_color_map(f_plot, "geo_name")
    multi_cats = len(eff_cats) > 1

    if separate_countries and separate_categories:
        # Columns = Categories, Rows = Countries  ✅
        fig = px.line(
            f_plot, x="date", y=ycol,
            color="geo_name",                # keep country colors
            facet_col="coicop_name",        # columns by Category
            facet_row="geo_name",           # rows by Country
            markers=True,
            color_discrete_map=cmap_countries,
            title=title,
            labels={"geo_name":"Country/Regions","coicop_name":"Categories","date":"Date"},
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        color_mode = "country"

    elif separate_countries and not separate_categories:
        fig = px.line(
            f_plot, x="date", y=ycol, color="coicop_name",
            facet_col="geo_name", facet_col_wrap=2, markers=True,
            color_discrete_sequence=CATEGORY_COLOR_SEQ, title=title,
            labels={"coicop_name":"Categories","geo_name":"Country/Regions","date":"Date"},
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        color_mode = "category"

    elif separate_categories and not separate_countries:
        fig = px.line(
            f_plot, x="date", y=ycol, color="geo_name",
            facet_col="coicop_name", facet_col_wrap=2, markers=True,
            color_discrete_map=cmap_countries, title=title,
            labels={"geo_name":"Country/Regions","coicop_name":"Categories","date":"Date"},
        )
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
        color_mode = "country"

    else:
        if multi_cats:
            fig = px.line(
                f_plot, x="date", y=ycol,
                color="coicop_name", line_dash="geo_name", symbol="geo_name",
                markers=True, color_discrete_sequence=CATEGORY_COLOR_SEQ, title=title,
                labels={"geo_name":"Country/Regions","coicop_name":"Categories","date":"Date"},
            )
            color_mode = "category"
        else:
            fig = px.line(
                f_plot, x="date", y=ycol,
                color="geo_name", markers=True, color_discrete_map=cmap_countries, title=title,
                labels={"geo_name":"Country/Regions","coicop_name":"Categories","date":"Date"},
            )
            color_mode = "country"

    fig.update_layout(height=520, legend=dict(orientation="h", y=-0.22, yanchor="top", x=0, xanchor="left"),
                      margin=dict(t=60, b=110))
    return fig, color_mode

def render_tab_annual(f, eff_geos, eff_cats, separate_countries, separate_categories):
    fig, color_mode = _line_chart_logic(
        f, "Annual inflation rate", "Annual inflation rate (YoY %)",
        separate_countries, separate_categories, eff_geos, eff_cats
    )

    # Facet annotation cleanup when both dims are used
    if separate_countries and separate_categories:
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], textangle=0))

    # decide scroll vs normal
    rows, cols = _facet_grid_dims(separate_countries, separate_categories, eff_geos, eff_cats)
    use_scroll = (rows >= 3) or (cols >= 4) or (rows * cols >= 10)

    if use_scroll:
        plot_scrollable(fig, cols=cols, rows=rows)
    else:
        st.plotly_chart(fig, use_container_width=True)

    render_country_category_matrix(eff_geos, eff_cats, color_mode=color_mode)

def render_tab_monthly(f, eff_geos, eff_cats, separate_countries, separate_categories):
    fig, color_mode = _line_chart_logic(
        f, "Monthly inflation rate", "Monthly inflation rate (MoM %)",
        separate_countries, separate_categories, eff_geos, eff_cats
    )
    if separate_countries and separate_categories:
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], textangle=0))

    rows, cols = _facet_grid_dims(separate_countries, separate_categories, eff_geos, eff_cats)
    use_scroll = (rows >= 3) or (cols >= 4) or (rows * cols >= 10)

    if use_scroll:
        plot_scrollable(fig, cols=cols, rows=rows)
    else:
        st.plotly_chart(fig, use_container_width=True)

    render_country_category_matrix(eff_geos, eff_cats, color_mode=color_mode)

def render_tab_index(f, eff_geos, eff_cats, separate_countries, separate_categories):
    fig, color_mode = _line_chart_logic(
        f, "index", "Index (2015=100)",
        separate_countries, separate_categories, eff_geos, eff_cats
    )
    if separate_countries and separate_categories:
        fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1], textangle=0))

    rows, cols = _facet_grid_dims(separate_countries, separate_categories, eff_geos, eff_cats)
    use_scroll = (rows >= 3) or (cols >= 4) or (rows * cols >= 10)

    if use_scroll:
        plot_scrollable(fig, cols=cols, rows=rows)
    else:
        st.plotly_chart(fig, use_container_width=True)

    render_country_category_matrix(eff_geos, eff_cats, color_mode=color_mode)

def render_tab_latest_by_country(f):
    f_flag = f.copy()
    f_flag["geo_label"] = f_flag["geo_name"].astype(str).apply(with_flag)
    last = f_flag.sort_values("date").groupby(["geo_label","coicop_name"], as_index=False).tail(1)
    fig = px.bar(
        last, x="geo_label", y="Annual inflation rate",
        color="coicop_name", barmode="group",
        title="Latest Annual inflation rate — grouped by Category",
        labels={"geo_label":"Country/Regions","coicop_name":"Categories"},
    )
    legend_bottom(fig)
    st.plotly_chart(fig, use_container_width=True)

def render_tab_by_category_latest(f):
    f_flag = f.copy()
    f_flag["geo_label"] = f_flag["geo_name"].astype(str).apply(with_flag)
    last_cat = f_flag.sort_values("date").groupby(["coicop_name","geo_name"], as_index=False).tail(1)
    cmap = {g: COUNTRY_FLAG_COLORS.get(g, "#666666") for g in last_cat["geo_name"].unique()}
    fig = px.bar(
        last_cat, x="coicop_name", y="Annual inflation rate",
        color="geo_name", color_discrete_map=cmap, barmode="group",
        title="Annual inflation rate by Category (latest month)",
        labels={"coicop_name":"Categories","geo_name":"Country/Regions"},
    )
    # show flags in legend
    for tr in fig.data:
        tr.name = with_flag(tr.name)
        tr.legendgroup = tr.name
    legend_bottom(fig)
    st.plotly_chart(fig, use_container_width=True)
