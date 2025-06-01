import streamlit as st
import pandas as pd
import warnings
import os
from src.average_carrier_delay import average_carrier_delay, load_and_prepare_data

# Set page config
st.set_page_config(page_title="U.S. Flight Delay Analysis (2013-2023)", layout="wide")

st.markdown(
    """
    <div style='
    '>
        <h1 style='margin-top: 0;'>✈️ U.S. Flight Delay Dashboard Analysis</h1>
        <h2 style='font-size: 24px; font-weight: bold;'>
            Carrier Delay Analysis
        </h2>
    </div>
    """,
    unsafe_allow_html=True
)


# Read csv file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "..", "src", "dataset", "Airline_Delay_Cause_Data_Processing.csv")
df = load_and_prepare_data(csv_path)

st.write("")
st.write("")

# Airline academic years from 2013/2014 to 2022/2023
valid_years = [f"{y}/{ y +1}" for y in range(2013, 2023)]  # ['2013/2014', ..., '2022/2023']

st.markdown("<h2 style='font-size: 16px;'>Select Year Range (based on end year)</h2>", unsafe_allow_html=True)

# Slider from 2014 to 2023 (which maps to indices 0 to 9 of valid_years)
selected_years_int = st.slider(
    "",
    min_value=2014,
    max_value=2023,
    value=(2014, 2023),
    step=1
)

# Map 2014–2023 to "2013/2014"–"2022/2023"
start_index = selected_years_int[0] - 2014  # e.g. 2014 -> 0
end_index = selected_years_int[1] - 2014    # e.g. 2023 -> 9
selected_years = valid_years[start_index:end_index + 1]
st.write(f"Selected Years: {selected_years[0]} to {selected_years[-1]}")

st.write("")

## Graph 4: Daftar Rata-rata Keterlambatan penerbangan per maskapai
average_carrier_delay(df, selected_years)