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
    previous_label_year = previous_year['airline_year'].split('/')[-1]
    
    # Calculate delta (gain/loss) from previous year
    previous_year = merged_df.iloc[-2]
    delta_percentage = recent_year['percentage'] - previous_year['percentage']
    delta_delay = recent_year['total_delay'] - previous_year['total_delay']
    delta_flights = recent_year['total_flights'] - previous_year['total_flights']

    st.markdown(
        f"""
        <div style='
        '>
            <h2 style='font-size: 12px; font-weight: bold;'>
                Delay Overview for Latest Year ({previous_label_year}/{recent_label_year})
            </h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # === Top Metrics ===
    col1, col2, col3 = st.columns(3)

    # Determine arrow and color for percentage delta
    if delta_percentage > 0:
        arrow = "▲"
        delta_color = "#d62728"  # red
    else:
        arrow = "▼"
        delta_color = "#2ca02c"  # green

    with col1:
        st.markdown(
            f"""
            <div style='padding: 0px 12px 0px 0px; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:4px;'>Percentage of Flight Delays ({recent_label_year})</div>
                <div style='font-size:2.2em; font-weight:bold; color:#fff;'>{recent_year['percentage']:.2f}%</div>
                <div style='font-size:1em; color:{delta_color}; font-weight:600;'>{arrow} {abs(delta_percentage):.2f}% from previous year</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div style='padding: 0px 12px 0px 8px; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:4px;'>Total Flight Delays ({recent_label_year})</div>
                <div style='font-size:2.2em; font-weight:bold; color:#fff;'>{format_with_dots(recent_year['total_delay'])}</div>
                <div style='font-size:1em; color:#aaa;'>+{format_with_dots(delta_delay)} from previous year</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div style='padding: 0px 0px 0px 8px; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:4px;'>Total Overall Flights ({recent_label_year})</div>
                <div style='font-size:2.2em; font-weight:bold; color:#fff;'>{format_with_dots(recent_year['total_flights'])}</div>
                <div style='font-size:1em; color:#aaa;'>+{format_with_dots(delta_flights)} from previous year</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.write("")
    
    year_range = f"{selected_years[0]}" if selected_years[0] == selected_years[-1] else f"{selected_years[0]} - {selected_years[-1]}"
    st.markdown(f"<h2 style='font-size: 24px;'>Flight Delays Trend Across Years<br><span style='font-size: 20px;'>({year_range})</span></h2>", unsafe_allow_html=True)    

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
        yaxis_title="Percentage of Flight Delays (%)",
        margin=dict(t=20, b=40, l=40, r=20),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True)