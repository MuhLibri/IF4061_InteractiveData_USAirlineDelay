import streamlit as st
import plotly.express as px

from src.utils import format_with_dots, get_airline_year

## Graph 1: Tren Penyebab Keterlambatan Penerbangan per Tahun
@st.cache_data
def preprocess_delay_data(df):
    df['airline_year'] = df.apply(get_airline_year, axis=1)

    df['total_delay'] = df[
        ['carrier_ct', 'weather_ct', 'nas_ct', 'security_ct', 'late_aircraft_ct']
    ].sum(axis=1)

    total_delay = df.groupby('airline_year')['total_delay'].sum().reset_index()
    total_flights = df.groupby('airline_year')['arr_flights'].sum().reset_index()
    
    percentage_of_delay_flights = (total_delay['total_delay'] / total_flights['arr_flights']) * 100

    # Remove incomplete final year if applicable
    if total_delay['airline_year'].iloc[-1] == '2023/2024':
        percentage_of_delay_flights = percentage_of_delay_flights[:-1]

    return total_delay, total_flights, percentage_of_delay_flights

def trend_flight_year(df, selected_years):
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    df = df[df['airline_year'].isin(selected_years)]

    total_delay, total_flights, percentage_of_delay_flights = preprocess_delay_data(df)

    merged_df = total_delay.copy()
    merged_df['total_flights'] = total_flights['arr_flights']
    merged_df['percentage'] = percentage_of_delay_flights
    merged_df['pct_change'] = merged_df['percentage'].pct_change() * 100
    merged_df['hover_pct'] = merged_df['percentage'].map(lambda x: f"{x:.2f}%")
    merged_df['Type'] = 'Delay Percentage'

    if len(merged_df) < 2:
        st.warning("Not enough years selected to compute trends.")
        return

    recent_year = merged_df.iloc[-1]
    previous_year = merged_df.iloc[-2]

    # Extract last year for labeling
    recent_label_year = recent_year['airline_year'].split('/')[-1]
    
    # Calculate delta (gain/loss) from previous year
    previous_year = merged_df.iloc[-2]
    delta_percentage = recent_year['percentage'] - previous_year['percentage']
    delta_delay = recent_year['total_delay'] - previous_year['total_delay']
    delta_flights = recent_year['total_flights'] - previous_year['total_flights']
    
    # === Top Metrics ===
    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Recent Year",
        f"{recent_year['airline_year']}",
        f"{delta_percentage:.2f}% from previous year"
    )
    col2.metric(f"Total Delay Flights ({recent_label_year})", format_with_dots(recent_year['total_delay']), format_with_dots(delta_delay) + " from previous year")
    col3.metric(f"Total Overall Flights ({recent_label_year})", format_with_dots(recent_year['total_flights']), format_with_dots(delta_flights) + " from previous year")
    
    st.write("")
    st.write("")
    st.write("")
    st.write("")
    
    st.markdown("<h2 style='font-size: 24px;'>Delay Flights Percentage By Year</h2>", unsafe_allow_html=True)

    # === Line Chart ===
    fig = px.line(
        merged_df,
        x='airline_year',
        y='percentage',
        markers=True,
        color='Type',
        hover_data={'hover_pct': True, 'percentage': False, 'Type': False},
        height=350
    )
    fig.update_traces(
        hovertemplate=
            'Year: <b>%{x}</b><br>'
            'Delay Percentage: <b>%{customdata[0]}<extra></extra></b>'
    )
    fig.update_layout(
        xaxis_title="Year",
        yaxis_title="Percentage of Delay Flights (%)",
        margin=dict(t=20, b=40, l=40, r=20),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)