import os
import json
import requests
from datetime import date
from datetime import datetime
import dotenv
import sqlite3
import pandas as pd
from .pregame import timestamp

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
    #cfbd_int_columns = df_cfbd_response.select_dtypes(include=['int']).columns
    #df_cfbd_response[cfbd_int_columns] = df_cfbd_response[cfbd_int_columns].fillna(0)
    #df_cfbd_response.fillna("None", inplace=True)
    return df_cfbd_response

def cfbd_api_request(cfbd_request_url):
    try:
        response = requests.get((cfbd_request_url), headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
        return None

    response_json = json.loads(response.text)
    return response_json

def remove_old_extracted_data(cfb_table_name,df_cfbd_data):
    conn = sqlite3.connect('blitzanalytics.db')
    # query = f"SELECT * FROM {table_name}"
    query = f"""
            DELETE FROM {table_name}
            WHERE (ID, timestamp) NOT IN (
                SELECT ID, MAX(timestamp) AS latest_date
                FROM {table_name}
                GROUP BY ID
            );
            """
    df_table = pd.read_sql_query(query, conn)
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
    #df_cfbd_data.drop('logos', axis=1, inplace=True)
    insert_cfbd_to_sqlite('extract_team_info', df_cfbd_data)

def cfbd_venue_info():
    request_url = str(cfb_url + str('venues'))
    response_json = cfbd_api_request(request_url)
    df_cfbd_data = default_json_to_df(response_json)
    insert_cfbd_to_sqlite('extract_venue_info', df_cfbd_data)

def cfbd_coach_info():
    request_url = str(cfb_url + str('coaches?minYear=2010'))
    response_json = cfbd_api_request(request_url)
    df_cfbd_data = pd.json_normalize(response_json, record_path=['seasons'], meta=['first_name', 'last_name'],
                                                errors='ignore')
    df_cfbd_data['timestamp'] = timestamp
    insert_cfbd_to_sqlite('extract_coach_info', df_cfbd_data)

def cfbd_fbs_season_games(years):
    for year in years:
        request_url = str(cfb_url + str('games?year=' + str(year) + '&seasonType=regular&division=fbs'))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        df_cfbd_data['home_line_scores'] = df_cfbd_data['home_line_scores'].astype(str)
        df_cfbd_data['away_line_scores'] = df_cfbd_data['away_line_scores'].astype(str)
        insert_cfbd_to_sqlite('extract_season_games', df_cfbd_data)

def cfbd_team_records(years):
    for year in years:
        request_url = str(cfb_url + str('records?year=' + str(year)))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data_original = default_json_to_df(response_json)
        df_cfbd_data = df_cfbd_data_original.rename(columns={"year": "season"})
        insert_cfbd_to_sqlite('extract_team_records', df_cfbd_data)

def cfbd_season_stats(years):
    for year in years:
        request_url = str(cfb_url + str('stats/season?year=' + str(year)))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        insert_cfbd_to_sqlite('extract_season_stats', df_cfbd_data)

def cfbd_rankings(years):
    for year in years:
        request_url = str(cfb_url + str('rankings?year=' + str(year) + '&seasonType=regular'))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data_normalized = pd.json_normalize(response_json, record_path=['polls', 'ranks'],
                                                          meta=['week', 'season', ['polls', 'poll']], errors='ignore')
        df_cfbd_data_normalized = df_cfbd_data_normalized[["polls.poll", "week", "rank", "school", "season"]]
        df_cfbd_data_normalized = df_cfbd_data_normalized.rename(columns={"polls.poll": "Poll Name"})
        df_cfbd_data = df_cfbd_data_normalized.pivot_table(index=['week', 'school', 'season'], columns=['Poll Name'],
                                                            values='rank').reset_index()
        df_cfbd_data['timestamp'] = timestamp
        column_name = 'Playoff Committee Rankings'
        if column_name not in df_cfbd_data.columns:
            df_cfbd_data['Playoff Committee Rankings'] = ''

        insert_cfbd_to_sqlite('extract_rankings', df_cfbd_data)

def cfbd_epa(years):
    for year in years:
        request_url = str(cfb_url + str('ppa/games?year=' + str(year) + '&seasonType=regular'))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        insert_cfbd_to_sqlite('extract_epa', df_cfbd_data)

def cfbd_odds_per_game(years):
    for year in years:
        request_url = str(cfb_url + str('metrics/wp/pregame?year=' + str(year) + '&seasonType=regular'))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        insert_cfbd_to_sqlite('extract_odds_per_game', df_cfbd_data)

def cfbd_stats_per_game(years):
    for year in years:
        request_url = str(cfb_url + str('stats/game/advanced?year=' + str(year)))
        response_json = cfbd_api_request(request_url)
        df_cfbd_data = default_json_to_df(response_json)
        df_cfbd_data['season'] = year
        insert_cfbd_to_sqlite('extract_stats_per_game', df_cfbd_data)

