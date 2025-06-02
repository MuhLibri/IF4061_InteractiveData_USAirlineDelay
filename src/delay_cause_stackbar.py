import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils import get_airline_year, format_with_dots  # Ensure this is imported from utils

def delay_cause_stacked_bar(df, selected_years):
    year_range = f"{selected_years[0]}" if selected_years[0] == selected_years[-1] else f"{selected_years[0]} - {selected_years[-1]}"
    st.markdown(f"<h2 style='font-size: 24px;'>Yearly Breakdown of Flight Delay Causes<br><span style='font-size: 20px;'>({year_range})</span></h2>", unsafe_allow_html=True)
    
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
    yearly_data = df.groupby("airline_year")[[c[0] for c in delay_causes] + ["arr_flights"]].sum().reset_index()
    yearly_data = yearly_data.sort_values("airline_year")

    # Calculate total delays for percentage calculation
    yearly_data["total_delays"] = yearly_data[[c[0] for c in delay_causes]].sum(axis=1)

    # Calculate delay percentage per cause per year (per batang/tahun)
    for col, _, _ in delay_causes:
        yearly_data[col + '_pct'] = (yearly_data[col] / yearly_data['arr_flights']) * 100

    # Create stacked bar chart (y = persentase delay, hover: total delay & % per batang)
    fig = go.Figure()
    for col, label, color in delay_causes:
        formatted_values = yearly_data[col].apply(format_with_dots)
        percentages = yearly_data[col + '_pct']
        customdata = np.stack([formatted_values, percentages.round(2)], axis=-1)
        fig.add_trace(go.Bar(
            x=yearly_data["airline_year"],
            y=percentages,
            name=label,
            marker_color=color,
            meta=[label] * len(yearly_data),
            customdata=customdata,
            hovertemplate=(
                '<b>%{x}</b><br>'
                '<b>%{meta}</b><br>'
                'Total Delay: <b>%{customdata[0]}</b><br>'
                'Percentage (of all flights): <b>%{customdata[1]:.2f}%</b><extra></extra>'
            )
        ))

    fig.update_layout(
        barmode='stack',
        xaxis=dict(title="Year", tickangle=45),
        yaxis=dict(title="Percentage of Flight Delays (%)"),
        height=600,
        margin=dict(t=60, b=40, l=40, r=40),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        ),
    )

    st.plotly_chart(fig, use_container_width=True)
