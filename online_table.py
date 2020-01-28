import dash
import dash_table
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import sqlite3

conn = sqlite3.connect('postmon.sqlite')
cursor = conn.cursor()

df = pd.read_sql("SELECT id, operation_time, code, category, timeout, status FROM res_h", conn)

###################
### Визуализация ##
###################

app = dash.Dash(__name__)

app.layout = dash_table.DataTable(
    id='datatable-interactivity',
    columns=[{"name": i, "id": i} for i in df.columns],
    data=df.to_dict('records'),
    page_size=100,
    page_action='native',
    sort_mode="multi",
    filter_action='native',
    sort_action="native",
    style_data={
        'whiteSpace': 'normal',
        'height': 'auto'
    },
    style_header={
        'backgroundColor': 'rgb(230, 230, 230)',
        'fontWeight': 'bold',
        'textAlign': 'left',
        'border': '1px solid gray',
    },
    style_data_conditional=[
        {
            'textAlign': 'left',
            'border': '1px solid gray',
            'color': '#506784'
        },
        {
            'if': {
                'column_id': 'category',
                'filter_query': '{category} eq "A"',
            },
            "fontWeight": "bold"
        },
        {
            'if': {
                'column_id': 'category',
                'filter_query': '{category} eq "A"',
                'column_id': 'status',
                'filter_query': '{status} eq "Error"'
            },
            'backgroundColor': "#ff6b80"
        }
    ],
)

###########################
###Манипуляции с данными###
###########################


def len_all_pu():
    _len = cursor.execute('SELECT id FROM res_h').fetchall()
    conn.commit()
    return len(_len)


if __name__ == '__main__':
    app.run_server(debug=True)