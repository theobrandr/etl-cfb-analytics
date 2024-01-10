from playbook.cfb import pregame
from playbook.cfb import extract
from playbook.cfb import transform
from playbook.cfb import reporting
from datetime import date
from datetime import datetime

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
    #reporting_week = transform.reporting_week(report_week)
    #reporting_year = transform.reporting_year(report_year)
    transform.combine_data_for_summary(report_year)
    transform.prep_data_for_reporting()

    # Create Reports from Transformed College Football Data
    reporting.matchups(report_year, report_week, report_season_type)

