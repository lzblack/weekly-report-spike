import marimo

app = marimo.App(width="medium")


@app.cell
def _():
    from datetime import datetime, timezone

    import altair as alt
    import marimo as mo
    import polars as pl
    import requests

    return alt, datetime, mo, pl, requests, timezone


@app.cell
def _(pl, requests):
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": 42.30,
            "longitude": -71.27,
            "daily": "temperature_2m_max,precipitation_sum",
            "past_days": 7,
            "forecast_days": 0,
            "timezone": "America/New_York",
        },
        timeout=30,
    )
    response.raise_for_status()
    week = pl.DataFrame(response.json()["daily"]).with_columns(
        pl.col("time").str.to_date()
    )
    week
    return (week,)


@app.cell
def _(datetime, mo, timezone, week):
    warmest = week.sort("temperature_2m_max", descending=True).row(0, named=True)
    mo.md(
        f"""
        # Babson weather, week ending {week["time"].max()}

        Warmest day: **{warmest["time"]}** at {warmest["temperature_2m_max"]} °C.
        Rain this week: **{week["precipitation_sum"].sum():.1f} mm**.

        Generated {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC.
        """
    )
    return


@app.cell
def _(alt, mo, week):
    mo.ui.altair_chart(
        alt.Chart(week)
        .mark_bar()
        .encode(
            x=alt.X("time:T", title="Day"),
            y=alt.Y("temperature_2m_max", title="High (°C)"),
        )
        .properties(title="Daily high, last seven days", width=500)
    )
    return


if __name__ == "__main__":
    app.run()
