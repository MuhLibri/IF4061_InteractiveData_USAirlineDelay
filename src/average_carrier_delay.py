import streamlit as st
import plotly.express as px
import pandas as pd
from src.utils import get_airline_year

@st.cache_data(show_spinner=False)
def compute_carrier_avg_delay(df):
    return (
        df.groupby('carrier_name')['arr_del15_percentage']
        .mean()
        .sort_values()
    )

@st.cache_data(show_spinner=False)
def filter_data_by_year(df, selected_years):
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    return df[df['airline_year'].isin(selected_years)]

@st.cache_data(show_spinner=False)
def load_and_prepare_data(path):
    df = pd.read_csv(path)
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    return df

def average_carrier_delay(df, selected_years):
    df = filter_data_by_year(df, selected_years)
    st.markdown("<h2 style='font-size: 24px;'>List of Average Flight Delays by Carriers</h2>", unsafe_allow_html=True)

    # Compute and cache average delay per carrier
    carrier_avg_delay = compute_carrier_avg_delay(df)

    selected_data = carrier_avg_delay.sort_values(ascending=False)

    # Compute overall average
    overall_avg = carrier_avg_delay.mean()

    # Display metric
    st.metric(label="Overall Average Delay", value=f"{overall_avg:.2f}%")

    df_plot = selected_data.reset_index()
    df_plot.columns = ['Carrier', 'AvgDelayPercent']

    # Plot
    fig = px.bar(
        df_plot,
        x='Carrier',
        y='AvgDelayPercent',
        text='AvgDelayPercent',
        labels={'AvgDelayPercent': 'Average % of Arrival Delays'},
        color='AvgDelayPercent',
        color_continuous_scale='Blues',
        template='plotly_white',
        height=450
    )

    fig.update_traces(
        texttemplate='%{text:.2f}%',
        textposition='outside',
        marker_line_color='darkgray',
        marker_line_width=1.5,
        hovertemplate='<b>%{x}</b><br>Delay Percentage: <b>%{y:.2f}%</b><extra></extra>'
    )

    fig.update_layout(
        yaxis_range=[0, df_plot['AvgDelayPercent'].max() * 1.2],
        font=dict(family="Segoe UI", size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=40, l=40, r=20),
    )

    st.plotly_chart(fig, use_container_width=True)