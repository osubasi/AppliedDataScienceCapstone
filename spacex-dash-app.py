# Import required libraries
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

options=[
    {'label': 'All Sites', 'value': 'ALL'},
]
launch_sites = spacex_df["Launch Site"].unique()
for item in launch_sites:
    options.append({'label': item, 'value': item})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36',
            'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(id='site-dropdown',
        options=options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    #
    # TASK 3: Add a slider to select payload range
    #dcc.RangeSlider(id='payload-slider',...)
    
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(id='payload-slider',
            min=0, max=10000, 
            step=1000,
            marks={0: '0',
                    100: '100'},
            value=[min_payload, max_payload]),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    ])

# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df[spacex_df['class']==1].groupby("Launch Site").sum().reset_index()
    if entered_site == 'ALL':
        fig = px.pie(filtered_df, values='class', 
        names='Launch Site', 
        title='Total Success Launches By Site')
        return fig
    else:
        #return the outcomes piechart for a selected site
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]
        filtered_df['ratio'] = filtered_df['class'].sum()/spacex_df.shape[0]
        fig = px.pie(filtered_df, values='ratio', 
        names='class', 
        title='Total Success Launches for Site '+entered_site)
        return fig
       

@app.callback(
Output(component_id='success-payload-scatter-chart', component_property='figure'),
Input(component_id='site-dropdown', component_property='value'), 
Input(component_id="payload-slider", component_property="value"))
def update_scatter_chart(entered_site, slider_range):
    low, high = slider_range
    if entered_site == 'ALL':
        mask = (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)
        fig = px.scatter(
            spacex_df[mask], y="class", x="Payload Mass (kg)",
            color="Booster Version Category",
            symbol="Booster Version Category",
            title='Correlation between Payload and Success for all Sites')
        return fig
    else:
        mask = (spacex_df['Payload Mass (kg)'] > low) & (spacex_df['Payload Mass (kg)'] < high)
        filtered_df = spacex_df[spacex_df['Launch Site']==entered_site]    
        fig = px.scatter(
            filtered_df[mask], y="class", x="Payload Mass (kg)",
            color="Booster Version Category",
            symbol="Booster Version Category",
            hover_data=['Payload Mass (kg)'],
            title='Correlation between Payload and Success for '+entered_site
            )
        return fig


if __name__ == '__main__':
    app.run()