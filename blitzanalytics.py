from playbook import pregame
from playbook import extract
from playbook import transform
from playbook import reporting
import argparse
from datetime import date
from datetime import datetime

parser = argparse.ArgumentParser(description='blitzanalytics Arguments')
parser.add_argument("-p", "--previous_years", action='store_true',
                    help="Pull data for the last 5 years. By default only the current year will be pulled")
parser.add_argument("-r", "--report_week", type=int, default=None,
                    help="Specify a week for reporting. Default week is the current week")
parser.add_argument("-y", "--report_year", type=int, default=None,
                    help="Specify a year for reporting. Default year is the current year")
parser.add_argument("-t", "--season_type", action='store_const', const='postseason',
                    help="Specifying this flag will set the reporting to postseason.")
parser.add_argument("-d", "--delete_tables", action='store_true',
                    help="Delete all DB tables if the DB is taking up too much space. Run the program with -p after to re-populate the DB.")
parser.add_argument("-s", "--skip_extract", action='store_true',
                    help="Skip the data extraction process if new data is not needed")

args = parser.parse_args()

if args.previous_years:
    print("Pulling data for previous years and current year")

if args.report_week is not None:
    if args.report_week > 1 < 16:
        print(f"Reporting week set to {args.report_week}")
    else:
        print("Not a valid reporting week. Please use a week number between 1 and 15")
        exit()

if args.report_year is not None:
    current_year = date.today().year
    possible_report_years = list(range(current_year, current_year - 5, -1))
    if args.report_year in possible_report_years:
        print(f"Reporting year set to {args.report_year}")
        report_year = args.report_year
    else:
        print(f"Not a valid reporting year. Please use a year within the last 5 years. {possible_report_years}")

if args.report_year is None:
    args.report_year = date.today().year

if args.season_type:
    args.season_type = args.season_type
else:
    args.season_type = 'regular'

if args.delete_tables:
   pregame.delete_all_tables()

if args.skip_extract:
   skip_extract = 1
else:
    skip_extract = 0

def cfb_cfbd(arg_years, arg_skip_extract, report_week, report_year, report_season_type):
    # Extract College Football Data
    years = arg_years
    if arg_skip_extract == 1:
        print("Skipping data extraction")
    else:
        print("Extracting College Football Data")
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

    # Transform the College Football Data Datasets
    transform.season_stats(years)
    transform.games_and_stats()
    transform.games_and_aggregate_scores()
    transform.odds()
    transform.epa()
    transform.polls()
    transform.team_records()
    transform.stats_per_game()
    transform.team_info()
    transform.combine_data_for_summary(report_year)
    transform.prep_data_for_reporting()

    # Create Reports from Transformed College Football Data
    reporting.matchups(report_year, report_week, report_season_type)


if __name__ == '__main__':
    print("blitzanalytics: Your Playbook to Success for College Football Data ETL's and Reporting.")
    # Prepare and check the ETL is ready to run
    pregame.api_key_check()
    pregame.check_sqllite_db()
    report_year, report_week, years_to_pull, report_season_type = pregame.cfbd_season_calendar(args.report_year, args.report_week, args.previous_years, args.season_type)
    pregame.filepath_check(report_year)
    cfb_cfbd(years_to_pull, skip_extract, report_week, report_year, report_season_type)

    exit()
