from playbook.nfl import load
from playbook.nfl import extract
import argparse
from datetime import date
from datetime import datetime

def nfl_espn():
    print("blitzanalytics: NFL Football Data ETL's and Reporting running.")
    extract.espn_nfl_teams()
    extract.espn_nfl_team_roster()
    extract.espn_nfl_scoreboard()
    #extract.espn_nfl_athletes()
    extract.espn_nfl_team_stats()
    #extract.espn_nfl_athlete_stats()
    extract.espn_nfl_team_roster_stats()


