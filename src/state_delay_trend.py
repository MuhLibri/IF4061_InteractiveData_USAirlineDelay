import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.utils import format_with_dots, get_airline_year

def state_delay_trend_and_cause(df, selected_years):
    # Siapkan data
    df = df.copy()
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    df = df[df['airline_year'].isin(selected_years)]
    
    # Hitung persentase delay per state per tahun
    state_year = df.groupby(['airport_state', 'airline_year']).agg(
        total_del15=('arr_del15', 'sum'),
        total_flights=('arr_flights', 'sum')
    ).reset_index()
    state_year['delay_pct'] = (state_year['total_del15'] / state_year['total_flights']) * 100

    # Ambil rata-rata delay untuk default selection
    avg_delay = state_year.groupby('airport_state')['delay_pct'].mean().sort_values(ascending=False)
    default_states = [avg_delay.index[0], avg_delay.index[-1]] if len(avg_delay) > 1 else avg_delay.index.tolist()

    # Pilihan state
    states = st.multiselect(
        'Select 2 States to Compare',
        options=avg_delay.index.tolist(),
        default=default_states,
        max_selections=2,
        help='Default: state with highest and lowest delay percentage.'
    )
    if len(states) != 2:
        st.warning('Please select exactly 2 states.')
        return

    # Judul
    year_range = f"{min(selected_years)} - {max(selected_years)}" if len(selected_years) > 1 else f"{selected_years[0]}"
    st.markdown(
        f"<h2 style='font-size: 24px;'>Delay Percentage Trend for {states[0]} and {states[1]}<br>"
        f"<span style='font-size: 20px;'>({year_range})</span></h2>",
        unsafe_allow_html=True
    )

    # Normalisasi tahun jadi 4 digit di awal jika perlu
    def normalize_airline_year(year_str):
        parts = year_str.split('/')
        first = parts[0]
        if len(first) == 2:
            first = '20' + first  # misalnya '22' jadi '2022'
        return f"{first}/{parts[1]}"

    state_year['airline_year'] = state_year['airline_year'].apply(normalize_airline_year)

    # Urutkan tahun
    year_order = sorted(state_year['airline_year'].unique(), key=lambda x: int(x.split('/')[0]))
    state_year['airline_year'] = pd.Categorical(
        state_year['airline_year'],
        categories=year_order,
        ordered=True
    )
    state_year = state_year.sort_values('airline_year')

    # Subset dan pastikan airline_year tetap kategori terurut
    filtered_state_year = state_year[state_year['airport_state'].isin(states)].copy()
    filtered_state_year['airline_year'] = pd.Categorical(
        filtered_state_year['airline_year'],
        categories=year_order,
        ordered=True
    )


    # Line chart
    line_colors = ["#2A78C3", "#F5F9FF"]
    fig = px.line(
        filtered_state_year,
        x='airline_year',
        y='delay_pct',
        color='airport_state',
        color_discrete_sequence=line_colors,
        markers=True,
        labels={
            'delay_pct': 'Percentage of Flight Delays (%)',
            'airline_year': 'Year',
            'airport_state': 'State'
        },
        height=350,
        category_orders={'airline_year': year_order}
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
    print(filtered_state_year['airline_year'].unique())
    print(filtered_state_year['airline_year'].dtype)

    st.write("")

    # Stacked bar untuk masing-masing state
    colA, colB = st.columns(2)
    for idx, state in enumerate(states):
        sdf = df[df['airport_state'] == state]
        if sdf.empty:
            (colA if idx == 0 else colB).warning(f'No data for {state}')
            continue
        (colA if idx == 0 else colB).markdown(
            f"<h2 style='font-size: 24px;'>Delay Cause Breakdown per Year: {state}<br>"
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
        yearly = sdf.groupby('airline_year')[[c[0] for c in delay_causes] + ['arr_flights']].sum().reset_index()
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
            height=500,
            margin=dict(t=0, b=0, l=0, r=20),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="center",
                x=0.465,
            )
        )
        fig2.update_annotations(font_size=16)
        (colA if idx == 0 else colB).plotly_chart(fig2, use_container_width=True)
