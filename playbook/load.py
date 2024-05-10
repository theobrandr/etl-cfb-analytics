import os
import pandas as pd
import sqlite3
from datetime import date
from datetime import datetime
from .pregame import timestamp

def sqlite_query_table_by_year(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    #query = f"SELECT * FROM {table_name}"
    query = f"""
        SELECT t1.*
        FROM {table_name} t1
        JOIN (
            SELECT season, MAX(timestamp) AS max_timestamp
            FROM {table_name}
            GROUP BY season
        ) t2
        ON t1.season = t2.season AND t1.timestamp = t2.max_timestamp
    """
    df_table = pd.read_sql_query(query, conn)
    conn.close()
    return df_table

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

def insert_cfbd_to_sqlite(cfb_table_name,df_cfbd_data):
    conn = sqlite3.connect('blitzanalytics.db')

    if 'timestamp' not in df_cfbd_data.columns:
        df_cfbd_data['timestamp'] = timestamp
    df_cfbd_data.to_sql(cfb_table_name, conn, if_exists='append', index=False)
    conn.close()

def insert_data_to_sqlite(data_table_name,df_data):
    conn = sqlite3.connect('blitzanalytics.db')
    if 'timestamp' not in df_data.columns:
        df_data['timestamp'] = timestamp
    df_cfbd_data.to_sql(cfb_table_name, conn, if_exists='append', index=False)
    conn.close()
