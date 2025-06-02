import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.utils import format_with_dots, get_airline_year

@st.cache_data(show_spinner=False)
def compute_delay_sums(df, selected_years):
        # Add airline year column
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    df = df[df['airline_year'].isin(selected_years)]
    
    if df.empty:
        st.warning("No data available for the selected year range.")
        return

    # Remove 2023/2024 data
    df = df[df['airline_year'] != "2023/2024"]

    # Select only airline years from 2013/2014 to 2022/2023
    allowed_years = [f"{y}/{y+1}" for y in range(2013, 2023)]
    df = df[df['airline_year'].isin(allowed_years)]

    # --- Horizontal Stacked Bar Chart (Most Recent Year Only) ---
    latest_airline_year = sorted(df['airline_year'].unique())[-1]
    recent_data = df[df['airline_year'] == latest_airline_year]

    grouped = recent_data.groupby('airline_year')[['carrier_ct', 'late_aircraft_ct', 'nas_ct', 'weather_ct', 'security_ct']].sum()
    percentages = grouped.div(grouped.sum(axis=1), axis=0) * 100
    
    return percentages, latest_airline_year, selected_years

def delay_cause_proportion(df, selected_years):
    # --- Preprocess Data ---
    percentages, latest_airline_year, selected_years = compute_delay_sums(df, selected_years)

    delay_causes = [
        ('carrier_ct', 'Carrier', '#636EFA'),
        ('weather_ct', 'Weather', '#EF553B'),
        ('nas_ct', 'NAS (National Airspace System)', '#00CC96'),
        ('security_ct', 'Security', '#AB63FA'),
        ('late_aircraft_ct', 'Late Aircraft', '#FFA15A'),
    ]

    # --- Horizontal Stacked Bar (Most Recent Year Only) ---
    bar_fig = go.Figure()
    for col, label, color in delay_causes:
        pct = percentages[col].values[0]
        bar_fig.add_trace(go.Bar(
            y=percentages.index,
            x=[pct],
            name=label,
            orientation='h',
            marker_color=color,
            text=[f'<b>{label}</b><br>{pct:.2f}%'],
            textposition='inside',
            insidetextanchor='middle',
            meta=label,
            hovertemplate=(
                '<b>%{y}</b><br>'
                '<b>%{meta}</b><br>'
                'Delay Percentage: <b>%{x:.2f}%</b><extra></extra>'
            ),
        ))

    bar_fig.update_layout(
        barmode='stack',
        title=dict(text=f"Delay Cause Proportions for Latest Year ({latest_airline_year})", font=dict(size=12)),
        xaxis=dict(title='Percentage', range=[0, 100], ticksuffix='%'),
        yaxis=dict(title=''),
        height=121,
        showlegend=False,
        margin=dict(t=20, l=20, r=20, b=0),
    )

    st.plotly_chart(bar_fig, use_container_width=True)

    # --- Pie Chart: Based on selected_years ---
    year_range = f"{selected_years[0]}" if selected_years[0] == selected_years[-1] else f"{selected_years[0]} - {selected_years[-1]}"
    st.markdown(f"<h2 style='font-size: 24px;'>Delay Cause Proportions Trend Across Years<br><span style='font-size: 20px;'>({year_range})</span></h2>", unsafe_allow_html=True)

    # Filter df again (to use it for the pie chart)
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    df = df[df['airline_year'].isin(selected_years)]
    
    if df.empty:
        st.warning("No data available for the pie chart.")
        return

    delay_total = df[["carrier_ct", "weather_ct", "nas_ct", "security_ct", "late_aircraft_ct"]].sum()
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
    colors = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
    percentages = (values / np.sum(values)) * 100
    custom_labels = [f"<b>{label}</b><br>{percent:.2f}%" for label, percent in zip(labels, percentages)]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors, line=dict(color='white', width=0.5)),
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
        margin=dict(t=0, b=20, l=0, r=0),  # Increase top margin for legend space
        height=330,
        legend=dict(
            orientation="h", 
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig, use_container_width=True)