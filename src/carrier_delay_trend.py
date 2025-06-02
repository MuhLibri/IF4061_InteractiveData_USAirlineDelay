import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.utils import get_airline_year, format_with_dots

def carrier_delay_trend_and_cause(df, selected_years):
    df = df.copy()
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    df = df[df['airline_year'].isin(selected_years)]
    
    # Calculate delay percentage per carrier per year
    carrier_year = df.groupby(['carrier_name', 'airline_year']).agg(
        total_del15=('arr_del15', 'sum'),
        total_flights=('arr_flights', 'sum')
    ).reset_index()
    carrier_year['delay_pct'] = (carrier_year['total_del15'] / carrier_year['total_flights']) * 100

    # Get average delay percentage for each carrier (over selected years)
    avg_delay = carrier_year.groupby('carrier_name')['delay_pct'].mean().sort_values(ascending=False)
    default_carriers = [avg_delay.index[0], avg_delay.index[-1]] if len(avg_delay) > 1 else avg_delay.index.tolist()

    # Carrier selection
    carriers = st.multiselect(
        'Select 2 Carriers to Compare',
        options=avg_delay.index.tolist(),
        default=default_carriers,
        max_selections=2,
        help='Default: carrier with highest and lowest delay percentage.'
    )
    if len(carriers) != 2:
        st.warning('Please select exactly 2 carriers.')
        return

    # Prepare year range string for titles
    if selected_years:
        year_range = f"{min(selected_years)} - {max(selected_years)}" if len(selected_years) > 1 else f"{selected_years[0]}"
    else:
        year_range = ""

    # Title for delay percentage trend
    st.markdown(
        f"<h2 style='font-size: 24px;'>Delay Percentage Trend for {carriers[0]} and {carriers[1]}<br>"
        f"<span style='font-size: 20px;'>({year_range})</span></h2>",
        unsafe_allow_html=True
    )
    # Line chart
    fig = px.line(
        carrier_year[carrier_year['carrier_name'].isin(carriers)],
        x='airline_year',
        y='delay_pct',
        color='carrier_name',
        markers=True,
        labels={'delay_pct': 'Percentage of Flight Delays (%)', 'airline_year': 'Year', 'carrier_name': 'Carrier'},
        height=350
    )
    fig.update_traces(
        mode='lines+markers',
        hovertemplate=(
            'Year: <b>%{x}</b><br>'
            'Delay Percentage: <b>%{y:.2f}%</b><extra></extra>'
        )
    )
    fig.update_layout(margin=dict(t=20, b=40, l=40, r=20))
    st.plotly_chart(fig, use_container_width=True)

    st.write("")

    # Stacked bar for each carrier (1 row, 2 columns)
    colA, colB = st.columns(2)
    for idx, carrier in enumerate(carriers):
        cdf = df[df['carrier_name'] == carrier]
        if cdf.empty:
            (colA if idx == 0 else colB).warning(f'No data for {carrier}')
            continue

        # Title for delay cause breakdown
        (colA if idx == 0 else colB).markdown(
            f"<h2 style='font-size: 24px;'>Delay Cause Breakdown per Year: {carrier}<br>"
            f"<span style='font-size: 20px;'>({year_range})</span></h2>",
            unsafe_allow_html=True
        )

        delay_causes = [
            ("carrier_ct", "Carrier", "#636EFA"),
            ("weather_ct", "Weather", "#EF553B"),
            ("nas_ct", "NAS (National Airspace System)", "#00CC96"),
            ("security_ct", "Security", "#AB63FA"),
            ("late_aircraft_ct", "Late Aircraft", "#FFA15A")
        ]
        yearly = cdf.groupby('airline_year')[[c[0] for c in delay_causes] + ['arr_flights']].sum().reset_index()
        for col, _, _ in delay_causes:
            yearly[col + '_pct'] = (yearly[col] / yearly['arr_flights']) * 100
        fig2 = go.Figure()
        for col, label, color in delay_causes:
            formatted_values = yearly[col].apply(format_with_dots)
            percentages = yearly[col + '_pct']
            customdata = pd.DataFrame({'val': formatted_values, 'pct': percentages.round(2)}).values
            fig2.add_trace(go.Bar(
                x=yearly['airline_year'],
                y=percentages,
                name=label,
                marker_color=color,
                meta=[label] * len(yearly),
                customdata=customdata,
                hovertemplate=(
                    '<b>%{x}</b><br>'
                    '<b>%{meta}</b><br>'
                    'Total Delay: <b>%{customdata[0]}</b><br>'
                    'Percentage (of all flights): <b>%{customdata[1]:.2f}%</b><extra></extra>'
                )
            ))
        fig2.update_layout(
            barmode='stack',
            xaxis=dict(title="Year", tickangle=45),
            yaxis=dict(title="Percentage of Flight Delays (%)"),
            height=400,
            margin=dict(t=60, b=40, l=40, r=40),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.12,
                xanchor="right",
                x=0.58,
                font=dict(size=13)
            )
        )
        fig2.update_annotations(font_size=16)
        (colA if idx == 0 else colB).plotly_chart(fig2, use_container_width=True)
