import streamlit as st
import pandas as pd
import warnings

from src.trend_flight_year import trend_flight_year
from src.trend_flight_month import trend_flight_month
from src.delay_cause_proportion import delay_cause_proportion
from src.average_carrier_delay import average_carrier_delay

warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(page_title="Analysis of U.S. Flight Data (2013-2023)", layout="wide")

# Title and description
st.markdown(
    """
    <div style='
    '>
        <h1 style='margin-top: 0;'>✈️ US Airline Flight Delay Dashboard</h1>
        
    </div>
    """,
    unsafe_allow_html=True
)

# Read csv file
df = pd.read_csv('src/dataset/Airline_Delay_Cause_Data_Processing.csv')

st.write("")
st.write("")


# -----------------------------------------------------------------------------------------------------
col1, col2 = st.columns(2)
# -----------------------------------------------------------------------------------------------------
## Graph 1: Tren Penyebab Keterlambatan Penerbangan per Tahun
with col1:
    trend_flight_year(df)
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
## Graph 2: Tren Penyebab Keterlambatan Penerbangan per Bulan
with col2:
    trend_flight_month(df)
# -----------------------------------------------------------------------------------------------------

st.write("")
st.write("")

col3, col4 = st.columns([0.4, 0.6], gap="large")
# -----------------------------------------------------------------------------------------------------
## Graph 3: Proporsi Penyebab Keterlambatan Penerbangan
with col3:
    delay_cause_proportion(df)
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
## Graph 4: Daftar Rata-rata Keterlambatan penerbangan per maskapai
with col4:
    average_carrier_delay(df)
# -----------------------------------------------------------------------------------------------------