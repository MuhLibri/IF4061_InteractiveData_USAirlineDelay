# Grouped data by period year from August to July
def get_airline_year(row):
    if row['month'] >= 8:
        return f"{row['year']}/{row['year'] + 1}"
    else:
        return f"{row['year'] - 1}/{row['year']}"

# Utility function to format numbers with dots instead of commas
def format_with_dots(val):
    s = f"{val:,.0f}"
    return s

# Function to get the two-month span for metrics display
def get_two_month_span(idx, total_delay):
    if idx > 0:
        return f"{total_delay.loc[idx-1, 'month']}–{total_delay.loc[idx, 'month']}"
    return total_delay.loc[idx, 'month']  # Fallback for the first row

# Normalisasi tahun jadi 4 digit di awal jika perlu
def normalize_airline_year(year_str):
    parts = year_str.split('/')
    first = parts[0]
    if len(first) == 2:
        first = '20' + first  # misalnya '22' jadi '2022'
    return f"{first}/{parts[1]}"