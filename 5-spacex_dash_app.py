# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}
                                        ),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                              options=[{'label': 'All Sites', 'value': 'ALL'}
                                                        ,{'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'}
                                                        ,{'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                                        ,{'label': 'KSC LC-39A', 'value': 'KSC LC-39A'}
                                                        ,{'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}]
                                               ,value='ALL'
                                               ,placeholder = 'Select a Launch Site here'
                                               ,searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider'
                                                ,min=0
                                                ,max=10000
                                                ,step=1000
                                                ,marks={0: '0',
                                                    100: '100'}
                                                ,value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches By Site'
        )
        fig.update_layout(xaxis_type='linear') 
        return fig
    else:
        # Filter the DataFrame for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # Group by class to count successes (1) and failures (0)
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']
        
        # Replace class values with labels for readability (optional)
        counts['class'] = counts['class'].replace({1: 'Success', 0: 'Failure'})

        # Create the pie chart
        fig = px.pie(
            counts,
            values='count',
            names='class',
            title=f'Success vs. Failure Launches for site {entered_site}'
        )
        fig.update_layout(xaxis_type='linear') 
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(entered_site, payload_range):
    # Filter by payload range (both min and max)
    low, high = payload_range
    payload_filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    if entered_site == 'ALL':
        # No additional filtering, use all launch sites
        fig = px.scatter(
            payload_filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation Between Payload and Success for All Sites'
        )
        fig.update_layout(xaxis_type='linear') 
        return fig
    else:
        # Filter by selected launch site
        site_df = payload_filtered_df[payload_filtered_df['Launch Site'] == entered_site]

        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation Between Payload and Success for Site {entered_site}'
        )
        fig.update_layout(xaxis_type='linear') 
        return fig
    

if __name__ == '__main__':
    app.run(debug=True)