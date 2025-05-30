import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils import get_airline_year, format_with_dots  # Ensure this is imported from utils

def delay_cause_stacked_bar(df, selected_years):
    st.markdown("<h2 style='font-size: 24px;'>Stacked Trend of Total Flight Delays by Cause</h2>", unsafe_allow_html=True)

    delay_causes = [
        ("carrier_ct", "Carrier", "#636EFA"),
        ("weather_ct", "Weather", "#EF553B"),
        ("nas_ct", "NAS (National Airspace System)", "#00CC96"),
        ("security_ct", "Security", "#AB63FA"),
        ("late_aircraft_ct", "Late Aircraft", "#FFA15A")
    ]

    # Add airline year
    df["airline_year"] = df.apply(get_airline_year, axis=1)
    df = df[df["airline_year"].isin(selected_years)]

    if df.empty:
        st.warning("No data available for the selected year range.")
        return

    # Group and sort
    yearly_data = df.groupby("airline_year")[[c[0] for c in delay_causes]].sum().reset_index()
    yearly_data = yearly_data.sort_values("airline_year")

    # Create stacked bar chart
    fig = go.Figure()
    for col, label, color in delay_causes:
        # Format values for hovertemplate
        formatted_values = yearly_data[col].apply(format_with_dots)

        fig.add_trace(go.Bar(
            x=yearly_data["airline_year"],
            y=yearly_data[col],
            name=label,
            marker_color=color,
            meta=[label] * len(yearly_data),
            customdata=formatted_values,
            hovertemplate=(
                '<b>%{x}</b><br>'
                '<b>%{meta}</b><br>'
                'Total Delays: <b>%{customdata}</b><extra></extra>'
            )
        ))

    fig.update_layout(
        barmode='stack',
        xaxis=dict(title="Year", tickangle=45),
        yaxis=dict(title="Number of Delays", tickformat=","),
        height=500,
        margin=dict(t=60, b=40, l=40, r=40),  # increase top margin for legend spacing
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,  # position legend slightly above the plot
            xanchor="center",
            x=0.5
        ),
    )

    st.plotly_chart(fig, use_container_width=True)
