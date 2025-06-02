import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from src.utils import get_airline_year
from src.state_utils import state_abbrev_to_name, state_coords

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