import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def run_dashboard():
    url = "https://data.cdc.gov/api/views/v6ab-adf5/" "rows.csv?accessType=DOWNLOAD"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()

    required_columns = ["Year", "Age Group", "Death Rate"]

    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            f"Columns found: {df.columns.tolist()}"
        )

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Death Rate"] = pd.to_numeric(df["Death Rate"], errors="coerce")

    df = df.dropna(subset=["Year", "Age Group", "Death Rate"]).copy()

    df["Year"] = df["Year"].astype(int)

    df = df.sort_values(["Age Group", "Year"])

    # Ensure one observation per age group and year.
    duplicates = df.duplicated(subset=["Age Group", "Year"], keep=False)

    if duplicates.any():
        raise ValueError(
            "Duplicate Year/Age Group combinations found. "
            "Inspect the source data before calculating changes."
        )

#age group ordering
    preferred_order = ["1-4 Years", "5-9 Years", "10-14 Years", "15-19 Years"]

    age_groups = [age for age in preferred_order if age in df["Age Group"].unique()]

    # Include any additional age groups in the source file.
    age_groups += [age for age in df["Age Group"].unique() if age not in age_groups]

    df["Age Group"] = pd.Categorical(
        df["Age Group"], categories=age_groups, ordered=True
    )

    df = df.sort_values(["Age Group", "Year"]).copy()

#Rate of change calculations

    grouped = df.groupby("Age Group", observed=True)["Death Rate"]

    previous_rate = grouped.shift(1)
    previous_year = df.groupby("Age Group", observed=True)["Year"].shift(1)

    # Only compare consecutive calendar years.
    consecutive = df["Year"].eq(previous_year + 1)

    # Absolute annual change
    df["Annual Change"] = (df["Death Rate"] - previous_rate).where(consecutive)

    # Percentage change
    valid_previous = previous_rate.where(consecutive & previous_rate.ne(0))

    df["Annual Change (%)"] = (
        (df["Death Rate"] - previous_rate) / valid_previous
    ) * 100

    # Five-year rolling average of original death rates.
    df["5-Year Average"] = df.groupby("Age Group", observed=True)[
        "Death Rate"
    ].transform(lambda s: s.rolling(window=5, min_periods=5).mean())

#Annual precentage change chart code
    fig_change = go.Figure()

    for age in age_groups:
        subset = df[df["Age Group"] == age]

        fig_change.add_trace(
            go.Scatter(
                x=subset["Year"],
                y=subset["Annual Change (%)"],
                mode="lines",
                name=age,
                connectgaps=False,
                hovertemplate=(
                    "Year: %{x}<br>" "Change: %{y:.2f}%" "<extra>" + age + "</extra>"
                ),
            )
        )

    fig_change.add_hline(y=0, line_dash="dash", line_color="gray")

    fig_change.update_layout(
        title="CDC Mortality: Annual Percentage Change",
        xaxis_title="Year",
        yaxis_title="Change from Previous Year (%)",
        template="plotly_white",
        hovermode="x unified",
        height=650,
    )

    fig_change.show()

#Rolling average chart code

    fig_average = go.Figure()

    for age in age_groups:
        subset = df[df["Age Group"] == age]

    fig_average.add_trace(
        go.Scatter(
            x=subset["Year"],
            y=subset["Death Rate"],
            mode="lines",
            line=dict(width=1, dash="dot"),
            opacity=0.35,
            name=f"{age} - Annual Rate",
            connectgaps=False,
        )
    )

    fig_average.add_trace(
        go.Scatter(
            x=subset["Year"],
            y=subset["5-Year Average"],
            mode="lines",
            line=dict(width=3),
            name=f"{age} - 5-Year Average",
            connectgaps=False,
        )
    )

    fig_average.update_layout(
        title="CDC Mortality: Five-Year Rolling Average",
        xaxis_title="Year",
        yaxis_title="Death Rate",
        template="plotly_white",
        hovermode="x unified",
        height=650,
    )

    fig_average.show()

#Heat map code

    heatmap_data = df.pivot(
        index="Age Group", columns="Year", values="Annual Change (%)"
    ).reindex(age_groups)

    # Symmetric color limits make positive and negative
    # changes easier to compare.
    values = heatmap_data.to_numpy(dtype=float)
    finite_values = values[np.isfinite(values)]

    if len(finite_values) > 0:
        color_limit = np.percentile(np.abs(finite_values), 95)
        if color_limit == 0:
            color_limit = 1
    else:
        color_limit = 1

    fig_heatmap = go.Figure(
        data=go.Heatmap(
            z=heatmap_data.to_numpy(dtype=float),
            x=heatmap_data.columns,
            y=heatmap_data.index.astype(str),
            colorscale="RdBu",
            zmid=0,
            zmin=-color_limit,
            zmax=color_limit,
            colorbar=dict(title="Annual Change (%)"),
            hovertemplate=(
                "Age Group: %{y}<br>"
                "Year: %{x}<br>"
                "Change: %{z:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig_heatmap.update_layout(
        title="CDC Mortality: Annual Percentage Change Heatmap",
        xaxis_title="Year",
        yaxis_title="Age Group",
        template="plotly_white",
        height=400,
    )

    fig_heatmap.show()

#Export results to CSV and HTML files for further analysis or sharing.
    df["Age Group"] = df["Age Group"].astype(str)

    df.to_csv("cdc_rate_of_change_results.csv", index=False)

    fig_change.write_html("cdc_annual_percentage_change.html")

    fig_average.write_html("cdc_five_year_rolling_average.html")

    fig_heatmap.write_html("cdc_rate_of_change_heatmap.html")

    print("\nAnalysis complete!")
    print("Age groups:", age_groups)
    print("Observations analyzed:", len(df))
    print(
        "Annual percentage changes calculated:", df["Annual Change (%)"].notna().sum()
    )

    print("\nFiles created:")
    print("- cdc_rate_of_change_results.csv")
    print("- cdc_annual_percentage_change.html")
    print("- cdc_five_year_rolling_average.html")
    print("- cdc_rate_of_change_heatmap.html")


if __name__ == "__main__":
    run_dashboard()
