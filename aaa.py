import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Step 1: Load correct table
url = "https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals"
tables = pd.read_html(url)
df = tables[3]  # Confirmed from your output!

# Step 2: Clean and prepare
df['Winners'] = df['Winners'].replace('West Germany', 'Germany')
df['Runners-up'] = df['Runners-up'].replace('West Germany', 'Germany')

# Rename for consistency
df = df.rename(columns={'Winners': 'Winner', 'Runners-up': 'RunnerUp'})

# Subset relevant columns
finals_df = df[['Year', 'Winner', 'RunnerUp']]

# Count wins
win_counts = finals_df['Winner'].value_counts().reset_index()
win_counts.columns = ['Country', 'Wins']

# Step 3: Dash App
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("FIFA World Cup Dashboard", style={'textAlign': 'center'}),

    dcc.Graph(id='choropleth'),

    html.Label("Select a Country:"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': c, 'value': c} for c in sorted(win_counts['Country'].unique())],
        value='Brazil'
    ),
    html.Div(id='country-output', style={'marginTop': 10}),

    html.Label("Select a Year:"),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': y, 'value': y} for y in sorted(finals_df['Year'].unique())],
        value=2018
    ),
    html.Div(id='year-output', style={'marginTop': 10})
])

@app.callback(
    Output('choropleth', 'figure'),
    Input('country-dropdown', 'value')
)
def update_map(_):
    fig = px.choropleth(win_counts,
                        locations='Country',
                        locationmode='country names',
                        color='Wins',
                        hover_name='Country',
                        color_continuous_scale='Viridis',
                        title='World Cup Wins by Country')
    fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
    return fig

@app.callback(
    Output('country-output', 'children'),
    Input('country-dropdown', 'value')
)
def update_country_output(country):
    wins = win_counts[win_counts['Country'] == country]['Wins'].values
    return f"{country} has won the World Cup {wins[0]} time(s)." if len(wins) > 0 else f"{country} has never won the World Cup."

@app.callback(
    Output('year-output', 'children'),
    Input('year-dropdown', 'value')
)
def update_year_output(year):
    row = finals_df[finals_df['Year'] == year]
    if not row.empty:
        winner = row['Winner'].values[0]
        runner = row['RunnerUp'].values[0]
        return f"In {year}, the Winner was {winner} and the Runner-up was {runner}."
    return "Year not found."

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port, debug=True)


