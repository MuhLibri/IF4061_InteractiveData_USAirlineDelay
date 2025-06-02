import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from src.utils import format_with_dots, get_airline_year, normalize_airline_year
from src.state_utils import state_abbrev_to_name

def state_delay_trend_and_cause(df, selected_years):
    df = df.copy()
    df['airline_year'] = df.apply(get_airline_year, axis=1)
    df = df[df['airline_year'].isin(selected_years)]

    # Map full state name
    df['state_full'] = df['airport_state'].map(state_abbrev_to_name)
    df = df[df['state_full'].notnull()]

    # Compute average delay per state
    state_avg_delay = df.groupby('state_full')['arr_del15_percentage'].mean().reset_index()

    # Identify states with highest and lowest delay
    highest_state = state_avg_delay.loc[state_avg_delay['arr_del15_percentage'].idxmax(), 'state_full']
    lowest_state = state_avg_delay.loc[state_avg_delay['arr_del15_percentage'].idxmin(), 'state_full']
    default_states = [highest_state, lowest_state]

    # State selection
    states = st.multiselect(
        'Select 2 States to Compare',
        options=state_avg_delay['state_full'].tolist(),
        default=default_states,
        max_selections=2,
        help='Default: state with highest and lowest delay percentage.'
    )

    if len(states) != 2:
        st.warning('Please select exactly 2 states.')
        return

    # Title
    year_range = f"{min(selected_years)} - {max(selected_years)}" if len(selected_years) > 1 else f"{selected_years[0]}"
    st.markdown(
        f"<h2 style='font-size: 24px;'>Delay Percentage Trend for {states[0]} and {states[1]}<br>"
        f"<span style='font-size: 20px;'>({year_range})</span></h2>",
        unsafe_allow_html=True
    )

    # Aggregate delay percentage per state per year
    state_year = (
        df[df['state_full'].isin(states)]
        .groupby(['state_full', 'airline_year'])['arr_del15_percentage']
        .mean()
        .reset_index()
        .rename(columns={'arr_del15_percentage': 'delay_pct'})
    )

    # Normalize airline_year for consistent labeling (e.g., '2013/2014')
    state_year['airline_year'] = state_year['airline_year'].apply(normalize_airline_year)

    # Set a consistent order for categorical x-axis
    year_order = sorted(state_year['airline_year'].unique(), key=lambda x: int(x.split('/')[0]))
    state_year['airline_year'] = pd.Categorical(state_year['airline_year'], categories=year_order, ordered=True)

    # Sort the data for clean plotting
    state_year = state_year.sort_values(['state_full', 'airline_year'])
    print(state_year)

    # Line chart
    line_colors = ["#2A78C3", "#F5F9FF"]
    fig = px.line(
        state_year,
        x='airline_year',
        y='delay_pct',
        color='state_full',
        color_discrete_sequence=line_colors,
        markers=True,
        labels={'delay_pct': 'Percentage of Flight Delays (%)', 'airline_year': 'Year', 'state_full': 'State'},
        height=350,
        category_orders={'airline_year': year_order}
    )
    fig.update_traces(
        mode='lines+markers',
        hovertemplate='Year: <b>%{x}</b><br>Delay Percentage: <b>%{y:.2f}%</b><extra></extra>'
    )
    fig.update_layout(margin=dict(t=20, b=40, l=40, r=20))
    st.plotly_chart(fig, use_container_width=True)

    st.write("")

    # Stacked bar chart for each selected state
    colA, colB = st.columns(2)
    for idx, state in enumerate(states):
        sdf = df[df['state_full'] == state]
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

        yearly = sdf.groupby('airline_year')[[col[0] for col in delay_causes] + ['arr_flights']].sum().reset_index()
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