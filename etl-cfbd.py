from cfb.cfbd import pregame
from cfb.cfbd import extract
from cfb.cfbd import transform
import argparse


parser = argparse.ArgumentParser(description='blitzanalytics Arguments')
parser.add_argument("-d", "--delete_all_tables", action='store_true',
                    help="Delete all DB tables if the DB is taking up too much space. Run the program with -p after to re-populate the DB.")
parser.add_argument("-s", "--skip_extract", action='store_true',
                    help="Skip the data extraction process if new data is not needed")
parser.add_argument("-t", "--skip_transform", action='store_true',
                    help="Skip the data transform process if transforming data is not needed")

args = parser.parse_args()

if args.delete_all_tables:
   pregame.delete_all_tables()

if args.skip_extract:
    skip_extract = 1
else:
    skip_extract = 0

if args.skip_transform:
    skip_transform = 1
else:
    skip_transform = 0

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
        extract.cfbd_player_team_roster(years)
        extract.cfbd_player_stats_per_season(years)
        extract.cfbd_player_usage_per_season(years)
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

def transform_cfb_data_from_cfbd(arg_skip_transform):
    def transform_cfbd():
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
        transform.schedule()
        transform.player_stats_and_team_roster()
        transform.prep_data_for_reporting()

    if arg_skip_transform == 1:
        print("Skipping data transform")

    else:
        transform_cfbd()


if __name__ == '__main__':
    print("Accretion Data: College Football Data ETL's and Reporting.")
    # Prepare and check the ETL is ready to run
    pregame.api_key_check()
    pregame.db_folder_check()
    pregame.check_sqllite_db_status()
    default_years, default_report_year = pregame.calculate_default_data_years()
    status_existing_data = pregame.check_existing_sqlite_data(default_years)
    extract_cfb_data(skip_extract, status_existing_data, default_years, default_report_year)
    transform_cfb_data_from_cfbd(skip_transform)
    #reporting.matchup_report()
    exit()
