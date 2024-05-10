import os
import dotenv
from datetime import date
from datetime import datetime
import sqlite3
import requests
import json

#Load Enviroment Variables
dotenv.load_dotenv()

#Datetimestamp to insert into DB
global timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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

def filepath_check(arg_report_year):
    # Year and week variables for CFB API
    report_year = arg_report_year
    # File path and file variables
    cwd = os.getcwd()
    file_env = dotenv.find_dotenv()
    file_path_sport = cwd
    file_path_sport_reports = cwd + '/reports/'
    file_path_sport_reports_cfb = file_path_sport_reports + 'cfb/'
    file_path_sport_reports_report_year = file_path_sport_reports_cfb + str(report_year) + '/'
    file_path_sport_reports_report_year_teams = file_path_sport_reports_report_year + 'Teams' + '/'
    file_path_sport_reports_report_year_regular_season = file_path_sport_reports_report_year + str('regular') + '/'
    file_path_sport_reports_report_year_post_season = file_path_sport_reports_report_year + str('postseason') + '/'

    check_reports_folder = os.path.exists(file_path_sport_reports)
    check_reports_folder_cfb = os.path.exists(file_path_sport_reports_cfb)
    check_reports_folder_report_year = os.path.exists(file_path_sport_reports_report_year)
    check_reports_folder_report_year_teams = os.path.exists(file_path_sport_reports_report_year_teams)
    check_reports_folder_report_year_regular_season = os.path.exists(file_path_sport_reports_report_year_regular_season)
    check_reports_folder_report_year_post_season = os.path.exists(file_path_sport_reports_report_year_post_season)

    def filepath_reports_check():
        if check_reports_folder == True:
            return()
        elif check_reports_folder == False:
            os.mkdir(file_path_sport_reports)
            return()
    def filepath_reports_cfb_check():
        if check_reports_folder_cfb == True:
            return()
        elif check_reports_folder_cfb == False:
            os.mkdir(file_path_sport_reports_cfb)
            return()

    def filepath_reports_report_year_check():
        if check_reports_folder_report_year == True:
            return()
        elif check_reports_folder_report_year == False:
            os.mkdir(file_path_sport_reports_report_year)
            return()

    def filepath_reports_report_year_teams_check():
        if check_reports_folder_report_year_teams == True:
            return()
        elif check_reports_folder_report_year_teams == False:
            os.mkdir(file_path_sport_reports_report_year_teams)
            return()

    def filepath_reports_report_year_regular_season_check():
        if check_reports_folder_report_year_regular_season == True:
            return()
        elif check_reports_folder_report_year_regular_season == False:
            os.mkdir(file_path_sport_reports_report_year_regular_season)
            return()

    def filepath_reports_report_year_post_season_check():
        if check_reports_folder_report_year_post_season == True:
            return ()
        elif check_reports_folder_report_year_post_season == False:
            os.mkdir(file_path_sport_reports_report_year_post_season)
            return ()

    def filepath_reports_report_year_weeks_check():
        weeks = list(range(1, 16))
        for week in weeks:
            path_reports_folder_report_year_week = file_path_sport_reports_report_year + 'Week_' + str(week) + '/'
            check_reports_folder_report_year_week = os.path.exists(str(path_reports_folder_report_year_week))
            if check_reports_folder_report_year_week == True:
                continue
            elif check_reports_folder_report_year_week == False:
                os.mkdir(path_reports_folder_report_year_week)
                continue

    def filepath_reports_report_year_regular_season_weeks_check():
        weeks = list(range(1, 16))
        for week in weeks:
            path_reports_folder_report_year_regular_season_week = file_path_sport_reports_report_year_regular_season + 'Week_' + str(week) + '/'
            check_reports_folder_report_year_week_regular_season = os.path.exists(str(path_reports_folder_report_year_regular_season_week))
            if check_reports_folder_report_year_week_regular_season == True:
                continue
            elif check_reports_folder_report_year_week_regular_season == False:
                os.mkdir(path_reports_folder_report_year_regular_season_week)
                continue
    def filepath_reports_report_year_post_season_weeks_check():
        weeks = list(range(1, 3))
        for week in weeks:
            path_reports_folder_report_year_post_season_week = file_path_sport_reports_report_year_post_season + 'Week_' + str(week) + '/'
            check_reports_folder_report_year_week_post_season = os.path.exists(str(path_reports_folder_report_year_post_season_week))
            if check_reports_folder_report_year_week_post_season == True:
                continue
            elif check_reports_folder_report_year_week_post_season == False:
                os.mkdir(path_reports_folder_report_year_post_season_week)
                continue

    filepath_reports_check()
    filepath_reports_cfb_check()
    filepath_reports_report_year_check()
    filepath_reports_report_year_teams_check()
    filepath_reports_report_year_regular_season_check()
    filepath_reports_report_year_post_season_check()
    #filepath_reports_report_year_weeks_check()
    filepath_reports_report_year_regular_season_weeks_check()
    filepath_reports_report_year_post_season_weeks_check()

    return(print("Pregame Filepath Checks Complete"))

def api_key_check():
    cfb_api_key = os.environ.get('env_cfb_api_key')
    if len(cfb_api_key) == 64:
        return(print("Api Key Valid"))
    elif len(cfb_api_key) < 64:
        error_message = [
            'Incorrect API Key in .env file.',
            'Please obtain an API key to continue.',
            'Exiting Program'
        ]
        exit('\n'.join(error_message))

def check_sqllite_db():
    # Testing Connection to sqlite CFB.DB
    connection = sqlite3.connect("blitzanalytics.db")
    cursor = connection.cursor()
    sql_version_query = 'select sqlite_version();'
    cursor.execute(sql_version_query)
    result_sql_version_query = cursor.fetchall()
    print('SQLite Version is {}'.format(result_sql_version_query))
    cursor.close()
    connection.close()

def delete_all_tables():
    print("Warning, this will delete all the tables in the CFB Database.")
    selector_db_delete = input("Type y to Continue or type any other key to quit:")
    if selector_db_delete == 'y':
        conn = sqlite3.connect('blitzanalytics.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        remaining_tables = cursor.fetchall()
        if len(remaining_tables) == 0:
            print("All tables were successfully deleted. The database is empty.")
        else:
            print("Some tables still exist in the database:")
            for table in remaining_tables:
                print(table[0])
        conn.commit()
        cursor.execute("VACUUM;")
        print("The database was vacummed vacuumed to reduce file size")
        conn.close()

    else:
        exit()

def cfbd_api_request(cfbd_request_url):
    try:
        response = requests.get((cfbd_request_url), headers=headers_cfb)
    except requests.exceptions.RequestException as error:
        print("Error: ", error)
        return None
    response_json = json.loads(response.text)
    return response_json



def cfbd_season_calendar(arg_report_year, arg_report_week, arg_previous_years, arg_season_type):
    report_week = arg_report_week
    report_year = arg_report_year
    report_season_type = arg_season_type
    request_url = str(cfb_url + str('calendar?year=') + str(report_year))
    response_json = cfbd_api_request(request_url)


    team_records_request_url = str(cfb_url + str('records?year=' + str(report_year)))
    team_records_response_json = cfbd_api_request(team_records_request_url)
    if len(team_records_response_json) == 0:
        report_year = (current_year - 1)
        print("Reporting year selected contains no data. Generating a report using the most recent data instead")
    else:
        report_year = current_year

    request_url = str(cfb_url + str('calendar?year=') + str(report_year))
    response_json = cfbd_api_request(request_url)

    filtered_data = [game for game in response_json if (game['seasonType'] == 'postseason' and game['week'] == 1 or (game['seasonType'] == 'regular'))]

    for item in filtered_data:
        item['lastGameStart'] = datetime.strptime(item['lastGameStart'], '%Y-%m-%dT%H:%M:%S.%fZ')
    current_datetime = datetime.utcnow()
    closest_date = min(filtered_data, key=lambda x: abs(x['lastGameStart'] - current_datetime))
    closest_last_game_start = closest_date['lastGameStart']
    report_week = closest_date['week']
    report_year = closest_date['season']
    report_season_type = closest_date['seasonType']

    '''
    if not response_json:
        report_year = (current_year-1)
        request_url = str(cfb_url + str('calendar?year=') + str(report_year))
        response_json = cfbd_api_request(request_url)

        filtered_data = [game for game in response_json if (
                    game['seasonType'] == 'postseason' and game['week'] == 1 or (game['seasonType'] == 'regular'))]

        for item in filtered_data:
            item['lastGameStart'] = datetime.strptime(item['lastGameStart'], '%Y-%m-%dT%H:%M:%S.%fZ')
        current_datetime = datetime.utcnow()
        closest_date = min(filtered_data, key=lambda x: abs(x['lastGameStart'] - current_datetime))
        closest_last_game_start = closest_date['lastGameStart']
        report_week = closest_date['week']
        report_year = closest_date['season']
        report_season_type = closest_date['seasonType']
        print("Reporting year selected contains no data. Generating a report using the most recent data instead")

    elif response_json:
 
    filtered_data = [game for game in response_json if (
            game['seasonType'] == 'postseason' and game['week'] == 1 or (game['seasonType'] == 'regular'))]
    for item in filtered_data:
        item['lastGameStart'] = datetime.strptime(item['lastGameStart'], '%Y-%m-%dT%H:%M:%S.%fZ')
    current_datetime = datetime.utcnow()
    closest_date = min(filtered_data, key=lambda x: abs(x['lastGameStart'] - current_datetime))
    closest_last_game_start = closest_date['lastGameStart']
    report_week = closest_date['week']
    report_year = closest_date['season']
    report_season_type = closest_date['seasonType']
   '''
    if arg_previous_years:
        years_to_pull = list(range(int(report_year), int(report_year) - 5, -1))
    else:
        years_to_pull = [report_year]

    return report_year, report_week, years_to_pull, report_season_type