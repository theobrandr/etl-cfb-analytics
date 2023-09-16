import os
import pandas as pd
import sqlite3
from datetime import date
from datetime import datetime
from .pregame import timestamp

def sqlite_query_table_by_year(table_name):
    conn = sqlite3.connect('blitzalytics.db')
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
    conn = sqlite3.connect('blitzalytics.db')
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
    conn = sqlite3.connect('blitzalytics.db')

    if 'timestamp' not in df_cfbd_data.columns:
        df_cfbd_data['timestamp'] = timestamp
    df_cfbd_data.to_sql(cfb_table_name, conn, if_exists='append', index=False)
    conn.close()


def data_to_excel():
    print('Loading Datasets to xlsx')
    with pd.ExcelWriter(str(file_path_cfb) + '/cfb.xlsx') as writer:
        cfb_summary.to_excel(writer, sheet_name='cfb_summary', engine='xlsxwriter')
        cfb_games_with_spread_analytics.to_excel(writer, sheet_name='cfb_games_spread', engine='xlsxwriter')
        cfb_season_stats_by_season.to_excel(writer, sheet_name='cfb_season_stats_by_season', engine='xlsxwriter')
        cfb_season_games_agg_scores.to_excel(writer, sheet_name='cfb_games_scores', engine='xlsxwriter')
        cfb_team_record_by_year.to_excel(writer, sheet_name='cfb_team_record', engine='xlsxwriter')
        cfb_stats_per_game.to_excel(writer, sheet_name=' cfb_stats_per_game', engine='xlsxwriter')
        cfb_all_data.to_excel(writer, sheet_name='cfb_all_data', engine='xlsxwriter')