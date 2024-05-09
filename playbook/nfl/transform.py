import sqlite3
import pandas as pd
import playbook.nfl.load
import playbook.nfl.pregame

def espn_team_stats_oponent():
    df_espn_nfl_teams_stats_sql = playbook.nfl.load.sqlite_query_table('nfl_extract_team_stats')
    df_espn_nfl_teams_stats_opponent = pd.json_normalize(df_espn_nfl_teams_stats_sql[['results.opponent']])
    print()