from nfl import pregame
from nfl import load
from nfl import extract
from nfl import transform
import argparse
from datetime import date
from datetime import datetime

parser = argparse.ArgumentParser(description='Accretion Data NFL ETL Arguments')
parser.add_argument("-s", "--skip_extract", action='store_true',
                    help="Skip the data extraction process if new data is not needed")

args = parser.parse_args()

if args.skip_extract:
   skip_extract = 1
else:
    skip_extract = 0

def extract_espn_data():
    extract.espn_nfl_teams()
    extract.espn_nfl_team_roster()
    extract.espn_nfl_scoreboard()
    extract.espn_nfl_athletes()
    extract.espn_nfl_team_stats()
    extract.espn_nfl_athlete_stats()
    extract.espn_nfl_team_roster_stats()

def transform_espn_data():
    transform.espn_team_stats_oponent()

if __name__ == '__main__':
    # Prepare and check the ETL is ready to run

    pregame.check_sqllite_db_status()

    if skip_extract == 1:
        transform_espn_data()

    elif skip_extract == 0:
        extract_espn_data()
        transform_espn_data()

    exit()