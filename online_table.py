import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from datetime import datetime
import dash_table
import pandas as pd
import sqlite3
import dash



colors = {
    'background': '#e0ddff',
    'background2': 'gray',
    'text': '#506784'
    }

app = dash.Dash(__name__)
server = app.server
conn = sqlite3.connect('postmon.sqlite', check_same_thread=False)
cursor = conn.cursor()

df = pd.read_sql("SELECT id, operation_time, code, category, timeout, status FROM res_h", conn)
df.index = df['id']
df_global = pd.read_sql("SELECT code FROM res_h", conn)
code_list = df_global['code']


app.layout = html.Div([html.H1('Crypto Price Graph',
                               style={
                                      'textAlign': 'center',
                                      "background": "gray"}),
               html.Div(['Выбери временной диапазон',
               dcc.DatePickerRange(
                   id='date-input',
                   stay_open_on_select=False,
                   min_date_allowed=datetime(2020, 1, 1),
                   max_date_allowed=datetime.now(),
                   initial_visible_month=datetime.now(),
                   start_date=datetime.now(),
                   end_date=datetime.now(),
                   number_of_months_shown=2,
                   month_format='MMMM,YYYY',
                   display_format='YYYY-MM-DD',
                   style={
                          'color': 'black',
                          'font-size': '8px',
                          'margin': 10,
                          'padding': '8px',
                          'background': 'black',
                   }
               ),
               'Выбери код услуги',
               dcc.Dropdown(id='dropdown',
                            options=[{'label': i, 'value': i} for i in code_list],
                            value='code',
                            optionHeight=10,
                            style={
                                'height': '40px',
                                'font-weight': 100,
                                'font-size': '8px',
                                'line-height': '10px',
                                'color': 'black',
                                'margin': 0,
                                'padding': '8px',
                                'background': 'black',
                                'position': 'middle',
                                'display': 'inline-block',
                                'width': '150px',
                                'vertical-align': 'middle',
                                }
                            ),
                html.Div(id='date-output'),
                html.Div(id='intermediate-value', style={'display': 'none'}),
                               ], className="row ",
                    style={'marginTop': 0, 'marginBottom': 0, 'font-size': 30, 'color': 'white',
                           'display': 'inline-block'}),
               html.Div(id='graph-output'),
               html.Div(children=[html.H1(children="Data Table",
                                          style={
                                              'textAlign': 'center',
                                              "background": "gray"})
                                  ]
                        ),
               html.Div(children=[html.Table(id='table'), html.Div(id='table-output')]),
               html.Div(children=[dcc.Markdown(
                   " © 2019 [DCAICHARA](https://github.com/dc-aichara)  All Rights Reserved.")], style={
                                'textAlign': 'center',
                                "background": "yellow"}),
                              ],
              style={"background": "#000080"}
                            )


@app.callback(Output('table-output', 'children'),
              [Input('dropdown', 'value')])
def get_data_table(option):
    df['operation_time'] = pd.to_datetime(df['operation_time'])
    data_table = dash_table.DataTable(
        id='datatable-data',
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        page_size=50,
        page_action='native',
        filter_action='native',
        sort_mode="multi",
        sort_action="native",
        style_cell={'width': '100px'},
        style_header={'backgroundColor': 'rgb(230, 230, 230)',
                      'fontWeight': 'bold',
                      'textAlign': 'left',
                      'border': '1px solid gray'},
        style_data_conditional=[
            {'textAlign': 'left',
             'border': '1px solid gray',
             'color': '#506784'},
            {'if': {
                'column_id': 'category',
                'filter_query': '{category} eq "A"', },
                "fontWeight": "bold"},
            {'if': {'column_id': 'status',
                    'filter_query': '{status} eq "Error"'},
             'backgroundColor': "#ff6b80"}
        ]
    )
    conn.commit()
    return data_table


@app.callback(Output('graph-output', 'children'),
              [Input('date-input', 'start_date'),
               Input('date-input', 'end_date'),
               Input('dropdown', 'value')])
def render_graph(start_date, end_date, option):
    df = pd.read_sql("SELECT id, operation_time, code, status from global_answers_data", conn)
    df['operation_time'] = pd.to_datetime(df['operation_time'])
    data = df[(df.operation_time >= start_date) & (df.operation_time <= end_date)]
    conn.commit()
    return dcc.Graph(
        id='graph-1',
        figure={
            'data': [
                {'x': data['operation_time'],
                 'y': data['status'],
                 'type': 'bar_chart',
                 'name': 'value1'},
            ],
            'layout': {
                'title': f'{option.capitalize()} История',
                'plot_bgcolor': '#cdcdcd',
                'paper_bgcolor': '#9a9a9a',
                'font': {
                    'color': colors['text'],
                    'size': 18
                },
                'xaxis': {
                        'title': 'Дата/Время',
                        'showspikes': True,
                        'spikedash': 'dot',
                        'spikemode': 'across',
                        'spikesnap': 'cursor',
                        },
                'yaxis': {
                        'title': '',
                        'showspikes': True,
                        'spikedash': 'dot',
                        'spikemode': 'across',
                        'spikesnap': 'cursor'
                        },

            }
        }
    )


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')