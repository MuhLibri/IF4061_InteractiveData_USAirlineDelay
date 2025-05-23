import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import time
import warnings
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
df = pd.read_csv('Airline_Delay_Cause_Data_Processing.csv')

# Show raw data
st.write("")  # adds a small gap
# === Chart Title ===
st.markdown("<h2 style='font-size: 24px;'>Show Raw Head Data</h2>", unsafe_allow_html=True)
st.dataframe(df.head())
st.write("")  # adds a small gap


# -----------------------------------------------------------------------------------------------------


## Graph 1: Tren Penyebab Keterlambatan Penerbangan per Tahun
# Grouped data
delay_yearly = df.groupby('year')[[
    'carrier_delay', 'weather_delay', 'nas_delay', 'security_delay', 'late_aircraft_delay'
]].sum().reset_index()

# === Chart Title ===
st.markdown("<h2 style='font-size: 24px;'>Tren Penyebab Keterlambatan Penerbangan per Tahun</h2>", unsafe_allow_html=True)

# Label mapping: internal → readable
label_map = {
    "carrier_delay": "Carrier",
    "weather_delay": "Weather",
    "nas_delay": "NAS (National Airspace System)",
    "security_delay": "Security",
    "late_aircraft_delay": "Late Aircraft"
}

# Inverse label map: readable → internal
reverse_label_map = {v: k for k, v in label_map.items()}

# CHOOSE BETWEEN DROPDOWN OR MULTISELECT
# Dropdown options
readable_delay_types = list(label_map.values())
options_dropdown = ['Show All'] + readable_delay_types

selected_option = st.selectbox("Pilih Penyebab Keterlambatan:", options_dropdown)

# Determine selected internal column names
if selected_option == 'Show All':
    selected_causes = list(label_map.keys())
else:
    selected_causes = [reverse_label_map[selected_option]]
    
# Multiselect options
# readable_delay_types = list(label_map.values())
# selected_options = st.multiselect(
#     "Pilih Penyebab Keterlambatan:",
#     options=readable_delay_types,
#     default=readable_delay_types  # Preselect all
# )

# # Determine selected internal column names
# if not selected_options:
#     st.warning("Pilih minimal satu penyebab untuk menampilkan grafik.")
#     st.stop()

# selected_causes = [reverse_label_map[option] for option in selected_options]


# Melt using original column names
df_melt = delay_yearly.melt(
    id_vars='year',
    value_vars=selected_causes,
    var_name='Penyebab',
    value_name='Menit_Delay'
)

# Apply readable labels for plotting
df_melt['Penyebab'] = df_melt['Penyebab'].map(label_map)

# Fixed color mapping using readable names
color_map = {
    'Carrier': '#1f77b4',
    'Weather': '#ff7f0e',
    'NAS (National Airspace System)': '#2ca02c',
    'Security': '#d62728',
    'Late Aircraft': '#9467bd'
}

# Plot
fig = px.line(
    df_melt,
    x='year',
    y='Menit_Delay',
    color='Penyebab',
    markers=True,
    color_discrete_map=color_map
)

# Update layout
fig.update_layout(
    margin=dict(t=10, b=40, l=40, r=20)
)

# Update x-axis
st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------------------------------


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