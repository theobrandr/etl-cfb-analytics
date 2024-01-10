from playbook.nfl import load
from playbook.nfl import extract
import argparse
from datetime import date
from datetime import datetime

def nfl_espn():
    print("blitzanalytics: Your Playbook to Success through NFL Football Data ETL's and Reporting.")
    extract.nfl_teams()
    extract.nfl_scoreboard()
    extract.nfl_athletes()
    extract.nfl_team_stats()