import os
import io
from playbook import load
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
#from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt



def matchup_points_by_season_bar(df):
    fig = px.bar(
        df,
        x="week",
        y="points",
        color="team",
        barmode="group",
        facet_col="season",
    )
    fig.update_layout(
        height=600,
        width=1600,
        title_text="Matchup Points by Week for Each Season"
    )

    for facet in fig.select_xaxes():
        facet.update(
            tickmode='linear',
            tick0=1,
            dtick=1
        )
    #fig.show()
    return fig

def matchup_spread_result_by_season_bar(df):
    df['spread_counts'] = 1
    fig = px.bar(
        df,
        x="result_of_the_spread",
        y='spread_counts',
        color="team",
        barmode="group",
        facet_col="season",
    )
    fig.update_layout(
        height=600,
        width=1600,
        title_text="Result of the Spread Totals for Each Season"
    )

    for facet in fig.select_xaxes():
        facet.update(
            tickmode='linear',
            tick0=1,
            dtick=1
        )
    #fig.show()
    return fig

def matchup_stats_by_report_year_line(df_in, x_value, y_value, home_team, away_team, reporting_year, team_colors):
    df = df_in.loc[((df_in['team'] == home_team) | (df_in['team'] == away_team)) & (df_in['season'] == reporting_year)]
    columns = df.columns
    values = [df[col] for col in columns]
    fig = px.line(
        df,
        x=x_value,
        y=y_value,
        markers=True,
        color='team',
        height=400,
        width=800,
        color_discrete_map=team_colors
        )
    unique_tick = sorted(df[x_value].unique())
    fig.update_xaxes(tickmode='array', tickvals=unique_tick, tickangle=0, dtick=1)
    return fig


def matchup_stats_by_report_year_box(df_in, x_value, y_value, home_team, away_team, team_colors):
    df = df_in.loc[((df_in['team'] == home_team) | (df_in['team'] == away_team))]
    columns = df.columns
    values = [df[col] for col in columns]
    fig = px.box(
        df,
        x=x_value,
        y=y_value,
        color='team',
        height=400,
        width=800,
        color_discrete_map=team_colors
    )
    unique_tick = sorted(df[x_value].unique())
    fig.update_xaxes(tickmode='array', tickvals=unique_tick, tickangle=0, dtick=1)
    #fig.show()
    return fig

def matchup_stats_table(cfb_season_stats_by_season, home_team, away_team, stat_type):
    if stat_type == 'offense':
        stat_type_columns = ['team', 'season', 'offense_possessionTime', 'offense_totalYards',
                           'offense_netPassingYards', 'offense_passAttempts', 'offense_passCompletions',
                           'offense_passingTDs', 'offense_rushingYards', 'offense_rushingAttempts',
                           'offense_rushingTDs', 'offense_turnovers', 'offense_fumblesLost',
                           'offense_passesIntercepted']
    elif stat_type == 'offense_downs':
        stat_type_columns = ['team', 'season', 'offense_firstDowns', 'offense_thirdDowns', 'offense_thirdDownConversions',
                    'offense_fourthDowns', 'offense_fourthDownConversions', 'offense_turnovers',
                    'offense_fumblesLost', 'offense_passesIntercepted']
    elif stat_type == 'defense':
        stat_type_columns = ['team', 'season', 'defense_tacklesForLoss', 'defense_sacks', 'defense_fumblesRecovered',
                    'defense_interceptions', 'defense_interceptionTDs']
    elif stat_type == 'special_teams':
        stat_type_columns = ['team', 'season', 'specialteams_kickReturns', 'specialteams_kickReturnYards', 'specialteams_kickReturnTDs',
                'specialteams_puntReturnYards', 'specialteams_puntReturns', 'specialteams_puntReturnTDs']

    df = cfb_season_stats_by_season.loc[(cfb_season_stats_by_season['team'] == home_team) |(cfb_season_stats_by_season['team'] == away_team)]

    fig = go.Figure(go.Table(
        header=dict(
            values=list(stat_type_columns),
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df[col].tolist() for col in list(stat_type_columns)],
            align="left"
        )
    )
    )
    #fig.show()
    return fig


