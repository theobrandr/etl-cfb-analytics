from playbook import pregame
from playbook import extract
from playbook import transform
from playbook import reporting
import argparse
from datetime import date
from datetime import datetime

parser = argparse.ArgumentParser(description='blitzanalytics Arguments')
parser.add_argument("-d", "--delete_all_tables", action='store_true',
                    help="Delete all DB tables if the DB is taking up too much space. Run the program with -p after to re-populate the DB.")
parser.add_argument("-s", "--skip_extract", action='store_true',
                    help="Skip the data extraction process if new data is not needed")
parser.add_argument("-y", "--report_year", type=str,
                    help="Generate a report from the defined year")
parser.add_argument("-w", "--report_week", type=str,
                    help="Generate a report from a defined week")
parser.add_argument("-p", "--season_type", type=str,
                    help="Indicate the season type, post or regular. The default option is regular.")
args = parser.parse_args()

if args.delete_all_tables:
   pregame.delete_all_tables()

if args.skip_extract:
    skip_extract = 1
else:
    skip_extract = 0

#user_arg_report_year = args.report_year
#user_arg_report_week = args.report_week
#user_arg_report_season_type = args.season_type


def extract_cfb_data(arg_skip_extract, status_existing_data, years, report_year):
    # Extract College Football Data
    def extract_cfbd(years):
        print("Extracting College Football Data")
        extract.cfbd_schedule(years)
        extract.cfbd_team_info()
        extract.cfbd_venue_info()
        extract.cfbd_coach_info()
        extract.cfbd_fbs_season_games(years)
        extract.cfbd_team_records(years)
        extract.cfbd_season_stats(years)
        extract.cfbd_rankings(years)
        extract.cfbd_epa(years)
        extract.cfbd_odds_per_game(years)
        extract.cfbd_stats_per_game(years)
        print("College Football Data Extraction Complete")

    if arg_skip_extract == 1:
        print("Skipping data extraction")

    else:
        if status_existing_data == True:
            years = report_year
            extract_cfbd(report_year)
        elif status_existing_data == False:
            years = default_years
            extract_cfbd(years)

def transform_cfb_data_from_cfbd():
    # Transform the College Football Data Datasets
    transform.season_stats()
    transform.games_and_stats()
    transform.games_and_aggregate_scores()
    transform.odds()
    transform.epa()
    transform.polls()
    transform.team_records()
    transform.stats_per_game()
    transform.team_info()
    transform.schedule()
    transform.combine_data_for_summary()
    transform.prep_data_for_reporting()

def reporting_cfb_data_from_cfbd():
    # Create Reports from Transformed College Football Data
    report_year, report_week, report_season_type = reporting.calculate_report_criteria(pregame.timestamp)
    reporting.pdf_matchup_reports_new(report_year, report_week, report_season_type)


if __name__ == '__main__':
    print("blitzanalytics: Your Playbook to Success for College Football Data ETL's and Reporting.")
    # Prepare and check the ETL is ready to run
    pregame.api_key_check()
    pregame.check_sqllite_db_status()
    default_years, default_report_year = pregame.calculate_default_data_years()
    pregame.filepath_check(default_report_year)
    status_existing_data = pregame.check_existing_sqlite_data(default_years)
    extract_cfb_data(skip_extract, status_existing_data, default_years, default_report_year)
    transform_cfb_data_from_cfbd()
    reporting_cfb_data_from_cfbd()
    exit()
