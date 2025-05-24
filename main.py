import streamlit as st
import plotly.express as px
import pandas as pd
import time
import warnings

from src.trend_flight_year import trend_flight_year
from src.trend_flight_month import trend_flight_month
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(page_title="Analysis of U.S. Flight Data (2013-2023)", layout="wide")

## Title Introduction and Description
# Title
st.title("✈️ US Airline Flight Delay Dashboard")

# Add caption
st.markdown(
    """
    <p style='font-size:17px; color:white;'>
    United States is one of the busiest countries in the world when it comes to air travel services. Every year, millions of flights are operated by various Carriers across numerous airports throughout the country. With such a high volume of air traffic, it is not uncommon for the U.S. aviation system to face challenges, particularly those related to flight delays.
    <br><br>
    To gain a deeper understanding of the flight delays situation in the United States, let’s explore the following data.
    </p>
    """,
    unsafe_allow_html=True
)

# Read csv file
df = pd.read_csv('src/dataset/Airline_Delay_Cause_Data_Processing.csv')

st.write("")
st.write("")

# -----------------------------------------------------------------------------------------------------
## Graph 1: Tren Penyebab Keterlambatan Penerbangan per Tahun
trend_flight_year(df)
# -----------------------------------------------------------------------------------------------------

st.write("")
st.write("")

# -----------------------------------------------------------------------------------------------------
## Graph 2: Tren Penyebab Keterlambatan Penerbangan per Bulan
trend_flight_month(df)
# -----------------------------------------------------------------------------------------------------

st.write("")
st.write("")


## Graph 2: Daftar rata-rata keterlambatan penerbangan per maskapai
# Compute average delay by carrier
carrier_avg_delay = df.groupby('carrier_name')['arr_del15_percentage'].mean().sort_values()

# Radiobutton options
st.markdown("<h2 style='font-size: 24px;'>Daftar Rata-rata Keterlambatan penerbangan per maskapai</h2>", unsafe_allow_html=True)
option = st.radio(
    "View Options:",
    ["Show All", "Top 5 Carriers with Highest Delay", "Top 5 Carriers with Lowest Delay", ]
)

# Chart container
chart_placeholder = st.empty()

# Filter data
if option == "Show All":
    selected_data = carrier_avg_delay.sort_values(ascending=False)
elif option == "Top 5 Carriers with Highest Delay":
    selected_data = carrier_avg_delay.tail(5).sort_values(ascending=False)
elif option == "Top 5 Carriers with Lowest Delay":
    selected_data = carrier_avg_delay.head(5)

# Build Plotly DataFrame
df_plot = selected_data.reset_index()
df_plot.columns = ['Carrier', 'AvgDelayPercent']

# Create Plotly bar chart
fig = px.bar(
    df_plot,
    x='Carrier',
    y='AvgDelayPercent',
    text='AvgDelayPercent',
    labels={'AvgDelayPercent': 'Average % of Arrival Delays'},
    color='AvgDelayPercent',
    color_continuous_scale='Blues',
    template='plotly_white',
    height=500
)

fig.update_traces(
    texttemplate='%{text:.2f}%',
    textposition='outside',
    marker_line_color='darkgray',
    marker_line_width=1.5,
    hovertemplate='<b>%{x}</b><br>Delay: %{y:.2f}%<extra></extra>'
)

fig.update_layout(
    xaxis_tickangle=-30,
    yaxis_range=[0, df_plot['AvgDelayPercent'].max() * 1.2],
    font=dict(family="Segoe UI", size=14),
    plot_bgcolor='rgba(0,0,0,0)',
    margin=dict(t=0, b=40, l=40, r=20),
    transition_duration=500
)

# Optional tiny delay to simulate smooth update
time.sleep(0.1)

# Show chart in placeholder
chart_placeholder.plotly_chart(fig, use_container_width=True)