import streamlit as st
import plotly.express as px
import pandas as pd
from src.utils import get_airline_year, format_with_dots

@st.cache_data(show_spinner=False)
def compute_carrier_avg_delay(df):
    carrier_group = df.groupby('carrier_name').agg(
        total_del15=('arr_del15', 'sum'),
        total_flights=('arr_flights', 'sum')
    )
    avg_delay_percent = (carrier_group['total_del15'] / carrier_group['total_flights']) * 100
    return avg_delay_percent.sort_values()

@st.cache_data(show_spinner=False)
def filter_data_by_year(df, selected_years):
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    return df[df['airline_year'].isin(selected_years)]

@st.cache_data(show_spinner=False)
def load_and_prepare_data(path):
    df = pd.read_csv(path)
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    return df

def average_carrier_delay(df, selected_years):
    df = filter_data_by_year(df, selected_years)
    year_range = f"{selected_years[0]}" if selected_years[0] == selected_years[-1] else f"{selected_years[0]} - {selected_years[-1]}"
    
    # Check if data is available for the selected years
    carrier_avg = compute_carrier_avg_delay(filter_data_by_year(df, selected_years))

    # Get highest and lowest
    highest_carrier = carrier_avg.idxmax()
    highest_value = carrier_avg.max()
    lowest_carrier = carrier_avg.idxmin()
    lowest_value = carrier_avg.min()

    st.write("")

    # Compute and cache average delay per carrier
    carrier_avg_delay = compute_carrier_avg_delay(df)

    selected_data = carrier_avg_delay.sort_values(ascending=False)

    # Compute overall average
    overall_avg = carrier_avg_delay.mean()

    # Display metrics: no colored border, improved spacing and alignment
    col1, col2, col3 = st.columns([1, 1, 1], gap="large")

    with col1:
        st.markdown(
            f"""
            <div style='padding: 0 24px 8px 0; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:2px;'>Average Carrier Delay</div>
                <div style='font-size:2.2em; font-weight:bold; color:#fff;'>{overall_avg:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div style='padding: 0 24px 8px 0; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:2px;'>Carrier with the Highest Delay</div>
                <div style='font-size:1.5em; font-weight:bold; color:#d62728;'>{highest_carrier}</div>
                <div style='font-size:1.2em; color:#d62728;'>{highest_value:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div style='padding: 0 24px 8px 0; margin-bottom:8px; display:flex; flex-direction:column; justify-content:center; align-items:flex-start;'>
                <div style='font-size:15px; color:#fff; margin-bottom:2px;'>Carrier with the Lowest Delay</div>
                <div style='font-size:1.5em; font-weight:bold; color:#2ca02c;'>{lowest_carrier}</div>
                <div style='font-size:1.2em; color:#2ca02c;'>{lowest_value:.2f}%</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    df_plot = selected_data.reset_index()
    df_plot.columns = ['Carrier', 'AvgDelayPercent']
    
    # Calculate total delay and total flight for each carrier
    carrier_stats = df.groupby('carrier_name').agg(
        total_delay=('arr_del15', 'sum'),
        total_flight=('arr_flights', 'sum')
    )
    carrier_stats = carrier_stats.loc[selected_data.index]
    # Format total_delay and total_flight with dots
    df_plot['TotalDelay'] = carrier_stats['total_delay'].apply(format_with_dots).values
    df_plot['TotalFlight'] = carrier_stats['total_flight'].apply(format_with_dots).values

    st.markdown(f"<h2 style='font-size: 24px;'>Flight Delays Percentage of All Carriers<br><span style='font-size: 20px;'>({year_range})</span></h2>", unsafe_allow_html=True)

    # Plot
    fig = px.bar(
        df_plot,
        x='Carrier',
        y='AvgDelayPercent',
        labels={'AvgDelayPercent': 'Percentage of Flight Delays (%)'},
        color='AvgDelayPercent',
        color_continuous_scale='Blues',
        template='plotly_white',
        height=450
    )

    fig.update_traces(
        marker_line_color='darkgray',
        marker_line_width=1.5,
        hovertemplate='<b>%{x}</b><br>Delay Percentage: <b>%{y:.2f}%</b><br>Total Delays: <b>%{customdata[0]}</b><br>Total Flights: <b>%{customdata[1]}</b><extra></extra>',
        customdata=df_plot[['TotalDelay', 'TotalFlight']].values
    )

    fig.update_layout(
        yaxis_range=[0, df_plot['AvgDelayPercent'].max() * 1.2],
        font=dict(family="Segoe UI", size=14),
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=0, b=40, l=40, r=20),
        coloraxis_showscale=False  # Hide the color bar
    )

    st.plotly_chart(fig, use_container_width=True)