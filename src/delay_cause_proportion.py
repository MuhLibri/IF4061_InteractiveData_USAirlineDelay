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

    # Get cached values
    yearly_totals, label_map = compute_delay_sums(df)

    # Dropdown year selector
    years_options = ["All"] + sorted([str(year) for year in df['year'].unique()])
    selected_year = st.selectbox("Select Year", years_options)

    # Get delay totals for selected year
    delay_total = yearly_totals[selected_year]
    labels = [label_map[col] for col in delay_total.index]
    values = delay_total.values
    formatted_values = [format_with_dots(v) for v in values]
    title = f"Delay Causes for {selected_year}" if selected_year != "All" else "Delay Causes for All Years"

    # Define color palette
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']

    # Compute percent manually with 2f formatting
    percentages = (values / np.sum(values)) * 100
    custom_labels = [f"<b>{label}</b><br>{percent:.2f}%" for label, percent in zip(labels, percentages)]

    # Create donut chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        text=custom_labels,
        textinfo='text',  # use custom text instead of label+percent
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