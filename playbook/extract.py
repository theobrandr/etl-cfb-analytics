import os
import json
import requests
from datetime import date
from datetime import datetime
import dotenv
import sqlite3

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

#Datetimestamp to insert into DB during each extraction
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def cfbd_api_request(cfbd_request_url):
    try:
        response = requests.get((cfbd_request_url), headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
        return None
    return response.content

def sqlite_insert_json_data(conn, cfb_table_name, json_data):
    insert_query = f"""
    INSERT INTO {cfb_table_name} (json_data, timestamp)
    VALUES (?, ?)
    """
    conn.execute(insert_query, (json_data, timestamp))
    conn.commit()

def sqlite_conn_and_insert_cfb_info(cfb_table_name,cfbd_request_url):
    conn = sqlite3.connect('blitzalytics.db')
    create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {cfb_table_name} (
            id INTEGER PRIMARY KEY,
            json_data BLOB,
            timestamp TEXT
        )
        """
    conn.execute(create_table_query)
    conn.commit()

    data = cfbd_api_request(cfbd_request_url)

    if data:
        sqlite_insert_json_data(conn, cfb_table_name, data)

    conn.close()

def cfbd_team_info():
    request_url = str(cfb_url + str('teams'))
    sqlite_conn_and_insert_cfb_info('team_info', request_url)

def cfbd_venue_info():
    request_url = str(cfb_url + str('venues'))
    sqlite_conn_and_insert_cfb_info('venue_info', request_url)

def cfbd_coach_info():
    request_url = str(cfb_url + str('coaches?minYear=2010'))
    sqlite_conn_and_insert_cfb_info('coach_info', request_url)

def cfbd_fbs_season_games(years):
    for year in years:
        request_url = str(cfb_url + str('games?year=' + str(year) + '&seasonType=regular&division=fbs'))
        sqlite_conn_and_insert_cfb_info('season_games', request_url)

def cfbd_records(years):
    for year in years:
        request_url = str(cfb_url + str('records?year=' + str(year)))
        sqlite_conn_and_insert_cfb_info('records', request_url)

def cfbd_stats(years):
    for year in years:
        request_url = str(cfb_url + str('stats/season?year=' + str(year)))
        sqlite_conn_and_insert_cfb_info('stats', request_url)

def cfbd_rankings(years):
    for year in years:
        request_url = str(cfb_url + str('rankings?year=' + str(year) + '&seasonType=regular'))
        sqlite_conn_and_insert_cfb_info('rankings', request_url)

def cfbd_epa():
    for year in years:
        request_url = str(cfb_url + str('ppa/games?year=' + str(year) + '&seasonType=regular'))
        sqlite_conn_and_insert_cfb_info('epa', request_url)

def cfbd_odds_per_game(years):
    for year in years:
        request_url = str(cfb_url + str('metrics/wp/pregame?year=' + str(year) + '&seasonType=regular'))
        sqlite_conn_and_insert_cfb_info('odds_per_game', request_url)

def cfbd_stats_per_game(years):
    for year in years:
        request_url = str(cfb_url + str('stats/game/advanced?year=' + str(year)))
        sqlite_conn_and_insert_cfb_info('stats_per_game', request_url)



