from playbook import *
import argparse

parser = argparse.ArgumentParser(description='Blitzalytics Arguments')
parser.add_argument("-p", "--previous_years", action='store_true',
                    help="Pull data for the last 5 years. By default only the current year will be pulled")
parser.add_argument("-r", "--report_week", type=int, default=None,
                    help="Specify a week for reporting. Default week is the current week")
parser.add_argument("-y", "--report_year", type=int, default=None,
                    help="Specify a year for reporting. Default year is the current year")
parser.add_argument("-d", "--delete_tables", action='store_true',
                    help="Delete all DB tables if the DB is taking up too much space. Run the program with -p after to re-populate the DB.")
args = parser.parse_args()



if __name__ == '__main__':
    print("Blitzalytics: Your Playbook to Success through College Football Data ETL's and Reporting.")
    #Prepare and check the ETL is ready to run
    pregame.filepath_check()
    pregame.api_key_check()
    pregame.check_sqllite_db()
    pregame.argument_check(args)
    years = pregame.years_of_data_to_pull(args.previous_years)

    #Extract College Football Data
    print("Extracting College Football Data")
    #extract.cfbd_team_info()
    #extract.cfbd_venue_info()
    #extract.cfbd_coach_info()
    #extract.cfbd_fbs_season_games(years)
    #extract.cfbd_records(years)
    extract.cfbd_season_stats(years)
    #extract.cfbd_rankings(years)
    #extract.cfbd_epa(years)
    #extract.cfbd_odds_per_game(years)
    #extract.cfbd_stats_per_game(years)
    print("College Football Data Extraction Complete")

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
