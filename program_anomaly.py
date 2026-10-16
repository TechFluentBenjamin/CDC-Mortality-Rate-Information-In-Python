import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def run_anomaly():
    # Import the data and read it.
    url = "https://data.cdc.gov/api/views/v6ab-adf5/" "rows.csv?accessType=DOWNLOAD"

    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Death Rate"] = pd.to_numeric(df["Death Rate"], errors="coerce")

    df = df.dropna(subset=["Year", "Age Group", "Death Rate"]).copy()

    df["Year"] = df["Year"].astype(int)

    # Sort years within each age group
    df = df.sort_values(["Age Group", "Year"])

    # Calculate each age group's quartiles
    groups = df.groupby("Age Group")["Death Rate"]

    q1 = groups.transform("quantile", q=0.25)
    q3 = groups.transform("quantile", q=0.75)

    iqr = q3 - q1

    df["Lower Threshold"] = q1 - 1.5 * iqr
    df["Upper Threshold"] = q3 + 1.5 * iqr

    df["Anomaly"] = (df["Death Rate"] < df["Lower Threshold"]) | (
        df["Death Rate"] > df["Upper Threshold"]
    )

    # Confirm the required columns are still present
    print("Columns after anomaly detection:")
    print(df.columns.tolist())

    print("\nAge groups found:")
    print(df["Age Group"].unique())

    # Create chart for each age group.

    from plotly.subplots import make_subplots
    import plotly.graph_objects as go

    age_order = ["1-4 Years", "5-9 Years", "10-14 Years", "15-19 Years"]

    # Keep only age groups that actually exist in the dataset
    age_groups = [age for age in age_order if age in df["Age Group"].unique()]
    fig = make_subplots(
        rows=len(age_groups),
        cols=1,
        subplot_titles=[f"Age Group: {age}" for age in age_groups],
        vertical_spacing=0.06,
    )

    for i, age in enumerate(age_groups, start=1):

        subset = df[df["Age Group"] == age].sort_values("Year")
        anomalies = subset[subset["Anomaly"]]

        # Historical death-rate line
        fig.add_trace(
            go.Scatter(
                x=subset["Year"],
                y=subset["Death Rate"],
                mode="lines",
                name=f"{age} - Death Rate",
                line=dict(width=2),
                showlegend=False,
                hovertemplate=(
                    "Year: %{x}<br>"
                    "Death Rate: %{y:,.1f}"
                    "<extra>" + age + "</extra>"
                ),
            ),
            row=i,
            col=1,
        )

        # Red markers for anomalies
        fig.add_trace(
            go.Scatter(
                x=anomalies["Year"],
                y=anomalies["Death Rate"],
                mode="markers",
                name=f"{age} - Anomaly",
                marker=dict(
                    color="red",
                    size=9,
                    symbol="circle",
                    line=dict(color="white", width=1),
                ),
                showlegend=False,
                hovertemplate=(
                    "ANOMALY<br>"
                    "Year: %{x}<br>"
                    "Death Rate: %{y:,.1f}"
                    "<extra>" + age + "</extra>"
                ),
            ),
            row=i,
            col=1,
        )

        fig.update_yaxes(title_text="Death Rate", rangemode="tozero", row=i, col=1)

    fig.update_xaxes(title_text="Year", row=len(age_groups), col=1)

    fig.update_layout(
        title="CDC Mortality Rate Anomaly Dashboard",
        height=300 * len(age_groups),
        template="plotly_white",
        hovermode="closest",
    )

    fig.show()

    # Save the multi-chart dashboard
    fig.write_html("cdc_all_age_groups_dashboard.html")

    print("Saved: cdc_all_age_groups_dashboard.html")

    # Display the anomalies in a table and save them to a CSV file for further analysis. This allows users to easily identify and investigate unusual death rates across different age groups and years.

    anomalies = df[df["Anomaly"]].copy()

    anomalies = anomalies.sort_values("Death Rate", ascending=False)

    print("\nNumber of observations:", len(df))
    print("Number of flagged anomalies:", len(anomalies))

    print("\nMost extreme flagged observations:")
    print(
        anomalies[
            ["Year", "Age Group", "Death Rate", "Lower Threshold", "Upper Threshold"]
        ]
        .head(20)
        .to_string(index=False)
    )

    anomalies.to_csv("cdc_anomalies.csv", index=False)

    df.to_csv("cdc_data_with_anomalies.csv", index=False)

    fig.write_html("cdc_anomaly_detector.html")

    print("\nFiles saved:")
    print("- cdc_anomalies.csv")
    print("- cdc_data_with_anomalies.csv")
    print("- cdc_anomaly_detector.html")


if __name__ == "__main__":
    run_anomaly()
