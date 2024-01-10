import os
import json
import requests
import dotenv
import sqlite3
import pandas as pd
import playbook.nfl.load
import playbook.nfl.pregame

#File path and file variables
cwd = os.getcwd()
file_env = dotenv.find_dotenv()

def api_request(request_url):
    try:
        response = requests.get((request_url))
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


def nfl_teams():
    request_url = str('https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams')
    response_json = api_request(request_url)
    df_nfl_data = pd.json_normalize(response_json, record_path=['sports','leagues','teams'],  errors='ignore')
    df_nfl_data.drop(columns=['team.logos', 'team.links'], inplace=True)
    playbook.nfl.load.insert_data_to_sqlite('nfl_extract_teams', df_nfl_data)

def nfl_scoreboard():
    request_url = str('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard')
    response_json = api_request(request_url)
    df_nfl_data = pd.json_normalize(response_json, record_path=['events'],errors='ignore')
    df_nfl_data = df_nfl_data.astype(str)
    playbook.nfl.load.insert_data_to_sqlite('nfl_extract_current_week_scoreboard', df_nfl_data)

def nfl_athletes():
    request_url = str('https://sports.core.api.espn.com/v3/sports/football/nfl/athletes')
    response_json = api_request(request_url)
    df_nfl_data = pd.json_normalize(response_json, record_path=['items'], errors='ignore')
    playbook.nfl.load.insert_data_to_sqlite('nfl_extract_teams', df_nfl_data)

def nfl_team_stats():
    request_url_nfl_teams = str('https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams')
    response_json_nfl_teams = api_request(request_url_nfl_teams)
    df_nfl_teams = pd.json_normalize(response_json_nfl_teams, record_path=['sports', 'leagues', 'teams'], errors='ignore')
    for team in df_nfl_teams['team.id']:
        request_url = f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team}/statistics'
        response_json = api_request(request_url)
        df_nfl_data_stats_top_level = pd.json_normalize(response_json, errors='ignore')
        df_nfl_data_stats_categories = pd.json_normalize(response_json, record_path=['results','stats','categories','stats'], meta=[['results','stats','categories','name']], meta_prefix='category_name_', errors='ignore')
        df_nfl_data_stats_categories['team.id'] = df_nfl_data_stats_top_level['team.id'][0]
        df_nfl_data = pd.merge(df_nfl_data_stats_categories, df_nfl_data_stats_top_level, on='team.id', how='outer', )
        df_nfl_data.drop(columns=['results.stats.categories'], inplace=True)
        df_nfl_data = df_nfl_data.astype(str)
        playbook.nfl.load.insert_data_to_sqlite('nfl_extract_team_stats', df_nfl_data)



