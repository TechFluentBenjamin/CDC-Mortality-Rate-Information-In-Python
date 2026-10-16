import pandas as pd
import numpy as np
import plotly.express as px


def run_bubbles():
    # This downloads the data from the CDC website and creates an animated bubble chart of death rates by age group over time.
    url = "https://data.cdc.gov/api/views/v6ab-adf5/" "rows.csv?accessType=DOWNLOAD"

    df = pd.read_csv(url)

    # This cleans the columns names and converts the data types to appropriate formats for analysis.
    df.columns = df.columns.str.strip()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Death Rate"] = pd.to_numeric(df["Death Rate"], errors="coerce")

    df = df.dropna(subset=["Year", "Age Group", "Death Rate"]).copy()

    df["Year"] = df["Year"].astype(int)

    # This organizes the ages in a range.
    age_order = ["1-4 Years", "5-9 Years", "10-14 Years", "15-19 Years"]

    # Keep only age groups in the expected order
    # that actually appear in the data
    age_order = [age for age in age_order if age in df["Age Group"].unique()]

    df = df[df["Age Group"].isin(age_order)].copy()

    # This changes the bubble size to be proportional to the square root of the death rate, which makes the bubbles more visually comparable.
    df["Bubble Size"] = np.sqrt(df["Death Rate"].clip(lower=0))

    # Axis needs to be a little higher than the max death rate to avoid cutting off the top of the bubbles.
    y_max = df["Death Rate"].max() * 1.08

    # The bubble chart is created using Plotly Express, with the x-axis representing age groups, the y-axis representing death rates, and the size of the bubbles representing the square root of the death rate. The chart is animated over time, with each frame representing a different year.
    fig = px.scatter(
        df,
        x="Age Group",
        y="Death Rate",
        size="Bubble Size",
        color="Age Group",
        animation_frame="Year",
        animation_group="Age Group",
        hover_name="Age Group",
        hover_data={"Year": True, "Death Rate": ":,.1f", "Bubble Size": False},
        category_orders={"Age Group": age_order, "Year": sorted(df["Year"].unique())},
        size_max=65,
        range_x=[-0.5, len(age_order) - 0.5],
        range_y=[0, y_max],
        title="CDC Death Rates by Age Group Over Time",
        labels={"Age Group": "Age Group", "Death Rate": "Death Rate", "Year": "Year"},
        template="plotly_white",
    )

    # And a better appearance too!
    fig.update_layout(
        title_x=0.5,
        title_font_size=22,
        xaxis_title="Age Group",
        yaxis_title="Death Rate",
        legend_title="Age Group",
        height=650,
        font=dict(size=13),
    )

    fig.update_traces(marker=dict(opacity=0.8, line=dict(width=1, color="white")))

    # Smooth out the animation by adjusting the frame and transition durations. The frame duration controls how long each frame is displayed, while the transition duration controls how long it takes to transition between frames.
    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 150

    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 100

    # Display the chart in an interactive window. This allows users to explore the data by hovering over the bubbles to see detailed information about each age group and year.
    fig.show()

    # 11. Save an interactive HTML version
    fig.write_html("cdc_animated_bubble_chart.html")

    print("Saved as cdc_animated_bubble_chart.html")


if __name__ == "__main__":
    run_bubbles()
