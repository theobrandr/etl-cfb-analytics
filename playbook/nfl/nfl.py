from playbook.nfl import load
from playbook.nfl import extract
from playbook.nfl import reporting
from playbook.nfl import transform
import argparse
from datetime import date
from datetime import datetime

def nfl_espn():
    print("blitzanalytics: NFL Football Data ETL's and Reporting running.")
    #extract.espn_nfl_teams()
    #extract.espn_nfl_team_roster()
    #extract.espn_nfl_scoreboard()
    #extract.espn_nfl_athletes()
    #extract.espn_nfl_team_stats()
    #extract.espn_nfl_athlete_stats()
    #extract.espn_nfl_team_roster_stats()
    #transform.espn_team_stats_oponent()
    #reporting.espn_figure_teams_average_score_bar()
    #reporting.espn_figure_teams_cat_scores_wide_table()
    #reporting.espn_figure_teams_cat_scores_long_table()

    reporting.espn_export_to_csv()

