from playbook import *

import argparse
parser = argparse.ArgumentParser(description='Blitzalytics Arguments')
parser.add_argument("-p", "--previous_years", dest='arg_previous_years', action='store_true',
                    help="Pull data for the last 5 years. By default only the currernt year will be pulled")
parser.add_argument("-r", "--report_week", dest='arg_report_week', action='store_true',
                    help="Specify a week for reporting. Default week is the current week")
parser.add_argument("-y", "--report_year", dest='arg_report_year', action='store_true',
                    help="Specify a year for reporting. Default year is the current year")
parser.add_argument("-d", "--delete_tables", dest='arg_delete_tables', action='store_true',
                    help="Delete all DB tables if the DB is taking up too much space. Run the program with -p after to re-populate the DB. ")
args = parser.parse_args()

print("Blitzalytics: Your Playbook to Success through College Football Data ETL's and Reporting.")

if __name__ == '__main__':
    #Prepare and check the ETL is ready to run
    pregame.filepath_check()
    pregame.api_key_check()
    pregame.check_sqllite_db()
    years = pregame.years_of_data_to_pull(args.arg_previous_years)
    print(years)

    #Extract College Football Data
    extract.cfbd_team_info()
    extract.cfbd_venue_info()
    extract.cfbd_coach_info()
    extract.cfbd_season_games(years)
    extract.cfbd_records()
    extract.cfbd_stats()
    extract.cfbd_rankings()
    extract.cfbd_epa()
    extract.cfbd_odds_per_game()
    extract.cfbd_stats_per_game()



    print("CFB Analytics ETL Complete")
    '''
    extract.check_env_previous_years_api_pull()
    extract.cfbd_api_previous_years()
    extract.json_to_df()
    #Transform the College Football Data Datasets                              
    transform.season_stats()
    transform.games_and_stats()
    transform.games_and_aggregate_scores()
    transform.odds()
    transform.epa()
    transform.polls()
    transform.team_records()
    transform.stats_per_game()
    transform.team_info()
    transform.week()
    transform.summary_data()
    transform.data_for_load()
    #Load the Transformed Data to Excel
    load.data_to_excel()
    #Create Reports from Transformed College Football Data
    reporting.current_week_matchups()
    '''