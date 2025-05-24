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

# -----------------------------------------------------------------------------------------------------
## Graph 3: Proporsi Penyebab Keterlambatan Penerbangan
delay_cause_proportion(df)
# -----------------------------------------------------------------------------------------------------

st.write("")
st.write("")

# -----------------------------------------------------------------------------------------------------
## Graph 4: Daftar Rata-rata Keterlambatan penerbangan per maskapai
average_carrier_delay(df)
# -----------------------------------------------------------------------------------------------------