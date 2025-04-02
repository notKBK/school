import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import os

# Step 1
url = "https://en.wikipedia.org/wiki/List_of_FIFA_World_Cup_finals"
tables = pd.read_html(url)
world_cup_data = tables[3]

country_win_counts = world_cup_data['Winners'].replace('West Germany', 'Germany').value_counts().reset_index()
country_win_counts.columns = ['Country', 'Wins']

# Step 2
app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("FIFA World Cup", style={'textAlign': 'center'}),

    dcc.Graph(id='choropleth-map'),

    html.Label("Select a Country:"),
    dcc.Dropdown(
        id='country-selector',
        options=[{'label': country, 'value': country} for country in sorted(country_win_counts['Country'].unique())],
        value='Brazil'
    ),
    html.Div(id='country-result', style={'marginTop': 10}),

    html.Label("Select A Year:"),
    dcc.Dropdown(
        id='year-selector',
        options=[{'label': year, 'value': year} for year in sorted(world_cup_data['Year'].unique())],
        value=2018
    ),
    html.Div(id='year-result', style={'marginTop': 10})
])

# Step 2
@app.callback(
    Output('choropleth-map', 'figure'),
    Input('country-selector', 'value')
)
def update_map(selected_country):
    figure = px.choropleth(
        country_win_counts,
        locations='Country',
        locationmode='country names',
        color='Wins',
        hover_name='Country',
        color_continuous_scale='Greens',
        title='World Cup Wins by Country (choropleth-map)'
    )
    figure.update_layout(margin={"r": 0, "t": 50, "l": 0, "b": 0})
    return figure

# Step 2
@app.callback(
    Output('country-result', 'children'),
    Input('country-selector', 'value')
)
def show_country_wins(selected_country):
    win_series = world_cup_data['Winners'].replace('West Germany', 'Germany').value_counts()
    total_wins = win_series.get(selected_country, 0)
    if total_wins > 0:
        return f"{selected_country} has {total_wins} wins."
    else:
        return f"{selected_country} has no wins."

# Step 2
@app.callback(
    Output('year-result', 'children'),
    Input('year-selector', 'value')
)
def show_year_details(selected_year):
    match = world_cup_data[world_cup_data['Year'] == selected_year]
    if not match.empty:
        winning_team = match['Winners'].values[0]
        runner_up_team = match['Runners-up'].values[0]
        return f"In {selected_year}, {winning_team} won, and the runner-up was {runner_up_team}."
    return "Year not found."

# Step 3
if __name__ == '__main__':
    port_number = int(os.environ.get("PORT", 8050))
    app.run(host="0.0.0.0", port=port_number, debug=True)
