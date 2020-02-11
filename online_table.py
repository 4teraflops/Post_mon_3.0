import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from datetime import datetime
import dash_table
import pandas as pd
import sqlite3
import dash
import dash_daq as daq

colors = {
    'background': '#00001a',  # Черный
    'background2': '#000080',  # Синий
    'background3': 'royalblue',  # Светло-синий
    'background_table': 'rgb(230, 230, 230)',
    'background_white': 'white',
    'text': 'black',
    'text1': '#506784'  # цвет из таблицы
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
conn = sqlite3.connect('postmon.sqlite', check_same_thread=False)
cursor = conn.cursor()

df = pd.read_sql("SELECT id, operation_time, code, category, timeout, status FROM res_h", conn)
df.index = df['id']
df_global = pd.read_sql("SELECT code FROM res_h", conn)
code_list = df_global['code']

app.layout = html.Div([html.H1('График истории статусов',
                               style={
                                   'textAlign': 'center',
                                    "fontWeight": "bold",
                                   'background': colors['background_table'],
                                   'font-size': 28,
                               }),
                       html.Div([' Выбери временной диапазон ',
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
                                         'color': colors['text'],
                                         'font-size': '20px',
                                         'background': colors['background3'],
                                         'bottom': 5
                                     }
                                 ),

                                 ' Выбери код услуги ',
                                 dcc.Dropdown(id='dropdown',
                                              options=[{'label': i, 'value': i} for i in code_list],
                                              value='code',
                                              optionHeight=10,
                                              style={
                                                  'height': '45px',
                                                  'vertical-align': 'middle',
                                                  'font-weight': 100,
                                                  'font-size': '13px',
                                                  'color': colors['text1'],
                                                  'background': colors['background3'],
                                                  'display': 'inline-block',
                                                  'width': '150px',
                                                  'bottom': 5

                                              }
                                              ),
                                 html.Div(id='date-output'),
                                 html.Div(id='intermediate-value', style={'display': 'none'}),
                                 ], className="row",
                                style={'marginTop': 0, 'marginBottom': 0, 'font-size': 25,
                                       'color': colors['background_white'],
                                       'display': 'inline-block'}),
                       html.Div(id='graph-output'),

                       html.Div(children=[html.H1(children="Текущее состояние мониторинга",
                                                  style={
                                                      'textAlign': 'center',
                                                      "fontWeight": "bold",
                                                      "background": colors['background_table'],
                                                      'font-size': 25,
                                                  }),
                                          daq.LEDDisplay(
                                              id='leddisplay_all_pu',
                                              label='ПУ на мониторинге',
                                              labelPosition='bottom',
                                              color='#00cc00',
                                              backgroundColor=colors['background2'],
                                              value=len(pd.read_sql("SELECT id FROM res_h", conn)),
                                              style={
                                                  'vertical-align': 'middle',
                                                  'display': 'inline-block',
                                                  'width': '20%',
                                                  'color': 'white'
                                              }
                                          ),
                                          daq.LEDDisplay(
                                              id='leddisplay_pu_errors',
                                              label='ПУ работают с ошибками',
                                              labelPosition='bottom',
                                              color='#00cc00',
                                              backgroundColor=colors['background2'],
                                              value=len(pd.read_sql("SELECT id FROM res_h WHERE status='error'", conn)),
                                              style={
                                                  'vertical-align': 'middle',
                                                  'display': 'inline-block',
                                                  'width': '20%',
                                                  'color': 'white'
                                              }
                                          ),
                                            daq.LEDDisplay(
                                              id='leddisplay_pu_ok',
                                              label='ПУ в состоянии ok',
                                              labelPosition='bottom',
                                              color='#00cc00',
                                              backgroundColor=colors['background2'],
                                              value=len(pd.read_sql("SELECT id FROM res_h WHERE status='ok'", conn)),
                                              style={
                                                  'vertical-align': 'middle',
                                                  'display': 'inline-block',
                                                  'width': '20%',
                                                  'color': 'white'

                                              }
                                            ),
                                            daq.LEDDisplay(
                                              id='leddisplay_pu_format',
                                              label='ПУ с ошибкой формата',
                                              labelPosition='bottom',
                                              color='#00cc00',
                                              backgroundColor=colors['background2'],
                                              value=len(pd.read_sql("SELECT id FROM res_h WHERE status='format'", conn)),
                                              style={
                                                  'vertical-align': 'middle',
                                                  'display': 'inline-block',
                                                  'width': '20%',
                                                  'color': 'white'
                                              }
                                          ),
                                            daq.LEDDisplay(
                                              id='leddisplay_pu_shadow',
                                              label='ПУ с невыведенной услугой',
                                              labelPosition='bottom',
                                              color='#00cc00',
                                              backgroundColor=colors['background2'],
                                              value=len(pd.read_sql("SELECT id FROM res_h WHERE status='усгуга не выведена'", conn)),
                                              style={
                                                  'vertical-align': 'middle',
                                                  'display': 'inline-block',
                                                  'width': '20%',
                                                  'color': 'white'
                                              }
                                          ),
                                          ]),
                       html.Div(children=[html.Table(id='table'), html.Div(id='table-output')]),
                       html.Div(children=[dcc.Markdown(" © 2020 [CKASSA](https://ckassa.ru)  All Rights Reserved.")],
                                style={
                           'textAlign': 'center',
                           "background": colors['background3']}),
                       ],
                      style={"background": colors['background3'],
                             'font-family': 'Verdana, Geneva, Arial, sans-serif'}
                      )


@app.callback(Output('table-output', 'children'),
              [Input('dropdown', 'value')])
def get_data_table(option):
    df['operation_time'] = pd.to_datetime(df['operation_time'])
    data_table = dash_table.DataTable(
        id='datatable-data',
        data=df.to_dict('records'),
        columns=[{'id': c, 'name': c} for c in df.columns],
        page_size=25,
        page_action='native',
        filter_action='native',
        sort_mode="multi",
        sort_action="native",
        style_cell={'width': '100px'},
        style_header={'backgroundColor': colors['background_table'],
                      'fontWeight': 'bold',
                      'textAlign': 'left'},
        style_data_conditional=[
            {'textAlign': 'left',
             'border': '1px solid gray',
             'color': '#506784'},  # цвет текста
            {'if': {
                'column_id': 'category',
                'filter_query': '{category} eq "A"'},
                "fontWeight": "bold"},
            {'if': {'column_id': 'status',
                    'filter_query': '{status} eq "еrror"'},
             'backgroundColor': '#ffafdc'}
        ]
    )
    conn.commit()
    return data_table


@app.callback(Output('graph-output', 'children'),
              [Input('date-input', 'start_date'),
               Input('date-input', 'end_date'),
               Input('dropdown', 'value')])
def render_graph(start_date, end_date, option):
    df = pd.read_sql(f"SELECT id, operation_time, code, status from global_answers_data WHERE code = '{option}'", conn)
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
                 'name': 'value1',
                 },
            ],
            'layout': {
                'title': f'{option.capitalize()} Пульс клиента',
                'plot_bgcolor': colors['background_table'],  # фон диаграммы
                'paper_bgcolor': colors['background_white'],  # фон за графиком
                'font': {
                    'color': colors['text'],
                    'size': 14
                },
                'xaxis': {
                    'title': 'Дата и Время',
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
                    'spikesnap': 'cursor',
                    'zeroline': 'False',
                },

            }
        }
    )


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
