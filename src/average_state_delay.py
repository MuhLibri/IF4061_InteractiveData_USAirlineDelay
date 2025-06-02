import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.utils import format_with_dots, get_airline_year

# Dictionary to map state abbreviation to full name
state_abbrev_to_name = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'DC': 'District of Columbia', 'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii',
    'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
    'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine',
    'MD': 'Maryland', 'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota',
    'MS': 'Mississippi', 'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska',
    'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico',
    'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
    'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island',
    'SC': 'South Carolina', 'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas',
    'UT': 'Utah', 'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington',
    'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
    'PR': 'Puerto Rico', 'VI': 'Virgin Islands', 'TT': 'Trust Territories'
}

state_coords = {
    'AL': [32.7794, -86.8287], 'AK': [64.0685, -152.2782],
    'AZ': [34.2744, -111.6602], 'AR': [34.8938, -92.4426],
    'CA': [37.1841, -119.4696], 'CO': [38.9972, -105.5478],
    'CT': [41.6219, -72.7273], 'DE': [38.9896, -75.5050],
    'DC': [38.9101, -77.0147], 'FL': [29.6305, -82.4497],
    'GA': [32.6415, -83.4426], 'HI': [20.2927, -156.3737],
    'ID': [44.3509, -114.6130], 'IL': [40.0417, -89.1965],
    'IN': [39.8942, -86.2816], 'IA': [42.0751, -93.4960],
    'KS': [38.4937, -98.3804], 'KY': [37.5347, -85.3021],
    'LA': [31.7689, -92.3968], 'ME': [45.3695, -69.2428],
    'MD': [39.0550, -76.7909], 'MA': [42.2596, -71.8083],
    'MI': [43.3467, -84.7102], 'MN': [46.2807, -94.3053],
    'MS': [32.7364, -89.6678], 'MO': [38.3566, -92.4580],
    'MT': [47.0527, -109.6333], 'NE': [41.5378, -99.7951],
    'NV': [39.3289, -116.6312], 'NH': [43.6805, -71.5811],
    'NJ': [40.1907, -74.6728], 'NM': [34.4071, -106.1126],
    'NY': [42.9538, -75.5268], 'NC': [35.5557, -79.3877],
    'ND': [47.4501, -100.4659], 'OH': [40.2862, -82.7937],
    'OK': [35.5889, -97.4943], 'OR': [43.9336, -120.5583],
    'PA': [40.8781, -77.7996], 'RI': [41.6762, -71.5562],
    'SC': [33.9169, -80.8964], 'SD': [44.4443, -100.2263],
    'TN': [35.8580, -86.3505], 'TX': [31.4757, -99.3312],
    'UT': [39.3055, -111.6703], 'VT': [44.0687, -72.6658],
    'VA': [37.5215, -78.8537], 'WA': [47.3826, -120.4472],
    'WV': [38.6409, -80.6227], 'WI': [44.6243, -89.9941],
    'WY': [42.9957, -107.5512]
}

@st.cache_data(show_spinner=False)
def compute_state_avg_delay(df):
    return (
        df.groupby('airport_state')['arr_del15_percentage']
        .mean()
        .reset_index()
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

def average_state_delay(df, selected_years):
    year_range = f"{selected_years[0]}" if selected_years[0] == selected_years[-1] else f"{selected_years[0]} - {selected_years[-1]}"

    # Filter berdasarkan tahun
    filtered_df = filter_data_by_year(df, selected_years)
    
    # Hitung rata-rata keterlambatan per state
    state_delay = compute_state_avg_delay(filtered_df)

    # Tambahkan nama lengkap negara bagian
    state_delay['airport_state_full'] = state_delay['airport_state'].map(state_abbrev_to_name)

    # Overview metrics
    highest_state_row = state_delay.loc[state_delay['arr_del15_percentage'].idxmax()]
    lowest_state_row = state_delay.loc[state_delay['arr_del15_percentage'].idxmin()]
    overall_avg = state_delay['arr_del15_percentage'].mean()

    # Custom styled metrics, no border, improved spacing, white text except red/green
    col1, col2, col3 = st.columns([1, 1, 1], gap="large")

    with col1:
        st.markdown(
            f"""
            <div style='padding: 0 24px 8px 0; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:2px;'>Average Delay Percentage</div>
                <div style='font-size:2.2em; font-weight:bold; color:#fff;'>{overall_avg:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style='padding: 0 24px 8px 0; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:2px;'>Highest Delay Percentage State</div>
                <div style='font-size:1.2em; font-weight:bold; color:#d62728;'>{highest_state_row['airport_state_full']} ({highest_state_row['airport_state']})</div>
                <div style='font-size:1.2em; color:#d62728;'>{highest_state_row['arr_del15_percentage']:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div style='padding: 0 24px 8px 0; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:2px;'>Lowest Delay Percentage State</div>
                <div style='font-size:1.2em; font-weight:bold; color:#2ca02c;'>{lowest_state_row['airport_state_full']} ({lowest_state_row['airport_state']})</div>
                <div style='font-size:1.2em; color:#2ca02c;'>{lowest_state_row['arr_del15_percentage']:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(f"<h2 style='font-size: 24px;'>List of Average Flight Delays by States<br><span style='font-size: 20px;'>({year_range})</span></h2>", unsafe_allow_html=True)

    # Buat visualisasi choropleth
    choropleth = go.Choropleth(
        locations=state_delay['airport_state'],
        z=state_delay['arr_del15_percentage'],
        locationmode='USA-states',
        colorscale='Blues',
        colorbar_title='Average % of Arrival Delays',
        customdata=state_delay[['airport_state_full', 'airport_state']],
        hovertemplate='<b>%{customdata[0]} (%{customdata[1]})</b><br>Delay Percentage: <b>%{z:.2f}%</b><extra></extra>',
    )

    # Add state abbreviations as scattergeo
    scatter_text = go.Scattergeo(
        locationmode='USA-states',
        lon=[state_coords[abbr][1] for abbr in state_delay['airport_state'] if abbr in state_coords],
        lat=[state_coords[abbr][0] for abbr in state_delay['airport_state'] if abbr in state_coords],
        text=[abbr for abbr in state_delay['airport_state'] if abbr in state_coords],
        mode='text',
        textfont=dict(color='black', size=10),
        showlegend=False,
        hoverinfo='skip'
    )

    fig = go.Figure(data=[choropleth, scatter_text])

    fig.update_layout(
        geo=dict(
            scope='usa',
            projection=dict(type='albers usa'),
            showlakes=False,
            lakecolor='rgba(0,0,0,0)',
            bgcolor='rgba(0,0,0,0)',
            showframe=False,
            showcoastlines=False,
        ),
        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True)