import os
import json
import requests
from datetime import date
from datetime import datetime
import dotenv
import sqlite3
import pandas as pd
from playbook.pregame import timestamp

#Load Enviroment Variables
dotenv.load_dotenv()
#Variables

#Year and week variables for CFB API
current_year = date.today().year
previous_year = current_year - 1
previous_years_range = list(range(previous_year, previous_year - 5, -1))
years = list(range(current_year, current_year - 5, -1))
weeks = list(range(1,16))

#File path and file variables
cwd = os.getcwd()
file_env = dotenv.find_dotenv()

#CFB API Variables
cfb_api_key = os.environ.get('env_cfb_api_key')
cfb_url = 'https://api.collegefootballdata.com/'
headers_cfb = {'accept': 'application/json', 'Authorization': ('Bearer' + ' ' + str(cfb_api_key)), }

def default_json_to_df(response_json):
    df_cfbd_response = pd.json_normalize(response_json, errors='ignore')
    df_cfbd_response['timestamp'] = timestamp
    return df_cfbd_response

def cfbd_api_request(cfbd_request_url):
    try:
        response = requests.get((cfbd_request_url), headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
        return None
    response_json = json.loads(response.text)
    return response_json

def remove_duplicate_data_with_team_year_week_sqlite(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    cursor = conn.cursor()
    delete_query = f"""
    DELETE FROM {table_name}
    WHERE (season, school, week, timestamp) NOT IN (
        SELECT season, school, week, MAX(timestamp)
        FROM {table_name}
        GROUP BY season, school, week
    );
    """
    cursor.execute(delete_query)
    conn.commit()
    conn.close()

def remove_duplicate_data_with_team_year_statname_sqlite(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    cursor = conn.cursor()
    delete_query = f"""
    DELETE FROM {table_name}
    WHERE (season, team, statName, timestamp) NOT IN (
        SELECT season, team, statName, MAX(timestamp)
        FROM {table_name}
        GROUP BY season, team, statName
    );
    """
    cursor.execute(delete_query)
    conn.commit()
    conn.close()

def remove_duplicate_data_with_team_and_year_sqlite(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    cursor = conn.cursor()
    delete_query = f"""
    DELETE FROM {table_name}
    WHERE (season, team, timestamp) NOT IN (
        SELECT season, team, MAX(timestamp)
        FROM {table_name}
        GROUP BY season, team
    );
    """
    cursor.execute(delete_query)
    conn.commit()
    conn.close()

def remove_duplicate_data_with_id_sqlite(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    cursor = conn.cursor()
    delete_query = f"""
    DELETE FROM {table_name}
    WHERE (id, timestamp) NOT IN (
        SELECT id, MAX(timestamp)
        FROM {table_name}
        GROUP BY id
    );
    """
    cursor.execute(delete_query)
    conn.commit()
    conn.close()

def remove_duplicate_data_with_gameid_sqlite(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    cursor = conn.cursor()
    delete_query = f"""
    DELETE FROM {table_name}
    WHERE (gameId, timestamp) NOT IN (
        SELECT gameId, MAX(timestamp)
        FROM {table_name}
        GROUP BY gameId
    );
    """
    cursor.execute(delete_query)
    conn.commit()
    conn.close()

def remove_duplicate_data_timestamp_only_sqlite(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    cursor = conn.cursor()
    delete_query = f"""
    DELETE FROM {table_name}
    WHERE timestamp != (
        SELECT MAX(timestamp)
        FROM {table_name}
    );
    """
    cursor.execute(delete_query)
    conn.commit()
    conn.close()

def insert_cfbd_to_sqlite(cfb_table_name,df_cfbd_data):
    conn = sqlite3.connect('blitzanalytics.db')
    df_cfbd_data.to_sql(cfb_table_name, conn, if_exists='append', index=False)
    conn.close()

def cfbd_team_info():
    request_url = str(cfb_url + str('teams'))
    response_json = cfbd_api_request(request_url)
    df_cfbd_data = default_json_to_df(response_json)
    df_cfbd_data['timestamp'] = timestamp
    df_cfbd_data['logos'] = df_cfbd_data['logos'].astype(str)
    insert_cfbd_to_sqlite('cfb_extract_team_info', df_cfbd_data)
    remove_duplicate_data_timestamp_only_sqlite('cfb_extract_team_info')

def cfbd_venue_info():
    request_url = str(cfb_url + str('venues'))
    response_json = cfbd_api_request(request_url)
    df_cfbd_data = default_json_to_df(response_json)
    insert_cfbd_to_sqlite('cfb_extract_venue_info', df_cfbd_data)
    remove_duplicate_data_timestamp_only_sqlite('cfb_extract_venue_info')

def cfbd_coach_info():
    request_url = str(cfb_url + str('coaches?minYear=2010'))
    response_json = cfbd_api_request(request_url)
    df_cfbd_data = pd.json_normalize(response_json, record_path=['seasons'], meta=['first_name', 'last_name'],
                                                errors='ignore')
    df_cfbd_data['timestamp'] = timestamp
    insert_cfbd_to_sqlite('cfb_extract_coach_info', df_cfbd_data)
    remove_duplicate_data_timestamp_only_sqlite('cfb_extract_coach_info')

def cfbd_fbs_season_games(years):
    for year in years:
        #Get Regular Season Matchup Data
        request_url_regular_season = str(cfb_url + str('games?year=' + str(year) + '&seasonType=regular&division=fbs'))
        response_json_regular_season = cfbd_api_request(request_url_regular_season)
        df_cfbd_data_regular_season = default_json_to_df(response_json_regular_season)
        #Get Post Season Matchup Data
        request_url_post_season = str(cfb_url + str('games?year=' + str(year) + '&seasonType=postseason&division=fbs'))
        response_json_post_season = cfbd_api_request(request_url_post_season)
        df_cfbd_data_post_season = default_json_to_df(response_json_post_season)
        #Combine the Regular Season and Post Season data
        df_cfbd_data = pd.concat([df_cfbd_data_regular_season, df_cfbd_data_post_season], ignore_index=True)
        df_cfbd_data['home_line_scores'] = df_cfbd_data['home_line_scores'].astype(str)
        df_cfbd_data['away_line_scores'] = df_cfbd_data['away_line_scores'].astype(str)
        insert_cfbd_to_sqlite('cfb_extract_season_games', df_cfbd_data)
        remove_duplicate_data_with_id_sqlite('cfb_extract_season_games')

def cfbd_team_records(years):
    # Create blank dataframe
    for year in years:
        request_url = str(cfb_url + str('records?year=' + str(year)))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data_original = default_json_to_df(response_json)
        df_cfbd_data = df_cfbd_data_original.rename(columns={"year": "season"})
        if df_cfbd_data.empty:
            continue
        else:
            insert_cfbd_to_sqlite('cfb_extract_team_records', df_cfbd_data)
            remove_duplicate_data_with_team_and_year_sqlite('cfb_extract_team_records')

def cfbd_season_stats(years):
    for year in years:
        request_url = str(cfb_url + str('stats/season?year=' + str(year)))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        insert_cfbd_to_sqlite('cfb_extract_season_stats', df_cfbd_data)
        remove_duplicate_data_with_team_year_statname_sqlite('cfb_extract_season_stats')

def cfbd_rankings(years):
    for year in years:
        request_url = str(cfb_url + str('rankings?year=' + str(year) + '&seasonType=regular'))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data_normalized = pd.json_normalize(response_json, record_path=['polls', 'ranks'],
                                                          meta=['week', 'season', ['polls', 'poll']], errors='ignore')
        if df_cfbd_data_normalized.empty:
            continue
        else:
            df_cfbd_data_normalized = df_cfbd_data_normalized[["polls.poll", "week", "rank", "school", "season"]]
            df_cfbd_data_normalized = df_cfbd_data_normalized.rename(columns={"polls.poll": "Poll Name"})
            df_cfbd_data = df_cfbd_data_normalized.pivot_table(index=['week', 'school', 'season'], columns=['Poll Name'],
                                                                values='rank').reset_index()
            df_cfbd_data['timestamp'] = timestamp
            column_name = 'Playoff Committee Rankings'
            if column_name not in df_cfbd_data.columns:
                df_cfbd_data['Playoff Committee Rankings'] = ''
            insert_cfbd_to_sqlite('cfb_extract_rankings', df_cfbd_data)
            remove_duplicate_data_with_team_year_week_sqlite('cfb_extract_rankings')

def cfbd_epa(years):
    for year in years:
        request_url = str(cfb_url + str('ppa/games?year=' + str(year) + '&seasonType=regular'))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        if df_cfbd_data.empty:
            continue
        else:
            insert_cfbd_to_sqlite('cfb_extract_epa', df_cfbd_data)
            remove_duplicate_data_with_gameid_sqlite('cfb_extract_epa')

def cfbd_odds_per_game(years):
    for year in years:
        request_url = str(cfb_url + str('metrics/wp/pregame?year=' + str(year) + '&seasonType=regular'))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        if df_cfbd_data.empty:
            continue
        else:
            insert_cfbd_to_sqlite('cfb_extract_odds_per_game', df_cfbd_data)
            remove_duplicate_data_with_gameid_sqlite('cfb_extract_odds_per_game')

def cfbd_stats_per_game(years):
    for year in years:
        request_url = str(cfb_url + str('stats/game/advanced?year=' + str(year)))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        if df_cfbd_data.empty:
            continue
        else:
            df_cfbd_data['season'] = year
            insert_cfbd_to_sqlite('cfb_extract_stats_per_game', df_cfbd_data)
            remove_duplicate_data_with_gameid_sqlite('cfb_extract_stats_per_game')
