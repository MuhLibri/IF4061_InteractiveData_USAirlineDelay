import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils import format_with_dots


def delay_cause_proportion(df):
    st.markdown("<h2 style='font-size: 24px;'>Proportion of Delay Causes by Year</h2>", unsafe_allow_html=True)

    # Define mapping of column names to readable labels
    label_map = {
        "carrier_ct": "Carrier",
        "weather_ct": "Weather",
        "nas_ct": "NAS (National Airspace System)",
        "security_ct": "Security",
        "late_aircraft_ct": "Late Aircraft"
    }

    # Get the list of years and add "All" option
    years = sorted(df['year'].unique())
    years_options = ["All"] + [str(year) for year in years]

    # Streamlit dropdown (selectbox)
    selected_year = st.selectbox("Select Year", years_options)

    if selected_year == "All":
        # Aggregate all years
        delay_total = df[list(label_map.keys())].sum()
        title = "Delay Causes for All Years"
    else:
        year = int(selected_year)
        df_year = df[df['year'] == year]
        delay_total = df_year[list(label_map.keys())].sum()
        title = f"Delay Causes for {year}"

    labels = [label_map[col] for col in delay_total.index]
    values = delay_total.values
    formatted_values = [format_with_dots(val) for val in values]

    # Create pie chart without trace name
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        hovertemplate='<b>Cause = %{label}</b><br>Total Delay = %{customdata}<br>Percentage = %{percent}<extra></extra>',
        customdata=formatted_values,
        name=""  # This prevents 'trace 0' from showing
    )])

    fig.update_layout(title=title)

    # Display chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)