import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
from datetime import datetime
import dash_table
import pandas as pd
import sqlite3
import dash
import dash_daq as daq

conn = sqlite3.connect('postmon.sqlite', check_same_thread=False)
cursor = conn.cursor()


def get_len_all_pu():
    all_pu = pd.read_sql("SELECT id FROM res_h", conn)
    return len(all_pu)


print(type(get_len_all_pu()))