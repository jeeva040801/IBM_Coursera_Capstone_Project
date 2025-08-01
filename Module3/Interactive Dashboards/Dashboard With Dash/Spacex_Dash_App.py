# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read SpaceX launch data into pandas DataFrame
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Generate dropdown options (ALL + individual launch sites)
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in sorted(spacex_df['Launch Site'].unique())
]

# Build the layout
app.layout = html.Div([
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Launch-site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',                       # default selection
        placeholder='Select a Launch Site',
        searchable=True,
        style={'width': '80%', 'padding': '3px', 'font-size': '15px'}
    ),
    html.Br(),

    # TASK 2: Pie chart for successful launches
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload slider label
    html.P("Payload range (Kg):"),

    # TASK 3: Range slider for payload
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload, max=max_payload, step=1000,
        marks={int(x): f'{int(x)}' for x in
               [min_payload, 2500, 5000, 7500, max_payload]},
        value=[min_payload, max_payload]   # default slider range
    ),
    html.Br(),

    # TASK 4: Scatter plot for payload vs. success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# ----------------------- CALLBACKS -----------------------

# TASK 2 callback: update pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Success counts for each site
        df = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(
            df,
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Success vs. failure counts for the selected site
        df = spacex_df[spacex_df['Launch Site'] == selected_site] \
            .groupby('class') \
            .size() \
            .reset_index(name='count')
        df['Outcome'] = df['class'].replace({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            df,
            names='Outcome',
            values='count',
            title=f'Success vs. Failure for site {selected_site}'
        )
    return fig

# TASK 4 callback: update scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # Filter by launch site if not ALL
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title='Payload vs. Outcome for {}'.format(
            'All Sites' if selected_site == 'ALL' else selected_site
        ),
        labels={'class': 'Launch Outcome'}
    )
    return fig

# ---------------------------------------------------------

# Run the Dash app
if __name__ == '__main__':
    app.run(debug=True)

