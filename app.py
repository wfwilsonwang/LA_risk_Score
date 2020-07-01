import dash
import dash_core_components as dcc
import dash_html_components as html 
from dash.dependencies import Input, Output
import numpy as np
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
import os

risk_score = pd.read_csv('risk_score.csv')
POI_comm_rates = pd.read_csv('POI_comm_rates.csv')

def find_risk_day(weekday):
    risk_day = risk_score[risk_score['weekday'].str.match(weekday)]
    risk_day = risk_day.reset_index(drop = True)
    
    risk_day.insert(1, 'lat', POI_comm_rates['latitude'].astype(float))
    risk_day.insert(2, 'long', POI_comm_rates['longitude'].astype(float))
    
    risk_day.insert(0, 'name', POI_comm_rates['location_name'])
    risk_day.insert(1, 'address', POI_comm_rates['street_address'])
    risk_day.insert(2, 'category', POI_comm_rates['top_category'])
    risk_day = risk_day.dropna()
    return risk_day


risk_Mon = find_risk_day('Mon')
risk_Tue = find_risk_day('Tue')
risk_Wed = find_risk_day('Wed')
risk_Thu = find_risk_day('Thur')
risk_Fri = find_risk_day('Fri')
risk_Sat = find_risk_day('Sat')
risk_Sun = find_risk_day('Sun')


risk_all = {'Mon': risk_Mon,
            'Tue': risk_Tue,
            'Wed': risk_Wed,
            'Thur': risk_Thu,
            'Fri': risk_Fri,
            'Sat': risk_Sat,
            'Sun': risk_Sun
           }

category = list(risk_Mon.groupby('category').count().index)



rblue = '#4169e1'
mapbox_access_token = 'pk.eyJ1Ijoid2Z3aWxzb253YW5nIiwiYSI6ImNrYjQwcXJzeDBxNnUyeWxtZnlkaDF1OHoifQ.I6_PcA8uuq7kMuDh57hYJg'


app = dash.Dash()
server = app.server

app.layout = html.Div([
    
    # Title 
    html.H1(children = 'Risk Scores of POIs in Los Angeles',
                style = {
                    'textAlign': 'center',
                    'color': rblue,
                    'fontsize': 20,
                    'font-family' : 'verdana'
                }
               ),
    
    # Left column
    html.Div([
        dcc.Dropdown(
            id = 'Weekday-dropdown',
            options = [
                {'label': 'Monday', 'value': 'Mon'},
                {'label': 'Tuesday', 'value': 'Tue'},
                {'label': 'Wednesday', 'value': 'Wed'},
                {'label': 'Thursday', 'value': 'Thur'},
                {'label': 'Friday', 'value': 'Fri'},
                {'label': 'Saturday', 'value': 'Sat'},
                {'label': 'Sunday', 'value': 'Sun'},
            ],
            value = 'Mon',
#             style = {'width': '50%',
#                      'align-Items': 'center',
#                      # 'display': 'flex',
#                      'justify-content': 'center'
#                     }
        ),
        dcc.Dropdown(
            id = 'Category-dropdown',
            options = [
                {'label': i, 'value': i} for i in category
            ],
            value = 'Grocery Stores',
#             style = {'width': '50%',
#                     }
        ),

        dcc.Graph(id = 'Weekday-graph', style = {'height': '80%'}),
    
    # html.Div(id = 'Test')
       
],
      style = {'display': 'inline-block', 'width': '30%', 'height': 768}
),
    
    # Right column
    html.Div([
        dcc.Dropdown(
            id = 'Weekday-dropdown-map',
            options = [
                {'label': 'Monday', 'value': 'Mon'},
                {'label': 'Tuesday', 'value': 'Tue'},
                {'label': 'Wednesday', 'value': 'Wed'},
                {'label': 'Thursday', 'value': 'Thur'},
                {'label': 'Friday', 'value': 'Fri'},
                {'label': 'Saturday', 'value': 'Sat'},
                {'label': 'Sunday', 'value': 'Sun'},
            ],
            value = 'Mon',
#             style = {'width': '50%',
#                     }
        ),
        dcc.Dropdown(
            id = 'Category-dropdown-map',
            options = [
                {'label': i, 'value': i} for i in category
            ],
            value = 'Grocery Stores',
#             style = {'width': '50%',
#                     }
        ),
        

        dcc.Graph(id = 'Weekday-graph-map', style = {'height': '80%'})
       
],
      style = {'display': 'inline-block', 'width': '70%', 'height': 768}
)
])


@app.callback(Output('Weekday-graph', 'figure'),
              # Output('Test', 'children'),
              [Input('Weekday-dropdown', 'value'),
               Input('Category-dropdown', 'value')])
def update_graph(weekday_choice1, category_choice1):
    # selected = dropdown_properties['value']
    
    df = risk_all[weekday_choice1]
    df = df[df['category'].str.contains(category_choice1)]
    
    data = go.Histogram(
                     x = df.risk_score, 
                     # cumulative_enabled=True
                     marker_color = rblue,
                     opacity = 0.75
                 )
    layout = go.Layout(
                 title = 'Histogram of risk scores on ' + weekday_choice1,
                 hovermode = 'closest'
    )

    return {'data': [data], 'layout': layout}


@app.callback(Output('Weekday-graph-map', 'figure'),
              [Input('Weekday-dropdown-map', 'value'),
               Input('Category-dropdown-map', 'value')])
def update_graph_map(weekday_choice, category_choice):
    
    df = risk_all[weekday_choice]
    df = df[df['category'].str.contains(category_choice)]
    df['sizes'] = np.ones([len(df), 1]) * 6

     
    fig =  px.scatter_mapbox(df,
                             lat = 'lat',
                             lon = 'long',
                             color = 'risk_score',
                             hover_name = 'name',
                             text = 'address',
                             title = 'Risk scores of ' + category_choice + ' on ' + weekday_choice,
                              # center = dict(lat = 34, long = -118)
            )
    
    fig.update_layout(
                hovermode='closest',
                mapbox = dict(
                    accesstoken = mapbox_access_token,
                    bearing = 0,
                    center = go.layout.mapbox.Center(
                        lat = 34,
                        lon = -118
                    ),
                    pitch = 0,
                    zoom = 8,
                )
            )
    return fig

if __name__ == '__main__':
    app.run_server()