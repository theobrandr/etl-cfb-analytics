import sqlite3
import pandas as pd
import playbook.nfl.load
import playbook.nfl.pregame
import plotly.express as px
import plotly.graph_objects as go

def espn_figure_teams_average_score_bar():
    df_espn_nfl_teams_stats_sql = playbook.nfl.load.sqlite_query_table('nfl_extract_team_stats')
    df_espn_nfl_teams_stats_pointspergame = df_espn_nfl_teams_stats_sql.loc[
        (df_espn_nfl_teams_stats_sql['name'] == 'totalPointsPerGame') &
        (df_espn_nfl_teams_stats_sql['category_name_results.stats.categories.name'] == 'scoring')
        ]
    fig = px.bar(df_espn_nfl_teams_stats_pointspergame, x="team.name", y="displayValue")
    fig.update_yaxes(categoryorder='category ascending')
    fig.show()
    print()

def espn_figure_teams_cat_scores_wide_table():
    df_espn_nfl_teams_stats_sql = playbook.nfl.load.sqlite_query_table('nfl_extract_team_stats')
    df_spn_nfl_teams_cat_scores = df_espn_nfl_teams_stats_sql.loc[
        (df_espn_nfl_teams_stats_sql['team.id'] == '22') &
        (df_espn_nfl_teams_stats_sql['category_name_results.stats.categories.name'] == 'scoring')
        ]
    df = df_spn_nfl_teams_cat_scores[['team.name', 'displayName', 'displayValue', 'perGameDisplayValue']]
    df.rename(columns={"team.name": "team_name"}, inplace=True)
    fig = go.Figure(data=[go.Table(
        header=dict(values=df['displayName'],
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=df['displayValue'],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.show()

def espn_figure_teams_cat_scores_long_table():
    df_espn_nfl_teams_stats_sql = playbook.nfl.load.sqlite_query_table('nfl_extract_team_stats')
    df_spn_nfl_teams_cat_scores = df_espn_nfl_teams_stats_sql.loc[
        (df_espn_nfl_teams_stats_sql['team.id'] == '22') &
        (df_espn_nfl_teams_stats_sql['category_name_results.stats.categories.name'] == 'scoring')
        ]
    df = df_spn_nfl_teams_cat_scores[['team.name','displayName','displayValue', 'perGameDisplayValue']]
    df.rename(columns={"team.name": "team_name"}, inplace=True)
    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=[df.team_name, df.displayName, df.displayValue, df.perGameDisplayValue],
                   fill_color='lavender',
                   align='left'))
    ])
    fig.show()

def espn_export_to_csv():
    df_espn_nfl_teams_stats_sql = playbook.nfl.load.sqlite_query_table('nfl_extract_team_stats')
    df_espn_nfl_teams_stats_sql.drop(['results.opponent', 'team.logo'], axis=1)
    df_espn_nfl_teams_stats_sql_loc = df_espn_nfl_teams_stats_sql.loc[df_espn_nfl_teams_stats_sql['team.name'] == 'Chiefs']
    df_espn_nfl_teams_stats_sql_loc.to_csv("nfl_extract_team_stats.csv")