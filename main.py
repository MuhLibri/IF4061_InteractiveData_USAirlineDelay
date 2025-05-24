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
        border: 2px solid #CCCCCC;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 75px;
    '>
        <h1 style='margin-top: 0;'>✈️ US Airline Flight Delay Dashboard</h1>
        <p style='font-size:17px; margin-bottom: 28px;'>
            United States is one of the busiest countries in the world when it comes to air travel services.
            Every year, millions of flights are operated by various carriers across numerous airports throughout the country.
            With such a high volume of air traffic, it is not uncommon for the U.S. aviation system to face challenges,
            particularly those related to flight delays.
            <br><br>
            To gain a deeper understanding of the flight delays situation in the United States, let’s explore the following data.
        </p>
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
st.write("")
st.write("")
st.write("")


# -----------------------------------------------------------------------------------------------------
## Graph 3: Proporsi Penyebab Keterlambatan Penerbangan
delay_cause_proportion(df)
# -----------------------------------------------------------------------------------------------------


st.write("")
st.write("")
st.write("")
st.write("")


# -----------------------------------------------------------------------------------------------------
## Graph 4: Daftar Rata-rata Keterlambatan penerbangan per maskapai
average_carrier_delay(df)
# -----------------------------------------------------------------------------------------------------