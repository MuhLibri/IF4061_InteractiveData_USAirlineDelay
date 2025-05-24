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
    delay_grouped_cause = df.groupby('airline_year')[
        ['carrier_ct', 'weather_ct', 'nas_ct', 'security_ct', 'late_aircraft_ct']
    ].sum().reset_index()

    # Remove incomplete final year if applicable
    if total_delay['airline_year'].iloc[-1] == '2023/2024':
        total_delay = total_delay[:-1]
        delay_grouped_cause = delay_grouped_cause[:-1]

    return total_delay, delay_grouped_cause


def trend_flight_year(df):
    st.markdown("<h2 style='font-size: 24px;'>Trend of Flight Delay Causes by Year</h2>", unsafe_allow_html=True)

    # === Cached Preprocessing ===
    total_delay, delay_grouped_cause = preprocess_delay_data(df)

    # === User Selection ===
    plot_type = st.radio(
        "Choose Visualization Type:",
        ["Total Delay", "Total Delay by Cause"],
        horizontal=True,
        key="plot_type_radio_year"
    )

    # === Total Delay Plot ===
    if plot_type == "Total Delay":
        total_delay['hover_delay'] = total_delay['total_delay'].apply(format_with_dots)
        total_delay['Type'] = 'Total Delay'
        total_delay['pct_change'] = total_delay['total_delay'].pct_change() * 100

        max_row = total_delay.loc[total_delay['total_delay'].idxmax()]
        gain_row = total_delay.loc[total_delay['pct_change'].idxmax()]
        drop_row = total_delay.loc[total_delay['pct_change'].idxmin()]

        col1, col2, col3 = st.columns(3)
        col1.metric("Year with Highest Flights Delay", f"{max_row['airline_year']}", f"{max_row['total_delay']:,.0f} total flights delay")
        col2.metric("Biggest Increase", f"{gain_row['airline_year']}", f"{gain_row['pct_change']:.2f}%")
        col3.metric("Biggest Decrease", f"{drop_row['airline_year']}", f"{drop_row['pct_change']:.2f}%")

        fig = px.line(
            total_delay,
            x='airline_year',
            y='total_delay',
            color='Type',
            markers=True,
            hover_data={'hover_delay': True, 'total_delay': False, 'Type': False},
            height=350
        )
        fig.update_traces(
            hovertemplate=
                'Year: <b>%{x}</b><br>'
                'Total Delay: <b>%{customdata[0]} flights<extra></extra></b>'
        )
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Total Flights Delay",
            margin=dict(t=20, b=40, l=40, r=20),
            showlegend=True,
        )

        st.plotly_chart(fig, use_container_width=True)

    # === Delay by Cause Plot ===
    else:
        label_map = {
            "carrier_ct": "Carrier",
            "weather_ct": "Weather",
            "nas_ct": "NAS (National Airspace System)",
            "security_ct": "Security",
            "late_aircraft_ct": "Late Aircraft"
        }
        reverse_label_map = {v: k for k, v in label_map.items()}
        color_map = {
            'Carrier': '#1f77b4',
            'Weather': '#ff7f0e',
            'NAS (National Airspace System)': '#2ca02c',
            'Security': '#d62728',
            'Late Aircraft': '#9467bd'
        }

        readable_delay_types = list(label_map.values())
        options_dropdown = ['Show All'] + readable_delay_types
        selected_option = st.selectbox("Choose Delay Cause:", options_dropdown, index=0)

        if selected_option == 'Show All':
            selected_causes = list(label_map.keys())
        else:
            selected_causes = [reverse_label_map[selected_option]]

        df_melt = delay_grouped_cause.melt(
            id_vars='airline_year',
            value_vars=selected_causes,
            var_name='Cause',
            value_name='Total_Delay'
        )
        df_melt['Cause'] = df_melt['Cause'].map(label_map)
        df_melt['Total_Delay_Formatted'] = df_melt['Total_Delay'].apply(format_with_dots)

        fig = px.line(
            df_melt,
            x='airline_year',
            y='Total_Delay',
            color='Cause',
            markers=True,
            color_discrete_map=color_map,
            custom_data=['Cause', 'Total_Delay_Formatted'],
            height=350
        )
        
        fig.update_traces(
            hovertemplate=(
                'Cause: <b>%{customdata[0]}</b><br>'
                'Year: <b>%{x}</b><br>'
                'Total Delay: <b>%{customdata[1]} flights</b><extra></extra>'
            )
        )
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Total Flights Delay",
            margin=dict(t=0, b=40, l=40, r=20)
        )

        st.plotly_chart(fig, use_container_width=True)