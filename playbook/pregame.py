import os
import dotenv
from datetime import date
from datetime import datetime
import sqlite3

#Load Enviroment Variables
dotenv.load_dotenv()
#Variables

def filepath_check():
    # Year and week variables for CFB API
    current_year = date.today().year
    # File path and file variables
    cwd = os.getcwd()
    file_env = dotenv.find_dotenv()
    file_path_cfb = cwd
    file_path_cfb_api = cwd + '/api_files/'
    file_path_cfb_reports = cwd + '/reports/'
    file_path_cfb_reports_current_year = file_path_cfb_reports + str(current_year) + '/'

    check_api_folder = os.path.exists(file_path_cfb_api)
    check_reports_folder = os.path.exists(file_path_cfb_reports)
    check_reports_folder_current_year= os.path.exists(file_path_cfb_reports_current_year)
    def filepath_api_check():
        if check_api_folder == True:
            return()
        elif check_api_folder == False:
            os.mkdir(file_path_cfb_api)
            return()
    def filepath_reports_check():
        if check_reports_folder == True:
            return()
        elif check_reports_folder == False:
            os.mkdir(file_path_cfb_reports)
            return()
    def filepath_reports_current_year_check():
        if check_reports_folder_current_year == True:
            return()
        elif check_reports_folder_current_year == False:
            os.mkdir(file_path_cfb_reports_current_year)
            return()

    def filepath_reports_current_year_weeks_check():
        weeks = list(range(1, 16))
        for week in weeks:
            path_reports_folder_current_year_week = file_path_cfb_reports_current_year + 'Week_' + str(week) + '/'
            check_reports_folder_current_year_week = os.path.exists(str(path_reports_folder_current_year_week))
            if check_reports_folder_current_year_week == True:
                continue
            elif check_reports_folder_current_year_week == False:
                os.mkdir(path_reports_folder_current_year_week)
                continue

    filepath_api_check()
    filepath_reports_check()
    filepath_reports_current_year_check()
    filepath_reports_current_year_weeks_check()
    return(print("Pregame Filpath Checks Complete"))

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
    connection = sqlite3.connect("blitzalytics.db")
    cursor = connection.cursor()
    sql_version_query = 'select sqlite_version();'
    cursor.execute(sql_version_query)
    result_sql_version_query = cursor.fetchall()
    print('SQLite Version is {}'.format(result_sql_version_query))
    cursor.close()
    connection.close()

def years_of_data_to_pull(arg_previous_years):
    current_year = date.today().year
    print(arg_previous_years)
    if arg_previous_years:
        years = list(range(current_year, current_year - 5, -1))
        return(years)
    else:
        years = [current_year]
        return(years)
def delete_all_tables():
    print("Warning, this will delete all the tables in the CFB Database.")
    selector_db_delete = input("Type y to Continue or type any other key to quit:")
    if selector_db_delete == 'y':
        conn = sqlite3.connect('blitzalytics.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
            # Commit the changes and close the connection
        conn.commit()
        conn.close()
    else:
        exit()
