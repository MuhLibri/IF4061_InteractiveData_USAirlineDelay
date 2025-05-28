import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils import format_with_dots


@st.cache_data(show_spinner=False)
def compute_delay_sums(df):
    label_map = {
        "carrier_ct": "Carrier",
        "weather_ct": "Weather",
        "nas_ct": "NAS (National Airspace System)",
        "security_ct": "Security",
        "late_aircraft_ct": "Late Aircraft"
    }

    # Precompute totals for each year and overall
    yearly_totals = {
        str(year): df[df['year'] == year][list(label_map.keys())].sum()
        for year in df['year'].unique()
    }
    yearly_totals["All"] = df[list(label_map.keys())].sum()

    return yearly_totals, label_map


def delay_cause_proportion(df):
    st.markdown(
        "<h2 style='font-size: 24px;'>Proportion of Delay Causes</h2>",
        unsafe_allow_html=True
    )

    # Define year range
    min_year, max_year = int(df['year'].min()), int(df['year'].max())

    # Create slider for selecting 2-year interval
    selected_range = st.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(2013, 2023),
        step=1
    )

    # Filter DataFrame by selected year range
    df_filtered = df[(df['year'] >= selected_range[0]) & (df['year'] <= selected_range[1])]

    # Recompute totals after filtering
    delay_total = df_filtered[["carrier_ct", "weather_ct", "nas_ct", "security_ct", "late_aircraft_ct"]].sum()

    label_map = {
        "carrier_ct": "Carrier",
        "weather_ct": "Weather",
        "nas_ct": "NAS (National Airspace System)",
        "security_ct": "Security",
        "late_aircraft_ct": "Late Aircraft"
    }

    labels = [label_map[col] for col in delay_total.index]
    values = delay_total.values
    formatted_values = [format_with_dots(v) for v in values]
    title = f"Delay Causes from {selected_range[0]} to {selected_range[1]}"

    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
    percentages = (values / np.sum(values)) * 100
    custom_labels = [f"<b>{label}</b><br>{percent:.2f}%" for label, percent in zip(labels, percentages)]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        text=custom_labels,
        textinfo='text',
        customdata=formatted_values,
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Total Delay: <b>%{customdata}</b><br>'
            'Percentage: <b>%{percent:.2%}</b><extra></extra>'
        )
    )])

    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=20),
            x=0.5,
            xanchor='center'
        ),
        margin=dict(t=50, b=20, l=20, r=20),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
