from playbook.cfb import pregame
from playbook.cfb import cfb
from playbook.nfl import nfl
#from playbook.cfb import *
import argparse
from datetime import date
from datetime import datetime

parser = argparse.ArgumentParser(description='blitzanalytics Arguments')
parser.add_argument("-cfb", "--college_football", action='store_true',
                    help="Pull Data for College Football")
parser.add_argument("-nfl", "--nfl_football", action='store_true',
                    help="Pull Data for NFL Football")
parser.add_argument("-p", "--previous_years", action='store_true',
                    help="Pull data for the last 5 years. By default only the current year will be pulled")
parser.add_argument("-r", "--report_week", type=int, default=None,
                    help="Specify a week for reporting. Default week is the current week")
parser.add_argument("-y", "--report_year", type=int, default=None,
                    help="Specify a year for reporting. Default year is the current year")
parser.add_argument("-t", "--season_type", action='store_true',
                    help="regular for Regular Season or postseason for Postseason")
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

if args.delete_tables:
   pregame.delete_all_tables()

if args.skip_extract:
   skip_extract = 1
else:
    skip_extract = 0

if __name__ == '__main__':
    print("blitzanalytics: Your Playbook to Success through Sports Data ETL's and Reporting.")
    # Prepare and check the ETL is ready to run

    if args.college_football is True:
        cfb.pregame.api_key_check()
        cfb.pregame.check_sqllite_db()
        report_year, report_week, years_to_pull, report_season_type = pregame.cfbd_season_calendar(args.report_year, args.report_week, args.previous_years, args.season_type)
        cfb.pregame.filepath_check(report_year)
        cfb.cfb_cfbd(years_to_pull, skip_extract, report_week, report_year, report_season_type)

    if args.nfl_football is True:
        nfl.nfl_espn()

    exit()
