import streamlit as st
import pandas as pd
import warnings
import os

st.set_page_config(page_title="Airliner Comparison", layout="wide")

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
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(BASE_DIR, "..", "src", "dataset", "Airline_Delay_Cause_Data_Processing.csv")
df = pd.read_csv(csv_path)

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

# Optional: Show the mapped academic years
st.write(f"Selected Airline Years: {selected_years[0]} to {selected_years[-1]}")

st.write("")
st.write("")
