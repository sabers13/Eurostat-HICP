# Eurostat HICP – Power BI Dashboard

**What it shows:** Inflation trends (EU, country, COICOP) with YoY/MoM, weights, drilldowns.

**Skills used:** Power Query (M), DAX (CALCULATE, TIMEINTELLIGENCE), star schema design, model optimization.

## Data
- Source: Eurostat HICP (free/open)
- Sample file included for reproduction; full data pulled via Power Query.

## Key Measures (DAX)
```DAX
YoY % = DIVIDE([This Year Value]-[Last Year Value], [Last Year Value])
MoM % = DIVIDE([This Month Value]-[Prev Month Value], [Prev Month Value])
