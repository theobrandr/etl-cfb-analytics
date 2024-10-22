import sqlite3
import pandas as pd
import nfl.load
import nfl.pregame

def espn_team_stats_oponent():
    print("Transforming NFL Team Stats by Oponent")
    df_espn_nfl_teams_stats_sql = nfl.load.sqlite_query_table('nfl_extract_team_stats')
    df_espn_nfl_teams_stats_opponent = pd.json_normalize(df_espn_nfl_teams_stats_sql[['results.opponent']])
    print()