# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# List of unique sites for dropdown
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Dropdown
    dcc.Dropdown(id='site-dropdown',
                 options=site_options,
                 value='ALL',
                 placeholder="Select a Launch Site",
                 searchable=True
                 ),
    html.Br(),

    # Pie Chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    # Payload slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    marks={int(i): str(int(i)) for i in range(int(min_payload), int(max_payload)+1, 1000)},
                    value=[min_payload, max_payload]
                    ),
    html.Br(),

    # Scatter Chart
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(spacex_df,
                     values='class',
                     names='Launch Site',
                     title='Total Success Launches By Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        success_counts = filtered_df['class'].value_counts().reset_index()
        success_counts.columns = ['class', 'count']
        success_counts['class'] = success_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(success_counts,
                     values='count',
                     names='class',
                     title=f'Success vs Failure Launches for site {entered_site}')
    return fig


# Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_chart(entered_site, payload_range):
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title='Correlation between Payload and Success for ' + ('All Sites' if entered_site == 'ALL' else entered_site))
    return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True)