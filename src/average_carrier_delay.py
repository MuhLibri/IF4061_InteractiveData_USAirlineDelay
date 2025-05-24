import streamlit as st
import plotly.express as px
import time

def average_carrier_delay(df):
    ## Graph 4: Daftar rata-rata keterlambatan penerbangan per maskapai
    # Compute average delay by carrier
    carrier_avg_delay = df.groupby('carrier_name')['arr_del15_percentage'].mean().sort_values()

    # Radiobutton options
    st.markdown("<h2 style='font-size: 24px;'>List of Average Flight Delays by Airline</h2>", unsafe_allow_html=True)    
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
        hovertemplate='<b>%{x}</b><br>Delay Percentage: %{y:.2f}%<extra></extra>'
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