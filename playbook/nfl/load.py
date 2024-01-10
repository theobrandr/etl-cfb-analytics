import os
import pandas as pd
import sqlite3
from datetime import date
from datetime import datetime
from playbook.nfl.pregame import timestamp


def sqlite_query_table(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    #query = f"SELECT * FROM {table_name}"
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE timestamp = (SELECT MAX(timestamp) FROM {table_name} )
        """
    df_table = pd.read_sql_query(query, conn)
    conn.close()
    return df_table

def insert_data_to_sqlite(data_table_name,df_data):
    conn = sqlite3.connect('blitzanalytics.db')
    if 'timestamp' not in df_data.columns:
        df_data['timestamp'] = timestamp
    df_data.to_sql(data_table_name, conn, if_exists='append', index=False)
    conn.close()
