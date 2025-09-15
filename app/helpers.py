# helpers.py  — theme, colors, flags, legend-table, utilities
from __future__ import annotations
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

try:
    from PIL import Image  # used for embedding flag PNGs
except Exception:
    Image = None
# helpers.py
import streamlit.components.v1 as components

def plot_scrollable(fig, *, cols=1, rows=1, cell_w=340, cell_h=260, extra_h=140):
    """
    Render a Plotly figure inside a scrollable container.
    cols/rows: number of facet columns/rows to size the canvas.
    """
    # Give each facet a reasonable cell size
    width  = max(1100, int(cols * cell_w) + 120)
    height = max(520,  int(rows * cell_h) + int(extra_h))

    # Fix the figure size so Plotly doesn't auto-shrink
    fig.update_layout(width=width, height=height)

    # Embed the figure HTML inside a scrollable DIV
    html = fig.to_html(include_plotlyjs="cdn", full_html=False)
    components.html(
        f"""
        <div style="overflow:auto; width:100%; border:1px solid #eee; border-radius:8px;">
          <div style="width:{width}px; height:{height}px;">{html}</div>
        </div>
        """,
        height=min(height + 50, 1400),
        scrolling=True,
    )
def _facet_grid_dims(sep_countries, sep_categories, eff_geos, eff_cats):
    """
    Return (rows, cols) matching the facet layout we draw:
      - both on  -> rows=countries, cols=categories
      - only country -> rows=1, cols=countries
      - only category -> rows=1, cols=categories
      - none -> 1x1
    """
    if sep_countries and sep_categories:
        return len(eff_geos), len(eff_cats)
    if sep_countries:
        return 1, len(eff_geos)
    if sep_categories:
        return 1, len(eff_cats)
    return 1, 1

# ----- Colors (flag-inspired for countries) -----
COUNTRY_FLAG_COLORS = {
    "EU": "#003399", "France": "#0055A4", "Germany": "#FFCE00",
    "Italy": "#009246", "Netherlands": "#21468B", "Poland": "#DC143C", "Spain": "#AA151B",
}

CATEGORY_COLOR_SEQ = (
    px.colors.qualitative.Set2
    + px.colors.qualitative.Safe
    + px.colors.qualitative.D3
)

def setup_theme() -> None:
    pio.templates["eu_theme"] = go.layout.Template(
        layout=go.Layout(
            font=dict(family="Inter, Roboto, system-ui, -apple-system, Segoe UI", size=13, color="#111"),
            title=dict(x=0.0, xanchor="left", font=dict(size=18, color="#003399")),
            paper_bgcolor="white",
            plot_bgcolor="white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(showline=True, linecolor="#D0D0D0", gridcolor="#EAEAEA", zeroline=False),
            yaxis=dict(showline=False, gridcolor="#EAEAEA", zeroline=True, zerolinecolor="#D0D0D0"),
            hoverlabel=dict(bgcolor="white", font=dict(color="#111")),
            margin=dict(t=70, r=20, l=60, b=60),
        )
    )
    pio.templates.default = "eu_theme"

def country_color_map(df, country_col: str = "geo_name"):
    values = sorted(df[country_col].astype(str).unique())
    return {c: COUNTRY_FLAG_COLORS.get(c, "#666666") for c in values}

COUNTRY_FLAG_EMOJI = {"EU":"🇪🇺","France":"🇫🇷","Germany":"🇩🇪","Italy":"🇮🇹","Netherlands":"🇳🇱","Poland":"🇵🇱","Spain":"🇪🇸"}
def with_flag(name: str) -> str:
    return f"{COUNTRY_FLAG_EMOJI.get(name, '')} {name}".strip()

def legend_bottom(fig):
    fig.update_layout(
        legend=dict(orientation="h", y=-0.22, yanchor="top", x=0, xanchor="left"),
        margin=dict(b=max((fig.layout.margin.b or 80), 110)),
    )
    return fig

# ----- Flag strip & legend-table helpers -----
def _country_slug(name: str) -> str:
    return (
        str(name).lower()
        .replace(" ", "_").replace("-", "_")
        .replace("(", "").replace(")", "").replace("/", "_")
    )

def add_flag_strip(fig, country_names, folder="flags", y=-0.34, size=0.08, per_row=8):
    """Draw small flags under the legend. PNGs should be in ./flags/<country>.png ."""
    if not country_names:
        return fig
    fig.update_layout(margin=dict(b=max((fig.layout.margin.b or 80), 150)))
    if Image is None:
        return fig  # silently skip if Pillow isn't available

    x0, gap = 0.02, 0.11
    row = col = 0
    for name in sorted(set(country_names)):
        slug = _country_slug(name)
        path = os.path.join(folder, f"{slug}.png")
        if not os.path.isfile(path):
            continue
        try:
            img = Image.open(path)
        except Exception:
            continue

        xr = x0 + col * gap
        yr = y - row * (size + 0.08)
        col += 1
        if col >= per_row:
            col = 0
            row += 1

        fig.add_layout_image(dict(source=img, xref="paper", yref="paper",
                                  x=xr, y=yr + size, sizex=size, sizey=size,
                                  xanchor="left", yanchor="top", layer="above"))
        fig.add_annotation(
            xref="paper", yref="paper", x=xr + size + 0.01, y=yr + size/2,
            text=name, showarrow=False, xanchor="left", yanchor="middle",
            font=dict(size=12, color="#111"), bgcolor="rgba(255,255,255,0.0)"
        )
    return fig

def _category_color_map(categories):
    return {cat: CATEGORY_COLOR_SEQ[i % len(CATEGORY_COLOR_SEQ)] for i, cat in enumerate(categories)}

def render_country_category_matrix(countries, categories, color_mode="category", flags_folder="flags"):
    """
    Under-chart "legend table":
      - one column per country (flag shown if found)
      - rows = categories, with color swatch matching the chart
    """
    if not countries or not categories:
        return
    cols = st.columns(len(countries))
    cat_colors = _category_color_map(categories)
    for i, country in enumerate(countries):
        with cols[i]:
            path = os.path.join(flags_folder, f"{_country_slug(country)}.png")
            if os.path.isfile(path):
                st.image(path, width=28)
            st.markdown(f"**{country}**")
            for cat in categories:
                color = cat_colors[cat] if color_mode == "category" else COUNTRY_FLAG_COLORS.get(country, "#666666")
                st.markdown(
                    f"""
                    <div style="display:flex;align-items:center;margin:2px 0;">
                      <span style="width:10px;height:10px;background:{color};
                                   display:inline-block;border-radius:50%;
                                   margin-right:8px;"></span>
                      <span style="font-size:0.92rem;">{cat}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

def series_summary_table(df):
    """Latest MoM/YoY per (Country, Category) with suggested flag path."""
    latest = df.sort_values("date").groupby(["geo_name", "coicop_name"], as_index=False).tail(1).copy()
    tbl = latest[["geo_name","coicop_name","Monthly inflation rate","Annual inflation rate","date"]].rename(columns={
        "geo_name":"Country/Regions","coicop_name":"Categories",
        "Monthly inflation rate":"Monthly rate (%)","Annual inflation rate":"Annual rate (%)",
        "date":"Latest month",
    })
    def flag_path(name: str) -> str:
        return f"flags/{_country_slug(name)}.png"
    tbl["Flag PNG (put file here)"] = tbl["Country/Regions"].astype(str).apply(flag_path)
    return tbl.sort_values(["Country/Regions","Categories"]).reset_index(drop=True)
