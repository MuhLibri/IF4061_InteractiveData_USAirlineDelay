import streamlit as st
import plotly.express as px

from src.utils import format_with_dots, get_two_month_span

@st.cache_data
def preprocess_delay_by_month(df):
    month_map = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
        5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
        9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
    }
    month_order = list(month_map.values())

    df = df.copy()
    df['month'] = df['month'].map(month_map)
    df['total_delay'] = df[
        ['carrier_ct', 'weather_ct', 'nas_ct', 'security_ct', 'late_aircraft_ct']
    ].sum(axis=1)

    total_delay = df.groupby('month')['total_delay'].sum().reindex(month_order).reset_index()

    delay_by_cause = df.groupby('month')[
        ['carrier_ct', 'weather_ct', 'nas_ct', 'security_ct', 'late_aircraft_ct']
    ].sum().reindex(month_order).reset_index()

    return total_delay, delay_by_cause


def trend_flight_month(df):
    st.markdown("<h2 style='font-size: 24px;'>Trend of Flight Delay Causes by Month</h2>", unsafe_allow_html=True)

    # === Cached Data ===
    total_delay, delay_by_cause = preprocess_delay_by_month(df)

    # === User Input ===
    plot_type = st.radio(
        "Choose Visualization Type:",
        ["Total Delay", "Total Delay by Cause"],
        horizontal=True,
        key="plot_type_radio_month"
    )

    if plot_type == "Total Delay":
        total_delay = total_delay.copy()
        total_delay['Type'] = 'Total Delay'
        total_delay['hover_delay'] = total_delay['total_delay'].apply(format_with_dots)
        total_delay['pct_change'] = total_delay['total_delay'].pct_change() * 100

        # Metrics
        max_row = total_delay.loc[total_delay['total_delay'].idxmax()]
        min_row = total_delay.loc[total_delay['total_delay'].idxmin()]
        gain_idx = total_delay['pct_change'].idxmax()
        loss_idx = total_delay['pct_change'].idxmin()
        gain_month = get_two_month_span(gain_idx, total_delay)
        loss_month = get_two_month_span(loss_idx, total_delay)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Peak Delay Month", max_row['month'], f"{max_row['total_delay']:,.0f} delays")
        col2.metric("Least Delay Month", min_row['month'], f"{min_row['total_delay']:,.0f} delays","inverse")
        col3.metric("Highest Increase", gain_month, f"{total_delay.loc[gain_idx, 'pct_change']:.2f}%")
        col4.metric("Highest Decrease", loss_month, f"{total_delay.loc[loss_idx, 'pct_change']:.2f}%")

        # Plot
        fig = px.line(
            total_delay,
            x='month',
            y='total_delay',
            color='Type',
            markers=True,
            hover_data={'hover_delay': True, 'total_delay': False, 'Type': False},
            height=350
        )
        fig.update_traces(
            hovertemplate=
                'Month: <b>%{x}</b><br>'
                'Total Delay: <b>%{customdata[0]} flights</b><extra></extra>'
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Flights Delay",
            margin=dict(t=20, b=40, l=40, r=20),
            showlegend=True
        )
        st.plotly_chart(fig, use_container_width=True)

    else:
        label_map = {
            "carrier_ct": "Carrier",
            "weather_ct": "Weather",
            "nas_ct": "NAS (National Airspace System)",
            "security_ct": "Security",
            "late_aircraft_ct": "Late Aircraft"
        }
        reverse_map = {v: k for k, v in label_map.items()}
        color_map = {
            'Carrier': '#1f77b4',
            'Weather': '#ff7f0e',
            'NAS (National Airspace System)': '#2ca02c',
            'Security': '#d62728',
            'Late Aircraft': '#9467bd'
        }

        readable_types = list(label_map.values())
        selected = st.selectbox("Choose Delay Cause:", ['Show All'] + readable_types, index=0, key="delay_cause_selectbox")

        selected_cols = list(label_map.keys()) if selected == 'Show All' else [reverse_map[selected]]

        df_melt = delay_by_cause.melt(
            id_vars='month',
            value_vars=selected_cols,
            var_name='Cause',
            value_name='Total_Delay'
        )
        df_melt['Cause'] = df_melt['Cause'].map(label_map)
        df_melt['Total_Delay_Formatted'] = df_melt['Total_Delay'].apply(format_with_dots)

        fig = px.line(
            df_melt,
            x='month',
            y='Total_Delay',
            color='Cause',
            markers=True,
            color_discrete_map=color_map,
            custom_data=['Cause', 'Total_Delay_Formatted'],
            height=350
        )
        fig.update_traces(
            hovertemplate=
                'Cause: <b>%{customdata[0]}</b><br>'
                'Month: <b>%{x}</b><br>'
                'Total Delay: <b>%{customdata[1]} flights</b><extra></extra>'
        )
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Total Flights Delay",
            margin=dict(t=0, b=40, l=40, r=20)
        )

        st.plotly_chart(fig, use_container_width=True)