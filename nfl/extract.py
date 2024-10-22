import os
import json
import requests
import dotenv
import sqlite3
import pandas as pd
import nfl.load
import nfl.pregame

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

def api_request_with_parameters(request_url, params):
    try:
        response = requests.get(request_url, params=params)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
        return None

    response_json = json.loads(response.text)
    return response_json


def espn_nfl_teams():
    print("Extracting NFL Teams")
    request_url = str('https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams')
    response_json = api_request(request_url)
    df_nfl_data = pd.json_normalize(response_json, record_path=['sports','leagues','teams'],  errors='ignore')
    df_nfl_data.drop(columns=['team.logos', 'team.links'], inplace=True)
    nfl.load.insert_data_to_sqlite('nfl_extract_teams', df_nfl_data)

def espn_nfl_scoreboard():
    print("Extracting NFL Scoreboard")
    request_url = str('https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard')
    response_json = api_request(request_url)
    df_nfl_data = pd.json_normalize(response_json, record_path=['events'],errors='ignore')
    df_nfl_data = df_nfl_data.astype(str)
    nfl.load.insert_data_to_sqlite('nfl_extract_current_week_scoreboard', df_nfl_data)

def espn_nfl_team_roster():
    print("Extracting NFL Team Rosters")
    df_espn_nfl_sql = nfl.load.sqlite_query_table('nfl_extract_teams')
    list_nfl_team_rosters = []
    for index, row in df_espn_nfl_sql.iterrows():
        team_id = row['team.id']
        team_displayname = row['team.displayName']
        request_url = str(f'https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams/{team_id}/roster')
        response_json = api_request(request_url)
        df_nfl_team_roster_data = pd.json_normalize(response_json, record_path=['athletes', 'items'], meta=[['athletes', 'position']], errors='ignore')
        df_nfl_team_roster_data.insert(0, 'team.id', team_id)
        df_nfl_team_roster_data.insert(1, 'team.displayName', team_displayname)
        list_nfl_team_rosters.append(df_nfl_team_roster_data)
    df_nfl_data = pd.concat(list_nfl_team_rosters)
    df_nfl_data = df_nfl_data.astype(str)
    nfl.load.insert_data_to_sqlite_replace('nfl_extract_team_roster', df_nfl_data)

def espn_nfl_athletes():
    print("Extracting NFL Athletes")
    print("Due to the way ESPN provides this data, this step may take a while...")
    request_url = str('https://sports.core.api.espn.com/v3/sports/football/nfl/athletes?active=true')
    def get_all_items(request_url):
        all_items = []
        # Initial request to get the total count and page count
        response = requests.get(request_url)
        data = response.json()
        total_count = data['count']
        page_count = data['pageCount']
        # Iterate through all pages
        for page_index in range(1, page_count + 1):
            # Update the pageIndex parameter in the API URL
            paginated_url = f"{request_url}&page={page_index}"
            # Make the request for the current page
            response = requests.get(paginated_url)
            data = response.json()
            # Append the items from the current page to the list
            all_items.extend(data['items'])
        return all_items
    all_items = get_all_items(request_url)
    df_nfl_data = pd.json_normalize(all_items, errors='ignore')
    nfl.load.insert_data_to_sqlite_replace('nfl_extract_athletes', df_nfl_data)

def espn_nfl_team_stats():
    print("Extracting NFL Team Stats")
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
        nfl.load.insert_data_to_sqlite('nfl_extract_team_stats', df_nfl_data)

def espn_nfl_athlete_stats():
    print("Extracting NFL Athlete Stats")
    df_espn_nfl_athletes_sql = nfl.load.sqlite_query_table('nfl_extract_athletes')
    df_espn_nfl_athletes = df_espn_nfl_athletes_sql.loc[df_espn_nfl_athletes_sql['active'] == 1]
    list_of_dfs = []

    for index, row in df_espn_nfl_athletes.iterrows():
        athlete_id = row['id']
        athlete_displayname = row['displayName']
        #request_url = f'https://site.web.api.espn.com/apis/common/v3/sports/football/nfl/athletes/{athlete_id}/overview'
        request_url = f'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/athletes/{athlete_id}/statistics/'
        response_json = api_request(request_url)
        if 'error' in response_json and response_json['error']['code'] == 404:
            continue
        else:
            df_nfl_data_athlete_original = pd.json_normalize(response_json, record_path=['splits','categories','stats'], meta=[['splits','categories','name']], errors='ignore')
            df_nfl_data_athlete_sel_col = df_nfl_data_athlete_original[['displayName','displayValue', 'splits.categories.name']]
            df_nfl_data_athlete_sel_col.rename(columns={'displayName': 'statName'}, inplace=True)
            df_nfl_data_athlete_sel_col.rename(columns={'splits.categories.name': 'categoryName'}, inplace=True)
            df_nfl_data_athlete_sel_col['categoryName.statName'] = df_nfl_data_athlete_sel_col['categoryName'] + '.' + df_nfl_data_athlete_sel_col['statName']
            df_nfl_data_athlete_sel_col.drop(columns=['categoryName', 'statName'], inplace=True)
            df_nfl_data_athlete = df_nfl_data_athlete_sel_col.pivot_table(index=None, columns='categoryName.statName', values='displayValue', aggfunc='first')
            df_nfl_data_athlete.insert(0, 'id', athlete_id)
            df_nfl_data_athlete.insert(1, 'Athlete Name', athlete_displayname)
            df_nfl_data_athlete.reset_index(drop=True, inplace=True)
            list_of_dfs.append(df_nfl_data_athlete)

        df_nfl_data = pd.concat(list_of_dfs, axis=0, ignore_index=True)
    nfl.load.insert_data_to_sqlite('nfl_extract_athlete_stats', df_nfl_data)


def espn_nfl_team_roster_stats():
    print("Extracting NFL Roster Stats")
    df_espn_nfl_sql = nfl.load.sqlite_query_table('nfl_extract_team_roster')
    list_nfl_team_roster_stats = []
    for index, row in df_espn_nfl_sql.iterrows():
        athlete_id = row['id']
        athlete_displayname = row['displayName']
        request_url = f'http://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2023/types/2/athletes/{athlete_id}/statistics/'
        response_json = api_request(request_url)
        if 'error' in response_json and response_json['error']['code'] == 404:
            continue
        else:
            df_nfl_data_athlete_original = pd.json_normalize(response_json, record_path=['splits','categories','stats'], meta=[['splits','categories','name']], errors='ignore')
            df_nfl_data_athlete_sel_col = df_nfl_data_athlete_original[['displayName','displayValue', 'splits.categories.name']]
            df_nfl_data_athlete_sel_col.rename(columns={'displayName': 'statName'}, inplace=True)
            df_nfl_data_athlete_sel_col.rename(columns={'splits.categories.name': 'categoryName'}, inplace=True)
            df_nfl_data_athlete_sel_col['categoryName.statName'] = df_nfl_data_athlete_sel_col['categoryName'] + '.' + df_nfl_data_athlete_sel_col['statName']
            df_nfl_data_athlete_sel_col.drop(columns=['categoryName', 'statName'], inplace=True)
            df_nfl_data_athlete = df_nfl_data_athlete_sel_col.pivot_table(index=None, columns='categoryName.statName', values='displayValue', aggfunc='first')
            df_nfl_data_athlete.insert(0, 'id', athlete_id)
            df_nfl_data_athlete.insert(1, 'Athlete Name', athlete_displayname)
            df_nfl_data_athlete.reset_index(drop=True, inplace=True)
            list_nfl_team_roster_stats.append(df_nfl_data_athlete)
    df_nfl_data = pd.concat(list_nfl_team_roster_stats)
    df_nfl_data = df_nfl_data.astype(str)
    nfl.load.insert_data_to_sqlite_replace('nfl_extract_team_roster', df_nfl_data)
