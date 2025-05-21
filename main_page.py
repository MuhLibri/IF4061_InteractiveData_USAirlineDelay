import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Analysis of U.S. Flight Data (2013-2023)", layout="wide")

df = pd.read_csv('Airline_Delay_Cause.csv')

delay_yearly = df.groupby('year')[[
    'carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay'
]].sum().reset_index()

df_melt = delay_yearly.melt(id_vars='year', var_name='Penyebab', value_name='Menit_Delay')

fig = px.line(df_melt, x='year', y='Menit_Delay', color='Penyebab', markers=True,
              title='Tren Penyebab Keterlambatan Penerbangan per Tahun')

st.plotly_chart(fig)