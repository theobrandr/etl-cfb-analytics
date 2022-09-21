#!/usr/local/bin/python
import os
import json
import time
import pandas as pd
import requests
import dotenv
import openpyxl
from datetime import date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
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
file_path_cfb = cwd
file_path_cfb_api = cwd + '/api_files/'
file_path_cfb_api_season_games = file_path_cfb_api + 'season-games-'
file_path_cfb_api_season_team_record = file_path_cfb_api + 'season-team-record-'
file_path_cfb_api_season_stats = file_path_cfb_api + 'season-stats-'
file_path_cfb_api_season_rankings = file_path_cfb_api + 'season-rankings-'
file_path_cfb_api_team_info = file_path_cfb_api + 'team-info'
file_path_cfb_api_venues = file_path_cfb_api + 'venues'
file_path_cfb_api_epa_per_game = file_path_cfb_api + 'epa_per_game-'
file_path_cfb_api_coach_info = file_path_cfb_api + 'coach_info'
file_path_cfb_api_odds_per_game = file_path_cfb_api + 'odds_per_game-'
file_path_cfb_reports = cwd + '/reports/'
file_path_cfb_reports_current_year = file_path_cfb_reports + str(current_year) + '/'

#CFB API Variables
cfb_api_key = os.environ.get('env_cfb_api_key')
cfb_url = 'https://api.collegefootballdata.com/'
headers_cfb = {'accept': 'application/json', 'Authorization': ('Bearer' + ' ' + str(cfb_api_key)), }

#Pregame Variables
check_api_folder_exists = os.path.exists(file_path_cfb_api)
check_reports_folder_exists = os.path.exists(file_path_cfb_reports)
check_reports_folder_current_year_exists = os.path.exists(file_path_cfb_reports_current_year)
previous_years_api_pull_status = os.environ.get('env_previous_years_api_pull_status')

#Lists for DF's
list_season_games = []
list_team_record =[]
list_stats =[]
list_rankings = []
list_team_info = []
list_venues = []
list_epa_per_game = []
list_coach_info = []
list_odds_per_game = []

list_df_cfb_season_games = []
list_df_cfb_team_record = []
list_df_cfb_season_stats_pre_pivot = []
list_df_cfb_season_stats_all = []
list_df_cfb_rankings_all = []
list_df_cfb_epa_per_game = []
list_df_cfb_coach_info = []
list_df_cfb_odds_per_game = []

def function_cfb_pregame_filepath_check():
    def function_cfb_pregame_filepath_check():
        if check_api_folder_exists == True:
            return()
        elif check_api_folder_exists == False:
            os.mkdir(file_path_cfb_api)
            return()
    def function_cfb_pregame_filepath_reports_check():
        if check_reports_folder_exists == True:
            return()
        elif check_reports_folder_exists == False:
            os.mkdir(file_path_cfb_reports)
            return()
    def function_cfb_pregame_filepath_reports_current_year_check():
        if check_reports_folder_current_year_exists == True:
            return()
        elif check_reports_folder_current_year_exists == False:
            os.mkdir(file_path_cfb_reports_current_year)
            return()
    def function_cfb_pregame_filepath_reports_current_year__weeks_check():
        for week in weeks:
            file_path_cfb_reports_current_year_week = file_path_cfb_reports_current_year + 'Week_' + str(week) + '/'
            check_reports_folder_current_year_week_exists = os.path.exists(str(file_path_cfb_reports_current_year_week))
            if check_reports_folder_current_year_week_exists == True:
                continue
            elif check_reports_folder_current_year_week_exists == False:
                os.mkdir(file_path_cfb_reports_current_year_week)
                continue

    function_cfb_pregame_filepath_check()
    function_cfb_pregame_filepath_reports_check()
    function_cfb_pregame_filepath_reports_current_year_check()
    function_cfb_pregame_filepath_reports_current_year__weeks_check()
def function_cfb_pregame_api_check():
    if len(cfb_api_key) == 64:
        return()
    elif len(cfb_api_key) < 64:
        print('Incorrect API Key in .env file.')
        print('Please obtain an API key to continue')
        print('Exiting Program')
        time.sleep(3)
        exit()

def function_cfb_pregame_api_pull_previous_years_check():
    if previous_years_api_pull_status == 'True':
        print('Skipping pull of College Football Data from ' + str(previous_years_range))
        return()
    elif previous_years_api_pull_status == 'False':
        function_cfb_extract_previous_years_api_pulls()
        os.environ["env_previous_years_api_pull_status"] = "True"
        dotenv.set_key(file_env, "env_previous_years_api_pull_status", os.environ["env_previous_years_api_pull_status"])

def function_cfb_extract_previous_years_api_pulls():
    print('Pulling College Football Data from ' + str(previous_years_range) + ', please wait...this may take a while.')
    for season_year in previous_years_range:
        #Get Games/Season Info
        try:
            response_games = requests.get(
                (str(cfb_url + str('games?year=' + str(season_year) + '&seasonType=regular&division=fbs'))),
                headers=headers_cfb)
        except requests.exceptions.RequestException as error:
            print("Error: ", error)
        list_season_games.append(response_games)
        open(str(file_path_cfb_api_season_games) + str(season_year) + '.json', 'wb').write(response_games.content)

        #Get Records
        try:
            response_records = requests.get((str(cfb_url + str('records?year=' + str(season_year)))),
                                            headers=headers_cfb)
        except requests.exceptions.RequestException as error:
            print("Error: ", error)
        list_team_record.append(response_records)
        open(str(file_path_cfb_api_season_team_record) + str(season_year) + '.json', 'wb').write(response_records.content)

        #Get Stats
        try:
            response_stats = requests.get((str(cfb_url + str('stats/season?year=' + str(season_year)))),
                                          headers=headers_cfb)
        except requests.exceptions.RequestException as error:
            print("Error: ", error)
        list_stats.append(response_stats)
        open(str(file_path_cfb_api_season_stats) + str(season_year) + '.json', 'wb').write(response_stats.content)

        #Get Rankings
        try:
            response_rankings = requests.get(
                (str(cfb_url + str('rankings?year=' + str(season_year) + '&seasonType=regular'))),
                headers=headers_cfb)
        except requests.exceptions.RequestException as error:
            print("Error: ", error)
        list_rankings.append(response_rankings)
        open(str(file_path_cfb_api_season_rankings) + str(season_year) + '.json', 'wb').write(response_rankings.content)

        #Get EPA per Game
        try:
            response_epa_per_game = requests.get(
                (str(cfb_url + str('ppa/games?year=' + str(season_year) + '&seasonType=regular'))),
                headers=headers_cfb)
        except requests.exceptions.RequestException as error:
            print("Error: ", error)
        list_epa_per_game.append(response_epa_per_game)
        open(str(file_path_cfb_api_epa_per_game) + str(season_year) + '.json', 'wb').write(response_epa_per_game.content)

        try:
            response_odds_per_game = requests.get(
                (str(cfb_url + str('metrics/wp/pregame?year=' + str(season_year) + '&seasonType=regular'))),
                headers=headers_cfb)
        except requests.exceptions.RequestException as error:
            print("Error: ", error)
        list_odds_per_game.append(response_odds_per_game)
        open(str(file_path_cfb_api_odds_per_game) + str(season_year) + '.json', 'wb').write(response_odds_per_game.content)


def function_cfb_extract_current_year_api_pull():
    print('Pulling College Football Data from ' + str(current_year))
    #Get Season Info
    try:
        response_games = requests.get(
            (str(cfb_url + str('games?year=' + str(current_year) + '&seasonType=regular&division=fbs'))),
            headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_season_games.append(response_games)
    open(str(file_path_cfb_api_season_games) + str(current_year) + '.json', 'wb').write(response_games.content)

    #Get Records
    try:
        response_records = requests.get((str(cfb_url + str('records?year=' + str(current_year)))),
                                        headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_team_record.append(response_records)
    open(str(file_path_cfb_api_season_team_record) + str(current_year) + '.json', 'wb').write(response_records.content)

    #Get Stats
    try:
        response_stats = requests.get((str(cfb_url + str('stats/season?year=' + str(current_year)))),
                                      headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_stats.append(response_stats)
    open(str(file_path_cfb_api_season_stats) + str(current_year) + '.json', 'wb').write(response_stats.content)

    #Get Rankings
    try:
        response_rankings = requests.get(
            (str(cfb_url + str('rankings?year=' + str(current_year) + '&seasonType=regular'))),
            headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_rankings.append(response_rankings)
    open(str(file_path_cfb_api_season_rankings) + str(current_year) + '.json', 'wb').write(response_rankings.content)

    #Get EPA per Game
    try:
        response_epa_per_game = requests.get(
            (str(cfb_url + str('ppa/games?year=' + str(current_year) + '&seasonType=regular'))),
            headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_epa_per_game.append(response_epa_per_game)
    open(str(file_path_cfb_api_epa_per_game) + str(current_year) + '.json', 'wb').write(response_epa_per_game.content)

    #Get Odds per Game
    try:
        response_odds_per_game = requests.get(
            (str(cfb_url + str('metrics/wp/pregame?year=' + str(current_year) + '&seasonType=regular'))),
            headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_odds_per_game.append(response_odds_per_game)
    open(str(file_path_cfb_api_odds_per_game) + str(current_year) + '.json', 'wb').write(response_odds_per_game.content)

def function_cfb_extract_team_info_api_pull():
    #Get Team Info
    try:
        response_team_info = requests.get(
            (str(cfb_url + str('teams'))),
            headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_team_info.append(response_team_info)
    open(str(file_path_cfb_api_team_info) + '.json', 'wb').write(response_team_info.content)

    #Get Venues
    try:
        response_venues = requests.get(
            (str(cfb_url + str('venues'))),
            headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_venues.append(response_venues)
    open(str(file_path_cfb_api_venues) + '.json', 'wb').write(response_venues.content)

    #Get Coach Info
    try:
        response_coach_info = requests.get(
            (str(cfb_url + str('coaches?minYear=2010'))),
            headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
    list_coach_info.append(response_coach_info)
    open(str(file_path_cfb_api_coach_info) + '.json', 'wb').write(response_coach_info.content)

def function_cfb_extract_json_to_df():
    global df_cfb_season_games_all
    global df_cfb_team_record_all
    global df_cfb_season_stats_all
    global df_cfb_ranking_all
    global df_cfb_venue
    global df_cfb_team_info
    global df_cfb_coach_info
    global df_cfb_epa_per_game_all
    global df_cfb_odds_per_game_all
    print('Extracting json data and converting to dataframes')
    for year in years:
        #Load season games data from json to dataframe
        try:
            with open (str(file_path_cfb_api_season_games) + str(year) + '.json') as cfb_season_games_json_file:
                cfb_season_games_json = json.load(cfb_season_games_json_file)
                list_df_cfb_season_games.append(pd.json_normalize(cfb_season_games_json, errors='ignore'))
        except Exception:
            continue
        #Load team record data from json to dataframe
        try:
            with open(str(file_path_cfb_api_season_team_record) + str(year) + '.json') as cfb_team_record_json_file:
                cfb_team_record_json = json.load(cfb_team_record_json_file)
                list_df_cfb_team_record.append(pd.json_normalize(cfb_team_record_json, errors='ignore'))
        except Exception:
            continue
        #Load season stats data from json to list
        try:
            with open (str(file_path_cfb_api_season_stats) + str(year) + '.json') as cfb_season_stats_json_file:
                cfb_season_stats_json = json.load(cfb_season_stats_json_file)
                list_df_cfb_season_stats_pre_pivot.append(pd.json_normalize(cfb_season_stats_json, errors='ignore'))
        except Exception:
            continue
        #Load ranking data from json to dataframe
        try:
            with open(str(file_path_cfb_api_season_rankings) + str(year) + '.json') as cfb_ranking_json_file:
                cfb_ranking_json = json.load(cfb_ranking_json_file)
                list_df_cfb_rankings_all.append(pd.json_normalize(cfb_ranking_json, record_path=['polls', 'ranks'],meta=['week','season', ['polls', 'poll']], errors='ignore'))
        except Exception:
            continue
        #Load epa per game data from json to list
        try:
            with open(str(file_path_cfb_api_epa_per_game) + str(year) + '.json') as cfb_epa_per_game_json_file:
                cfb_epa_per_game_json = json.load(cfb_epa_per_game_json_file)
                list_df_cfb_epa_per_game.append(pd.json_normalize(cfb_epa_per_game_json, errors='ignore'))
        except Exception:
            continue
        #Load odds per game data from json to list
        try:
            with open(str(file_path_cfb_api_odds_per_game) + str(year) + '.json') as cfb_odds_per_game_json_file:
                cfb_odds_per_game_json = json.load(cfb_odds_per_game_json_file)
                list_df_cfb_odds_per_game.append(pd.json_normalize(cfb_odds_per_game_json, errors='ignore'))
        except Exception:
            continue
    #Concat lists of df's into one df
    df_cfb_season_games_all = pd.concat(list_df_cfb_season_games)
    df_cfb_team_record_all = pd.concat(list_df_cfb_team_record)
    df_cfb_ranking_all = pd.concat(list_df_cfb_rankings_all)
    df_cfb_epa_per_game_all = pd.concat(list_df_cfb_epa_per_game)
    df_cfb_odds_per_game_all = pd.concat(list_df_cfb_odds_per_game)

    #Load Venue data
    with open(str(file_path_cfb_api_venues) + '.json') as cfb_venue_json_file:
        cfb_venue_json = json.load(cfb_venue_json_file)
        df_cfb_venue = pd.json_normalize(cfb_venue_json, errors='ignore')

    #Load team info
    with open(str(file_path_cfb_api_team_info) + '.json') as cfb_team_info_json_file:
        cfb_team_info_json = json.load(cfb_team_info_json_file)
        df_cfb_team_info = pd.json_normalize(cfb_team_info_json, errors='ignore')

    #Load coach info
    with open(str(file_path_cfb_api_coach_info) + '.json') as cfb_coach_info_json_file:
        cfb_coach_info_json = json.load(cfb_coach_info_json_file)
        df_cfb_coach_info = pd.json_normalize(cfb_coach_info_json, errors='ignore')

    #Transform ranking df
    df_cfb_ranking_all = df_cfb_ranking_all[["polls.poll", "week", "rank", "school", "season"]]
    df_cfb_ranking_all = df_cfb_ranking_all.rename(columns={"polls.poll": "Poll Name"})
    df_cfb_ranking_all = df_cfb_ranking_all.pivot_table(index=['week', 'school', 'season'], columns=['Poll Name'], values='rank').reset_index()


def function_cfb_transform_season_stats():
    global df_cfb_season_stats_all
    print('Transforming Season Stats')
    #Convert list to df with pivot table
    for df_season_stats_year in list_df_cfb_season_stats_pre_pivot:
        list_df_cfb_season_stats_all.append(df_season_stats_year.pivot(index=['team', 'season'], columns='statName', values='statValue').reset_index())
    df_cfb_season_stats_all_original = pd.concat(list_df_cfb_season_stats_all)
    df_cfb_season_stats_all_original.rename(columns = lambda col: f"offense_{col}"
                                                    if col in ("possessionTime", "firstDowns", "fourthDownConversions", "fourthDowns", "fumblesLost", "passAttempts",
                                                               "netPassingYards", "passesIntercepted", "passCompletions", "passingTDs", "rushingAttempts", "rushingTDs",
                                                               "rushingYards", "thirdDownConversions", "thirdDowns", "totalYards", "turnovers")
                                                    else col, inplace=True)
    df_cfb_season_stats_all_original.rename(columns=lambda col: f"defense_{col}"
                                                    if col in ("fumblesRecovered", "interceptionTDs", "interceptionYards", "interceptions", "tacklesForLoss", "sacks")
                                                    else col, inplace=True)
    df_cfb_season_stats_all_original.rename(columns=lambda col: f"specialteams_{col}"
                                                    if col in ("kickReturnTDs", "kickReturnYards", "kickReturns", "puntReturnTDs", "puntReturnYards", "puntReturns")
                                                    else col, inplace=True)
    df_cfb_season_stats_all_for_loop = df_cfb_season_stats_all_original.copy()
    list_df_cfb_season_stats_all_for_loop_by_year = []
    for year in years:
        df_cfb_season_stats_all_for_loop = df_cfb_season_stats_all_original.loc[df_cfb_season_stats_all_original['season'].astype(str).str.contains(str(year))]
        #Calculate Offense Stats
        #Possession Time
        df_cfb_season_stats_all_for_loop['offense_possessionTime_zscore'] = (df_cfb_season_stats_all_for_loop['offense_possessionTime'] - df_cfb_season_stats_all_for_loop['offense_possessionTime'].mean()) / df_cfb_season_stats_all_for_loop['offense_possessionTime'].std()
        #First Downs
        df_cfb_season_stats_all_for_loop['offense_firstDowns_zscore'] = (df_cfb_season_stats_all_for_loop['offense_firstDowns'] - df_cfb_season_stats_all_for_loop['offense_firstDowns'].mean()) / df_cfb_season_stats_all_for_loop['offense_firstDowns'].std()
        #Fourth Downs
        df_cfb_season_stats_all_for_loop['offense_fourthDownConversions_zscore'] = (df_cfb_season_stats_all_for_loop['offense_fourthDownConversions'] - df_cfb_season_stats_all_for_loop['offense_fourthDownConversions'].mean()) / df_cfb_season_stats_all_for_loop['offense_fourthDownConversions'].std()
        df_cfb_season_stats_all_for_loop['offense_fourthDowns_zscore'] = (df_cfb_season_stats_all_for_loop['offense_fourthDowns'] - df_cfb_season_stats_all_for_loop['offense_fourthDowns'].mean()) / df_cfb_season_stats_all_for_loop['offense_fourthDowns'].std()
        #Calculate Actual Fourth Down Completion Percentage
        df_cfb_season_stats_all_for_loop['offense_fourthDownConversions_percent'] = (df_cfb_season_stats_all_for_loop['offense_fourthDownConversions'] - df_cfb_season_stats_all_for_loop['offense_fourthDowns'])
        df_cfb_season_stats_all_for_loop['offense_fourthDownConversions_percent_zscore'] = (df_cfb_season_stats_all_for_loop['offense_fourthDownConversions_percent'] - df_cfb_season_stats_all_for_loop['offense_fourthDownConversions_percent'].mean()) / df_cfb_season_stats_all_for_loop['offense_fourthDownConversions_percent'].std()
        #Pass Attempts and Completions
        df_cfb_season_stats_all_for_loop['offense_passAttempts_zscore'] = (df_cfb_season_stats_all_for_loop['offense_passAttempts'] - df_cfb_season_stats_all_for_loop['offense_passAttempts'].mean()) / df_cfb_season_stats_all_for_loop['offense_passAttempts'].std()
        df_cfb_season_stats_all_for_loop['offense_passCompletions_zscore'] = (df_cfb_season_stats_all_for_loop['offense_passCompletions'] - df_cfb_season_stats_all_for_loop['offense_passCompletions'].mean()) / df_cfb_season_stats_all_for_loop['offense_passCompletions'].std()
        #Calculate Actual Pass Completion Percentage
        df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent'] = (df_cfb_season_stats_all_for_loop['offense_passCompletions'] / df_cfb_season_stats_all_for_loop['offense_passAttempts'])
        df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent_zscore'] = (df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent'] - df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent'].mean()) / df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent'].std()
        #Rushing Attempts and Total Yards
        df_cfb_season_stats_all_for_loop['offense_rushingAttempts_zscore'] = (df_cfb_season_stats_all_for_loop['offense_rushingAttempts'] - df_cfb_season_stats_all_for_loop['offense_rushingAttempts'].mean()) / df_cfb_season_stats_all_for_loop['offense_rushingAttempts'].std()
        df_cfb_season_stats_all_for_loop['offense_rushingYards_zscore'] = (df_cfb_season_stats_all_for_loop['offense_rushingYards'] - df_cfb_season_stats_all_for_loop['offense_rushingYards'].mean()) / df_cfb_season_stats_all_for_loop['offense_rushingYards'].std()
        #Calculate Average Rushing Yards
        df_cfb_season_stats_all_for_loop['offense_rushingYards_perAttempt_percent'] = (df_cfb_season_stats_all_for_loop['offense_rushingYards'] - df_cfb_season_stats_all_for_loop['offense_rushingAttempts'])
        df_cfb_season_stats_all_for_loop['offense_rushingYards_perAttempt_percent_zscore'] = (df_cfb_season_stats_all_for_loop['offense_rushingYards_perAttempt_percent'] - df_cfb_season_stats_all_for_loop['offense_rushingYards_perAttempt_percent'].mean()) / df_cfb_season_stats_all_for_loop['offense_rushingYards_perAttempt_percent'].std()
        #Third Downs and Third Down conversions
        df_cfb_season_stats_all_for_loop['offense_thirdDownConversions_zscore'] = (df_cfb_season_stats_all_for_loop['offense_thirdDownConversions'] - df_cfb_season_stats_all_for_loop['offense_thirdDownConversions'].mean()) / df_cfb_season_stats_all_for_loop['offense_thirdDownConversions'].std()
        df_cfb_season_stats_all_for_loop['offense_thirdDowns_zscore'] = (df_cfb_season_stats_all_for_loop['offense_thirdDowns'] - df_cfb_season_stats_all_for_loop['offense_thirdDowns'].mean()) / df_cfb_season_stats_all_for_loop['offense_thirdDowns'].std()
        #Calculate Actual Third Down Completion Percentage
        df_cfb_season_stats_all_for_loop['offense_thirdDownConversions_percent'] = (df_cfb_season_stats_all_for_loop['offense_thirdDownConversions'] - df_cfb_season_stats_all_for_loop['offense_thirdDowns'])
        df_cfb_season_stats_all_for_loop['offense_thirdDownConversions_percent_zscore'] = (df_cfb_season_stats_all_for_loop['offense_thirdDownConversions_percent'] - df_cfb_season_stats_all_for_loop['offense_thirdDownConversions_percent'].mean()) / df_cfb_season_stats_all_for_loop['offense_thirdDownConversions_percent'].std()
        #Totals and other stats
        df_cfb_season_stats_all_for_loop['offense_rushingTDs_zscore'] = (df_cfb_season_stats_all_for_loop['offense_rushingTDs'] - df_cfb_season_stats_all_for_loop['offense_rushingTDs'].mean()) / df_cfb_season_stats_all_for_loop['offense_rushingTDs'].std()
        df_cfb_season_stats_all_for_loop['offense_totalYards_zscore'] = (df_cfb_season_stats_all_for_loop['offense_totalYards'] - df_cfb_season_stats_all_for_loop['offense_totalYards'].mean()) / df_cfb_season_stats_all_for_loop['offense_totalYards'].std()
        df_cfb_season_stats_all_for_loop['offense_netPassingYards_zscore'] = (df_cfb_season_stats_all_for_loop['offense_netPassingYards'] - df_cfb_season_stats_all_for_loop['offense_netPassingYards'].mean()) / df_cfb_season_stats_all_for_loop['offense_netPassingYards'].std()
        df_cfb_season_stats_all_for_loop['offense_passingTDs_zscore'] = (df_cfb_season_stats_all_for_loop['offense_passingTDs'] - df_cfb_season_stats_all_for_loop['offense_passingTDs'].mean()) / df_cfb_season_stats_all_for_loop['offense_passingTDs'].std()
        #Calculate zscore for offensive stats that need to be subtracted (minus)
        df_cfb_season_stats_all_for_loop['offense_passesIntercepted_zscore_minus'] = (df_cfb_season_stats_all_for_loop['offense_passesIntercepted'] - df_cfb_season_stats_all_for_loop['offense_passesIntercepted'].mean()) / df_cfb_season_stats_all_for_loop['offense_passesIntercepted'].std()
        df_cfb_season_stats_all_for_loop['offense_fumblesLost_zscore_minus'] = (df_cfb_season_stats_all_for_loop['offense_fumblesLost'] - df_cfb_season_stats_all_for_loop['offense_fumblesLost'].mean()) / df_cfb_season_stats_all_for_loop['offense_fumblesLost'].std()
        df_cfb_season_stats_all_for_loop['offense_turnovers_zscore_minus'] = (df_cfb_season_stats_all_for_loop['offense_turnovers'] - df_cfb_season_stats_all_for_loop['offense_turnovers'].mean()) / df_cfb_season_stats_all_for_loop['offense_turnovers'].std()
        #Calculate zscore for Defense Stats
        df_cfb_season_stats_all_for_loop['defense_fumblesRecovered_zscore'] = (df_cfb_season_stats_all_for_loop['defense_fumblesRecovered'] - df_cfb_season_stats_all_for_loop['defense_fumblesRecovered'].mean()) / df_cfb_season_stats_all_for_loop['defense_fumblesRecovered'].std()
        df_cfb_season_stats_all_for_loop['defense_interceptionTDs_zscore'] = (df_cfb_season_stats_all_for_loop['defense_interceptionTDs'] - df_cfb_season_stats_all_for_loop['defense_interceptionTDs'].mean()) / df_cfb_season_stats_all_for_loop['defense_interceptionTDs'].std()
        df_cfb_season_stats_all_for_loop['defense_interceptionYards_zscore'] = (df_cfb_season_stats_all_for_loop['defense_interceptionYards'] - df_cfb_season_stats_all_for_loop['defense_interceptionYards'].mean()) / df_cfb_season_stats_all_for_loop['defense_interceptionYards'].std()
        df_cfb_season_stats_all_for_loop['defense_interceptions_zscore'] = (df_cfb_season_stats_all_for_loop['defense_interceptions'] - df_cfb_season_stats_all_for_loop['defense_interceptions'].mean()) / df_cfb_season_stats_all_for_loop['defense_interceptions'].std()
        df_cfb_season_stats_all_for_loop['defense_tacklesForLoss_zscore'] = (df_cfb_season_stats_all_for_loop['defense_tacklesForLoss'] - df_cfb_season_stats_all_for_loop['defense_tacklesForLoss'].mean()) / df_cfb_season_stats_all_for_loop['defense_tacklesForLoss'].std()
        df_cfb_season_stats_all_for_loop['sacks_zscore'] = (df_cfb_season_stats_all_for_loop['defense_sacks'] - df_cfb_season_stats_all_for_loop['defense_sacks'].mean()) / df_cfb_season_stats_all_for_loop['defense_sacks'].std()
        #Calculate zscore for special teams stats
        df_cfb_season_stats_all_for_loop['specialteams_kickReturnTDs_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_kickReturnTDs'] - df_cfb_season_stats_all_for_loop['specialteams_kickReturnTDs'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_kickReturnTDs'].std()
        df_cfb_season_stats_all_for_loop['specialteams_kickReturnYards_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_kickReturnYards'] - df_cfb_season_stats_all_for_loop['specialteams_kickReturnYards'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_kickReturnYards'].std()
        df_cfb_season_stats_all_for_loop['specialteams_kickReturns_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_kickReturns'] - df_cfb_season_stats_all_for_loop['specialteams_kickReturns'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_kickReturns'].std()
        df_cfb_season_stats_all_for_loop['specialteams_puntReturnTDs_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_puntReturnTDs'] - df_cfb_season_stats_all_for_loop['specialteams_puntReturnTDs'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_puntReturnTDs'].std()
        df_cfb_season_stats_all_for_loop['specialteams_puntReturnYards_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_puntReturnYards'] - df_cfb_season_stats_all_for_loop['specialteams_puntReturnYards'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_puntReturnYards'].std()
        df_cfb_season_stats_all_for_loop['specialteams_puntReturns_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_puntReturns'] - df_cfb_season_stats_all_for_loop['specialteams_puntReturns'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_puntReturns'].std()
        #Fill NA with 0 and Sum zscore columns
        df_cfb_season_stats_all_for_loop.fillna(0,inplace=True)
        df_cfb_season_stats_all_for_loop['offense_plus_zscore_sum'] = df_cfb_season_stats_all_for_loop.filter(regex='offense_[a-zA-Z]+_zscore').sum(axis=1)
        df_cfb_season_stats_all_for_loop['offense_minus_zscore_sum'] = df_cfb_season_stats_all_for_loop.filter(regex='offense_[a-zA-Z]+_zscore_minus').sum(axis=1)
        df_cfb_season_stats_all_for_loop['offense_zscore_final'] = df_cfb_season_stats_all_for_loop['offense_plus_zscore_sum'] - df_cfb_season_stats_all_for_loop['offense_minus_zscore_sum']
        df_cfb_season_stats_all_for_loop['defense_zscore_final'] = df_cfb_season_stats_all_for_loop.filter(regex='defense_[a-zA-Z]+_zscore').sum(axis=1)
        df_cfb_season_stats_all_for_loop['specialteams_zscore_final'] = df_cfb_season_stats_all_for_loop.filter(regex='specialteams_[a-zA-Z]+_zscore').sum(axis=1)
        df_cfb_season_stats_all_for_loop['total_zscore'] = df_cfb_season_stats_all_for_loop['offense_zscore_final'] + df_cfb_season_stats_all_for_loop['defense_zscore_final'] + df_cfb_season_stats_all_for_loop['specialteams_zscore_final']
        list_df_cfb_season_stats_all_for_loop_by_year.append(df_cfb_season_stats_all_for_loop)
    df_cfb_season_stats_all = pd.concat(list_df_cfb_season_stats_all_for_loop_by_year)
    '''
    df_cfb_season_stats_all_sel_col = df_cfb_season_stats_all[[
        'team', 'season', 'games', 'offense_plus_zscore_sum', 'offense_minus_zscore_sum', 'offense_zscore_final',
        'defense_zscore_final', 'specialteams_zscore_final', 'total_zscore']]
    df_cfb_season_stats_all_sel_col_sorted = df_cfb_season_stats_all_sel_col.sort_values(by=['team','season'], ascending=True, na_position='first')
    df_cfb_season_stats_all_sel_col_sorted["games_year"] = df_cfb_season_stats_all_sel_col_sorted[['season', 'games']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_stats_all_sel_col_sorted_groupby = df_cfb_season_stats_all_sel_col_sorted.groupby(['team'])['games_year'].agg(", ".join).reset_index()
    '''

def function_cfb_transform_games_and_stats():
    global df_cfb_season_games_all_updated
    global df_cfb_season_games_all
    print('Transforming Game Matchups')
    # Clean up Team Info Data
    df_drop_cfb_teaminfo = df_cfb_team_info.dropna(subset=['conference'])
    df_select_col_cfb_teaminfo = df_drop_cfb_teaminfo[["id", "school", "conference", "location.venue_id","location.name","location.zip"]]

    #Add Column for Game Matchup and calculate average points given up by week
    df_cfb_season_games_all["Game Matchup"] = df_cfb_season_games_all[['away_team', 'home_team']].apply(" @ ".join, axis=1)

    #Split the home v away into 2 df
    df_cfb_season_games_all_home = df_cfb_season_games_all[["id", "Game Matchup", "season", "week", "start_date", "conference_game", "home_team", "home_conference", "home_points"]]
    df_cfb_season_games_all_home.rename(columns={"home_team": "team", "home_conference": "conference","home_points": "points"},inplace=True)
    df_cfb_season_games_all_home.insert(7, "home_vs_away", 'home')
    df_cfb_season_games_all_away = df_cfb_season_games_all[["id", "Game Matchup", "season", "week", "start_date", "conference_game", "away_team", "away_conference", "away_points"]]
    df_cfb_season_games_all_away.rename(columns={"away_team": "team", "away_conference": "conference", "away_points": "points"},inplace=True)
    df_cfb_season_games_all_away.insert(7, "home_vs_away", 'away')

    #Merge home and away df back together and sort them into order
    df_cfb_season_games_all_append = df_cfb_season_games_all_home.append(df_cfb_season_games_all_away)
    df_cfb_season_games_all_append['start_date'] = df_cfb_season_games_all_append['start_date'].str.replace('.000Z','')
    df_cfb_season_games_all_append['start_date'] = pd.to_datetime(df_cfb_season_games_all_append['start_date'],infer_datetime_format=True,errors='coerce')
    df_cfb_season_games_all_append.sort_values(by=['start_date','id'], inplace=True, ascending=True)
    df_cfb_season_games_all_updated = df_cfb_season_games_all_append
    df_cfb_season_games_all_updated.fillna(0, inplace=True)
    df_cfb_season_games_all_updated['points'].astype('int64')
    df_cfb_season_games_all_updated["date"] = pd.to_datetime(df_cfb_season_games_all_updated["start_date"], format="%Y/%m/%d")

def function_cfb_transform_games_and_agg_scores():
    global df_cfb_season_games_agg_scores
    print('Transforming Home and Away Aggregate Scores')
    #Transform average scores for home and away
    #Transform Home game scores
    df_cfb_season_games_home_group_scores = df_cfb_season_games_all[['home_team', 'home_points', 'season']]
    df_cfb_season_games_home_group_scores = df_cfb_season_games_home_group_scores.rename(columns={"home_team": "team"})
    df_cfb_season_games_home_group_scores_grouped_by_season = df_cfb_season_games_home_group_scores.groupby(['team','season']).agg(home_points_season_mean = ('home_points','mean'), home_points_season_max = ('home_points', 'max'), home_points_season_min = ('home_points', 'min')).reset_index()
    df_cfb_season_games_home_group_scores_grouped_by_total_years = df_cfb_season_games_home_group_scores.groupby(['team']).agg(home_points_mean_over_the_years = ('home_points','mean'), home_points_max_over_the_years = ('home_points', 'max'), home_points_min_over_the_years = ('home_points', 'min')).reset_index()
    df_cfb_season_games_home_agg_scores_merged = pd.merge(df_cfb_season_games_home_group_scores_grouped_by_season, df_cfb_season_games_home_group_scores_grouped_by_total_years, left_on='team', right_on='team', how='left')

    #Transform Away game scores
    df_cfb_season_games_away_group_scores = df_cfb_season_games_all[['away_team', 'away_points', 'season']]
    df_cfb_season_games_away_group_scores = df_cfb_season_games_away_group_scores.rename(columns={"away_team": "team"})
    df_cfb_season_games_away_group_scores_grouped_by_season = df_cfb_season_games_away_group_scores.groupby(['team','season']).agg(away_points_season_mean = ('away_points','mean'), away_points_season_max = ('away_points', 'max'), away_points_season_min = ('away_points', 'min')).reset_index()
    df_cfb_season_games_away_group_scores_grouped_by_total_years = df_cfb_season_games_away_group_scores.groupby(['team']).agg(away_points_mean_over_the_years = ('away_points','mean'), away_points_max_over_the_years = ('away_points', 'max'), away_points_min_over_the_years = ('away_points', 'min')).reset_index()
    df_cfb_season_games_away_agg_scores_merged = pd.merge(df_cfb_season_games_away_group_scores_grouped_by_season, df_cfb_season_games_away_group_scores_grouped_by_total_years, left_on='team', right_on='team', how='left')
    #Transform Merge Home and Away scores together
    df_cfb_season_games_agg_scores = pd.merge(df_cfb_season_games_home_agg_scores_merged, df_cfb_season_games_away_agg_scores_merged, left_on=['team','season'], right_on=['team','season'], how='left')

def function_cfb_transform_odds():
    global df_cfb_odds_per_game_with_calc
    global df_cfb_season_games_odds_for_summary
    print('Transforming Odds/Spread')
    #Transform odds per game
    #Prep the odds data
    df_cfb_odds_per_game_rename = df_cfb_odds_per_game_all.rename(columns={"gameId": "id", "homeWinProb": "home_team_WinProb" })
    df_cfb_odds_per_game_all_select_col = df_cfb_odds_per_game_rename.drop(columns=['season', 'week', 'homeTeam', 'awayTeam','seasonType'])
    df_cfb_season_games_all_for_odds = df_cfb_season_games_all[['id','season','week','home_team', 'home_points', 'away_team', 'away_points']]

    #Join the odds data on to the existing season games all data from above and rename it
    df_cfb_season_games_all_updated_odds_per_game_join = pd.merge(df_cfb_season_games_all_for_odds, df_cfb_odds_per_game_all_select_col, left_on=['id'],right_on=['id'], how='left')
    df_cfb_season_games_odds = df_cfb_season_games_all_updated_odds_per_game_join

    #Calculate the game point difference between to compare against the spread
    df_cfb_season_games_odds['game_point_diff'] = df_cfb_season_games_odds['away_points'] - df_cfb_season_games_odds['home_points']

    #Determine if the home team covered the spread with text and with an integer for additional analytics
    df_cfb_season_games_odds['home_team_result_of_the_spread'] = 'no result'
    df_cfb_season_games_odds.loc[df_cfb_season_games_odds['game_point_diff'] < df_cfb_season_games_odds['spread'],'home_team_result_of_the_spread'] = 'covered the spread'
    df_cfb_season_games_odds.loc[df_cfb_season_games_odds['game_point_diff'] == df_cfb_season_games_odds['spread'],'home_team_result_of_the_spread'] = 'tied the spread'
    df_cfb_season_games_odds.loc[df_cfb_season_games_odds['game_point_diff'] > df_cfb_season_games_odds['spread'],'home_team_result_of_the_spread'] = 'failed to cover the spread'
    df_cfb_season_games_odds['home_team_result_of_the_spread_int'] = '0'
    df_cfb_season_games_odds['home_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("covered the spread", case=False, na=False)] = '1'
    df_cfb_season_games_odds['home_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("tied the spread", case=False, na=False)] = '0'
    df_cfb_season_games_odds['home_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("failed to cover the spread", case=False, na=False)] = '0'

    # Determine if the away team covered the spread with text and with an integer for additional analytics
    df_cfb_season_games_odds['away_team_result_of_the_spread'] = 'no result'
    df_cfb_season_games_odds['away_team_result_of_the_spread'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("covered the spread", case=False, na=False)] = 'failed to cover the spread'
    df_cfb_season_games_odds['away_team_result_of_the_spread'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("tied the spread", case=False, na=False)] = 'tied the spread'
    df_cfb_season_games_odds['away_team_result_of_the_spread'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("failed to cover the spread", case=False, na=False)] = 'covered the spread'
    df_cfb_season_games_odds['away_team_result_of_the_spread_int'] = '0'
    df_cfb_season_games_odds['away_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("covered the spread", case=False, na=False)] = '0'
    df_cfb_season_games_odds['away_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("tied the spread", case=False, na=False)] = '0'
    df_cfb_season_games_odds['away_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("failed to cover the spread", case=False, na=False)] = '1'

    #Make the result of the spread an integer
    df_cfb_season_games_odds_astype = df_cfb_season_games_odds.astype({"away_team_result_of_the_spread_int": int,"home_team_result_of_the_spread_int": int })

    #Drop any row with null data in the spread column
    df_cfb_season_games_odds_drop_na = df_cfb_season_games_odds_astype[df_cfb_season_games_odds_astype['spread'].notnull()]

    #Calculate the average and total spread by year for the home team using group bys
    df_cfb_season_games_odds_groupby_home = df_cfb_season_games_odds_drop_na.groupby(['home_team', 'season']).agg(home_team_average_number_of_times_covered_the_spread_per_year = ('home_team_result_of_the_spread_int','mean'), home_team_number_of_times_covered_the_spread_per_year = ('home_team_result_of_the_spread_int', 'sum')).round(2).reset_index()
    df_cfb_season_games_odds_groupby_home["home_team_average_spread_covered_by_year"] = df_cfb_season_games_odds_groupby_home[['season', 'home_team_average_number_of_times_covered_the_spread_per_year']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_games_odds_groupby_home["home_team_total_spread_covered_by_year"] = df_cfb_season_games_odds_groupby_home[['season', 'home_team_number_of_times_covered_the_spread_per_year']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_games_odds_groupby_combined_rows_home = df_cfb_season_games_odds_groupby_home.groupby('home_team')['home_team_average_spread_covered_by_year','home_team_total_spread_covered_by_year'].agg(", ".join).reset_index()
    df_cfb_season_games_odds_groupby_combined_rows_home['home_team_average_spread_covered_by_year'] = 'Spread AVG While Home: ' + df_cfb_season_games_odds_groupby_combined_rows_home['home_team_average_spread_covered_by_year']
    df_cfb_season_games_odds_groupby_combined_rows_home['home_team_total_spread_covered_by_year'] = 'Spread Covered While Home: ' + df_cfb_season_games_odds_groupby_combined_rows_home['home_team_total_spread_covered_by_year']
    df_cfb_season_games_odds_groupby_combined_rows_home["home_vs_away"] = 'home'

    # Calculate the average and total spread by year for the away team using groupbys
    df_cfb_season_games_odds_groupby_away = df_cfb_season_games_odds_drop_na.groupby(['away_team', 'season']).agg(away_team_average_number_of_times_covered_the_spread_per_year = ('away_team_result_of_the_spread_int','mean'), away_team_number_of_times_covered_the_spread_per_year = ('away_team_result_of_the_spread_int', 'sum')).round(2).reset_index()
    df_cfb_season_games_odds_groupby_away["away_team_average_spread_covered_by_year"] = df_cfb_season_games_odds_groupby_away[['season', 'away_team_average_number_of_times_covered_the_spread_per_year']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_games_odds_groupby_away["away_team_total_spread_covered_by_year"] = df_cfb_season_games_odds_groupby_away[['season', 'away_team_number_of_times_covered_the_spread_per_year']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_games_odds_groupby_combined_rows_away = df_cfb_season_games_odds_groupby_away.groupby('away_team')['away_team_average_spread_covered_by_year','away_team_total_spread_covered_by_year'].agg(", ".join).reset_index()
    df_cfb_season_games_odds_groupby_combined_rows_away['away_team_average_spread_covered_by_year'] = 'Spread AVG While Away: ' + df_cfb_season_games_odds_groupby_combined_rows_away['away_team_average_spread_covered_by_year']
    df_cfb_season_games_odds_groupby_combined_rows_away['away_team_total_spread_covered_by_year'] = 'Spread Covered While Away: ' + df_cfb_season_games_odds_groupby_combined_rows_away['away_team_total_spread_covered_by_year']
    df_cfb_season_games_odds_groupby_combined_rows_away["home_vs_away"] = 'away'

    #Join the home team calculated spread data on to the original odds data, then rename and drop columns for upcoming appending
    df_cfb_season_games_odds_join_groupby_combined_rows_home = pd.merge(df_cfb_season_games_odds_drop_na, df_cfb_season_games_odds_groupby_combined_rows_home, left_on=['home_team'], right_on=['home_team'], how='left')
    df_cfb_season_games_odds_join_groupby_combined_rows_home_rename = df_cfb_season_games_odds_join_groupby_combined_rows_home.rename(columns={"home_team": "team", "home_points": "points",
                                                                                                                                               "home_team_result_of_the_spread": "result_of_the_spread", "home_team_average_spread_covered_by_year": "average_spread_covered_by_year",
                                                                                                                                                "home_team_total_spread_covered_by_year": "total_spread_covered_by_year" })
    df_cfb_season_games_odds_join_groupby_combined_rows_home_rename_drop = df_cfb_season_games_odds_join_groupby_combined_rows_home_rename.loc[:, ~df_cfb_season_games_odds_join_groupby_combined_rows_home_rename.columns.str.contains('^away_', case=False)].drop(columns=['home_team_result_of_the_spread_int'])

    #Join the away team calculated spread data on to the original odds data, then rename and drop columns for upcoming appending
    df_cfb_season_games_odds_join_groupby_combined_rows_away = pd.merge(df_cfb_season_games_odds_drop_na, df_cfb_season_games_odds_groupby_combined_rows_away, left_on=['away_team'], right_on=['away_team'], how='left')
    df_cfb_season_games_odds_join_groupby_combined_rows_away_rename = df_cfb_season_games_odds_join_groupby_combined_rows_away.rename(columns={"away_team": "team", "away_points": "points",
                                                                                                                                               "away_team_result_of_the_spread": "result_of_the_spread", "away_team_average_spread_covered_by_year": "average_spread_covered_by_year",
                                                                                                                                                "away_team_total_spread_covered_by_year": "total_spread_covered_by_year","home_vs_away": "h_vs_a" })
    df_cfb_season_games_odds_join_groupby_combined_rows_away_rename_drop = df_cfb_season_games_odds_join_groupby_combined_rows_away_rename.loc[:, ~df_cfb_season_games_odds_join_groupby_combined_rows_away_rename.columns.str.contains('^home_', case=False)].drop(columns=['away_team_result_of_the_spread_int'])
    df_cfb_season_games_odds_join_groupby_combined_rows_away_rename_drop = df_cfb_season_games_odds_join_groupby_combined_rows_away_rename_drop.rename(columns={"h_vs_a": "home_vs_away" })

    #Append the away odds data with spread calculations onto the home odds data with spread calculations and sort
    df_cfb_season_games_odds_append = df_cfb_season_games_odds_join_groupby_combined_rows_home_rename_drop.append(df_cfb_season_games_odds_join_groupby_combined_rows_away_rename_drop)
    df_cfb_season_games_odds_append.sort_values(by=['id'], inplace=True, ascending=True)

    #Group odds data for summmary view
    df_cfb_season_games_odds_groupby_home_for_summary = df_cfb_season_games_odds_groupby_home.rename(columns={"home_team": "team"})
    df_cfb_season_games_odds_groupby_away_for_summary = df_cfb_season_games_odds_groupby_away.rename(columns={"away_team": "team"})
    df_cfb_season_games_odds_groupby_join_home_and_away_for_summary = pd.merge(df_cfb_season_games_odds_groupby_home_for_summary, df_cfb_season_games_odds_groupby_away_for_summary,
                                                         left_on=['team', 'season'], right_on=['team', 'season'], how='left')
    df_cfb_season_games_odds_groupby_join_home_and_away_for_summary_drop = df_cfb_season_games_odds_groupby_join_home_and_away_for_summary.loc[:, ~df_cfb_season_games_odds_groupby_join_home_and_away_for_summary.columns.str.contains('by_year', case=False)]

    df_cfb_season_games_odds_for_summary = df_cfb_season_games_odds_groupby_join_home_and_away_for_summary_drop

    #Select on the odds columns needed for joining onto the main dataframe
    df_cfb_season_games_odds_append_sel_col = df_cfb_season_games_odds_append[['id','team','spread','home_team_WinProb','game_point_diff','result_of_the_spread', 'average_spread_covered_by_year','total_spread_covered_by_year',]]
    df_cfb_odds_per_game_with_calc = df_cfb_season_games_odds_append_sel_col

def function_cfb_transform_epa():
    global df_cfb_epa_per_game
    global df_cfb_epa_per_season_for_summary
    print('Transforming EPA')
    #Transform EPA
    df_cfb_epa_per_game_all_rename_col = df_cfb_epa_per_game_all.rename(columns={"gameId": "id"})
    df_cfb_epa_per_game_all_rename_col.columns = df_cfb_epa_per_game_all_rename_col.columns.str.replace("^offense", "epa_per_game_offense", regex=True)
    df_cfb_epa_per_game_all_rename_col.columns = df_cfb_epa_per_game_all_rename_col.columns.str.replace("^defense", "epa_per_game_defense", regex=True)
    df_cfb_epa_per_game_all_rename_col_with_epa = df_cfb_epa_per_game_all_rename_col.loc[:,df_cfb_epa_per_game_all_rename_col.columns.str.contains('^epa_per_game', case=False)]
    column_names = df_cfb_epa_per_game_all_rename_col_with_epa.columns.values.tolist()
    df_cfb_epa_per_game_all_rename_col_looped = pd.DataFrame
    for column_name in column_names:
        df_cfb_epa_per_game_all_rename_col[column_name] = df_cfb_epa_per_game_all_rename_col[column_name].astype(float).round(2)

    df_cfb_epa_per_game = df_cfb_epa_per_game_all_rename_col

    df_cfb_epa_per_game_all_rename_col_groupby = df_cfb_epa_per_game_all_rename_col.groupby(['team', 'season']).agg(epa_per_game_offense_overall_avg_per_season = ('epa_per_game_offense.overall', 'mean'),
                                                                                                                    epa_per_game_defense_overall_avg_per_season = ('epa_per_game_defense.overall', 'mean')).round(2).reset_index()
    df_cfb_epa_per_season_for_summary = df_cfb_epa_per_game_all_rename_col_groupby

def function_cfb_transform_polls():
    global df_cfb_ranking_groupby_ap
    global df_cfb_ranking_all_updated
    print('Transforming Polls/Rankings')
    df_cfb_ranking_all_rm_null_ap = df_cfb_ranking_all[df_cfb_ranking_all['AP Top 25'].notnull()]
    df_cfb_ranking_all_rename = df_cfb_ranking_all_rm_null_ap.rename(columns={"school": "team"})
    df_cfb_ranking_all_drop = df_cfb_ranking_all_rename.drop(columns=['AFCA Division II Coaches Poll','AFCA Division III Coaches Poll','FCS Coaches Poll'], errors='ignore')
    df_cfb_ranking_all_drop['AP Top 25'] = df_cfb_ranking_all_drop['AP Top 25'].astype(int).astype(str)
    df_cfb_ranking_all_drop['Week with prefix'] = 'w' + df_cfb_ranking_all_drop['week'].astype(str)
    df_cfb_ranking_all_drop["AP Top 25 by Week"] = df_cfb_ranking_all_drop[
        ['Week with prefix', 'AP Top 25']].astype(str).apply(":".join, axis=1)
    df_cfb_ranking_groupby_ap = df_cfb_ranking_all_drop.groupby(['team', 'season'])['AP Top 25 by Week'].agg(", ".join).reset_index()
    df_cfb_ranking_all_updated = df_cfb_ranking_all_drop

def  function_cfb_transform_team_records():
    global df_cfb_team_record_all_select_col
    print('Transforming Team Records')
    #Transform Team Records
    df_cfb_team_record_all_rename = df_cfb_team_record_all.rename(columns={"year": "season"})
    df_cfb_team_record_all_select_col = df_cfb_team_record_all_rename[["team", "season","total.wins", "total.losses", "conferenceGames.wins", "conferenceGames.losses"]]
def function_cfb_transform_team_info():
    global df_cfb_team_info_updated
    df_cfb_team_info_rename = df_cfb_team_info.rename(columns={"school": "team"})
    df_cfb_team_info_updated = df_cfb_team_info_rename.loc[df_cfb_team_info_rename['classification'].str.contains("fbs|fcs", case=False, na=False)]

def function_cfb_transform_summary_data():
    global cfb_summary_join_record_rank_agg_zscores_epa_sorted
    print('Transforming Summary Dataset')
    #CFB Seasons Stats zscores for summary
    df_cfb_season_stats_zscores_for_summary = df_cfb_season_stats_all[[
        'team', 'season', 'games', 'offense_plus_zscore_sum', 'offense_minus_zscore_sum', 'offense_zscore_final',
        'defense_zscore_final', 'specialteams_zscore_final', 'total_zscore']]

    #CFB Season Games Score Calculation for summary
    df_cfb_season_games_agg_scores_for_summary = df_cfb_season_games_agg_scores[['team','season','home_points_season_mean','home_points_mean_over_the_years','away_points_season_mean','away_points_mean_over_the_years']]

    #CFB Team Wins and Losses by Year for summary
    df_cfb_team_record_all_select_col_for_summary = df_cfb_team_record_all_select_col

    #CFB Top 25 Ranking for summary
    df_cfb_ranking_for_summary = df_cfb_ranking_groupby_ap

    # CFB Join dataframes for summary
    cfb_summary_join_record_and_rankings = pd.merge(df_cfb_team_record_all_select_col_for_summary,
                                                    df_cfb_ranking_for_summary,
                                                    left_on=['team', 'season'],
                                                    right_on=['team', 'season'], how='left')
    cfb_summary_join_record_rank_and_agg_scores = pd.merge(cfb_summary_join_record_and_rankings,
                                                           df_cfb_season_games_agg_scores_for_summary,
                                                           left_on=['team', 'season'],
                                                           right_on=['team', 'season'], how='left')
    cfb_summary_join_record_rank_agg_and_zscores_scores = pd.merge(cfb_summary_join_record_rank_and_agg_scores,
                                                                   df_cfb_season_stats_zscores_for_summary,
                                                                   left_on=['team', 'season'],
                                                                   right_on=['team', 'season'], how='left')
    cfb_summary_join_record_rank_agg_zscores_epa = pd.merge(cfb_summary_join_record_rank_agg_and_zscores_scores,
                                                            df_cfb_epa_per_season_for_summary,
                                                            left_on=['team', 'season'],
                                                            right_on=['team', 'season'], how='left')
    cfb_summary_join_record_rank_agg_zscores_epa_sorted = cfb_summary_join_record_rank_agg_zscores_epa.sort_values(by=['team', 'season'], ascending=True, na_position='first')

def function_cfb_transform_data_for_load():
    global cfb_all_data
    global cfb_summary
    global cfb_games_with_spread_analytics
    global cfb_season_stats_by_season
    global cfb_team_info
    global cfb_season_week_matchups
    global cfb_season_week_matchups_home_updated

    print('Transforming datasets for loading')
    #Transform df's with stats and merge on games
    df_cfb_games_and_stats = pd.merge(df_cfb_season_games_all_updated, df_cfb_season_stats_all,
                                      left_on=['team','season'], right_on=['team','season'], how='left')

    #Transform merge (games and stats) with (agg scores)
    df_cfb_games_stats_agg_scores = pd.merge(df_cfb_games_and_stats, df_cfb_season_games_agg_scores,
                                             left_on=['team','season'], right_on=['team','season'], how='left')

    #Transform Join Coach Poll / Rankings with Games/Stats/Agg Scores df
    df_cfb_games_stats_agg_scores_rankings = pd.merge(df_cfb_games_stats_agg_scores,df_cfb_ranking_all_updated ,
                                                      left_on=['team','week','season'],right_on=['team','week','season'], how='left')

    #Transform Join Rankings/Games/Stats/Agg Scores with Records
    df_cfb_games_stats_agg_scores_rankings_team_records = pd.merge(df_cfb_games_stats_agg_scores_rankings, df_cfb_team_record_all_select_col,
                                                                   left_on=['team','season'],right_on=['team','season'], how='left')

    #Transform Join EPA per Game on Rankings/Games/Stats/Agg Scores with Records
    df_cfb_epa_per_game_all_select_col = df_cfb_epa_per_game.drop(
        columns=['season', 'week', 'conference', 'opponent'])
    df_cfb_games_stats_agg_scores_rankings_team_records_epa = pd.merge(df_cfb_games_stats_agg_scores_rankings_team_records, df_cfb_epa_per_game_all_select_col,
        left_on=['id', 'team'], right_on=['id', 'team'], how='left')

    #Transform Join Rankings/Games/Stats/Agg Scores/EPA with Odds
    df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds = pd.merge(df_cfb_games_stats_agg_scores_rankings_team_records_epa, df_cfb_odds_per_game_with_calc,
        left_on=['id', 'team'], right_on=['id', 'team'], how='left')
    for col in df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds:
        # get dtype for column
        datatype = df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds[col].dtype
        # check if it is a number
        if datatype == int or datatype == float:
            df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds[col].fillna(0, inplace=True)
        else:
            df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds[col].fillna("No Data", inplace=True)


    #Transform Join Coach Poll / Rankings with Games/Stats/Agg Scores df
    df_cfb_season_games_all_updated_join_rankings = pd.merge(df_cfb_season_games_all_updated, df_cfb_ranking_all_updated,
                                                      left_on=['team', 'week', 'season'],
                                                      right_on=['team', 'week', 'season'], how='left')

    #General Game data joined with odds
    df_cfb_season_games_all_updated_join_odds = pd.merge(df_cfb_season_games_all_updated, df_cfb_odds_per_game_with_calc,
                                                        left_on=['id', 'team'], right_on=['id', 'team'], how='left')
    for col in df_cfb_season_games_all_updated_join_odds:
        # get dtype for column
        datatype = df_cfb_season_games_all_updated_join_odds[col].dtype
        # check if it is a number
        if datatype == int or datatype == float:
            df_cfb_season_games_all_updated_join_odds[col].fillna(0, inplace=True)
        else:
            df_cfb_season_games_all_updated_join_odds[col].fillna("No Data", inplace=True)

    #CFB Games/Matchups by Season and Week
    cfb_season_week_matchups = df_cfb_season_games_all
    cfb_season_week_matchups_home_updated = df_cfb_season_games_all_updated

    #CFB Team Info
    cfb_team_info = df_cfb_team_info_updated

    #CFB Season Games Score Calculation
    cfb_season_games_agg_scores = df_cfb_season_games_agg_scores

    #CFB Team Wins and Losses by Year
    cfb_team_record_by_year = df_cfb_team_record_all_select_col

    #CFB Games with odds/spread
    cfb_games_with_spread_analytics = df_cfb_season_games_all_updated_join_odds

    #CFB Games with all advanced stats
    cfb_season_stats_by_season = df_cfb_season_stats_all

    #CFB Summary Data
    cfb_summary = cfb_summary_join_record_rank_agg_zscores_epa_sorted

    #CFB All Data
    cfb_all_data = df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds
def function_cfb_reporting_current_year():
    print('Generating Reports')
    df_cfb_for_reporting_game_matchup = cfb_season_week_matchups.loc[cfb_season_week_matchups['season'].astype(str).str.contains(str(current_year), regex=False, case=False, na=False)]
    for week in cfb_season_week_matchups['week']:
        file_path_cfb_reports_current_year_week = file_path_cfb_reports_current_year + 'Week_' + str(week) + '/'
        for index, row in df_cfb_for_reporting_game_matchup.iterrows():
            home_team = row['home_team']
            away_team = row['away_team']
            matchup = row['Game Matchup']
            df_home_team = cfb_all_data.loc[cfb_all_data['team'] == home_team]
            df_away_team = cfb_all_data.loc[cfb_all_data['team'] == away_team]
            home_team_color = cfb_team_info.loc[cfb_team_info['team'] == home_team, 'color'].iloc[0]
            away_team_color = cfb_team_info.loc[cfb_team_info['team'] == away_team, 'color'].iloc[0]
            df_home_away_append = pd.concat([df_home_team,df_away_team],ignore_index=True)

            fig_matchup_team_points = sns.catplot(data=df_home_away_append, x="week", y="points", col="season", kind='bar', hue="team", palette={home_team:home_team_color, away_team:away_team_color})
            fig_matchup_result_of_the_spread = sns.catplot(data=df_home_away_append, x="result_of_the_spread", kind="count", col="season", hue="team", palette={home_team:home_team_color, away_team:away_team_color})
            fig_matchup_result_of_the_spread.set_xticklabels(rotation=65, horizontalalignment='right')

            list_figures = [fig_matchup_team_points, fig_matchup_result_of_the_spread]

            filename_team_report = file_path_cfb_reports_current_year_week + str(matchup) + ".pdf"
            pp = PdfPages(filename_team_report)
            for fig in list_figures:
                fig.savefig(pp, format='pdf')
            pp.close()
            plt.close('all')
            print('Report Generated for ' + str(matchup))


def funtion_cfb_load_to_excel():
    print('Loading Datasets to xlsx')
    with pd.ExcelWriter(str(file_path_cfb) + '/cfb.xlsx') as writer:
        cfb_summary.to_excel(writer, sheet_name='cfb_summary', engine='xlsxwriter')
        cfb_games_with_spread_analytics.to_excel(writer, sheet_name='cfb_games_spread', engine='xlsxwriter')
        cfb_season_stats_by_season.to_excel(writer, sheet_name='cfb_season_stats_by_season', engine='xlsxwriter')
        cfb_season_games_agg_scores.to_excel(writer, sheet_name='cfb_games_scores', engine='xlsxwriter')
        cfb_team_record_by_year.to_excel(writer, sheet_name='cfb_team_record', engine='xlsxwriter')
        cfb_all_data.to_excel(writer, sheet_name='cfb_all_data', engine='xlsxwriter')

#CFB ETL
function_cfb_pregame_filepath_check()
function_cfb_pregame_api_check()
function_cfb_pregame_api_pull_previous_years_check()
function_cfb_extract_current_year_api_pull()
function_cfb_extract_team_info_api_pull()
function_cfb_extract_json_to_df()
function_cfb_transform_season_stats()
function_cfb_transform_games_and_stats()
function_cfb_transform_games_and_agg_scores()
function_cfb_transform_odds()
function_cfb_transform_epa()
function_cfb_transform_polls()
function_cfb_transform_team_records()
function_cfb_transform_team_info()
function_cfb_transform_summary_data()
function_cfb_transform_data_for_load()
function_cfb_reporting_current_year()
funtion_cfb_load_to_excel()

