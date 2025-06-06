import streamlit as st
import pandas as pd
import warnings

from src.trend_flight_year import trend_flight_year
from src.delay_cause_proportion import delay_cause_proportion
from src.delay_cause_stackbar import delay_cause_stacked_bar

warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(page_title="U.S. Flight Delay Analysis (2013-2023)", layout="wide")

# Title and description
st.markdown(
    """
    <div style='
    '>
        <h1 style='margin-top: 0;'>✈️ U.S. Flight Delay Dashboard Analysis</h1>
        <h2 style='font-size: 24px; font-weight: bold;'>
            Delay Cause Trend Analysis
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)

# Read csv file
@st.cache_data
def load_data():
    return pd.read_csv('src/dataset/Airline_Delay_Cause_Data_Processing.csv')

df = load_data()

st.write("")
st.write("")

# Airline academic years from 2013/2014 to 2022/2023
valid_years = [f"{y}/{y+1}" for y in range(2013, 2023)]  # ['2013/2014', ..., '2022/2023']

st.markdown("<h2 style='font-size: 16px;'>Select Year Range (based on end year)</h2>", unsafe_allow_html=True)

# Slider from 2014 to 2023 (which maps to indices 0 to 9 of valid_years)
selected_years_int = st.slider(
    "Enter range here",
    min_value=2014,
    max_value=2023,
    value=(2014, 2023),
    step=1
)

# Map 2014–2023 to "2013/2014"–"2022/2023"
start_index = selected_years_int[0] - 2014  # e.g. 2014 -> 0
end_index = selected_years_int[1] - 2014    # e.g. 2023 -> 9
selected_years = valid_years[start_index:end_index + 1]

# Optional: Show the mapped academic years
st.write(f"Selected Years: {selected_years[0]} to {selected_years[-1]}")

st.write("")

# -----------------------------------------------------------------------------------------------------
col1, col2 = st.columns(2)
# -----------------------------------------------------------------------------------------------------

## Graph 1: Tren Penyebab Keterlambatan Penerbangan per Tahun
with col1:
    trend_flight_year(df, selected_years)
# -----------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------
## Graph 2: Tren Penyebab Keterlambatan Penerbangan per Bulan
with col2:
    delay_cause_proportion(df, selected_years)
# -----------------------------------------------------------------------------------------------------


# -----------------------------------------------------------------------------------------------------
## Graph 3: Stacked Bar Chart Penyebab Keterlambatan per Tahun
delay_cause_stacked_bar(df, selected_years)
# -----------------------------------------------------------------------------------------------------