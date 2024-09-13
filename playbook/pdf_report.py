import os
import io
from playbook import load
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.io as pio
import matplotlib.backends.backend_pdf
import matplotlib.pyplot as plt

cwd = os.getcwd()
file_path_cfb = cwd


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

def page_1(matchup_data, cfb_summary, home_team, away_team, report_title):
    matchup_data_columns = matchup_data[
        ['team', 'conference', 'home_vs_away', 'AP Top 25', 'season', 'season_type', 'week']]

    season_summary_columns = ['season', 'team', 'total.wins', 'total.losses', 'home_points_season_mean',
                              'away_points_season_mean', 'epa_per_game_offense_overall_avg_per_season',
                              'epa_per_game_offense_overall_avg_per_season']
    cfb_summary_home = cfb_summary.loc[(cfb_summary['team'] == home_team)]
    cfb_summary_away = cfb_summary.loc[(cfb_summary['team'] == away_team)]
    cfb_summary_home_values = [cfb_summary_home[col] for col in season_summary_columns]
    cfb_summary_away_values = [cfb_summary_away[col] for col in season_summary_columns]

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}],
               [{"type": "table"}],
               [{"type": "table"}]
               ]
    )
    fig.add_trace(go.Table(
        header=dict(
            values=[col for col in matchup_data_columns.columns],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[matchup_data[col].tolist() for col in matchup_data_columns.columns],
            align="left"
        )
    ), row=1, col=1)
    fig.add_trace(go.Table(
        header=dict(
            values=season_summary_columns,
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=cfb_summary_home_values,
            align="left"
        )
    ), row=2, col=1)
    fig.add_trace(go.Table(
        header=dict(
            values=season_summary_columns,
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=cfb_summary_away_values,
            align="left"
        )
    ), row=3, col=1)
    fig.update_layout(
        height=800,
        width=1200,
        showlegend=False,
        title_text=report_title
    )
    #fig.show()
    return fig

def page_2(reporting_year, df_matchup_home_away_all_data, subplot_title, team_colors):
    seasons = list(range(int(reporting_year), int(reporting_year) - 5, -1))
    subplot_col_number = len(seasons)

    figures_points = []
    figures_spread = []

    for season in seasons:
        df = df_matchup_home_away_all_data.loc[
            (df_matchup_home_away_all_data['season'].astype(str) == str(season)) &
            (df_matchup_home_away_all_data['season_type'].astype(str) == "regular")
            ]
        fig = px.bar(
            df,
            x="week",
            y="points",
            barmode="group",
            color='team',
            color_discrete_map=team_colors,
            facet_col = "season_type"
        )
        fig.update_xaxes(type='category')  # Ensure x-axis shows all values
        #fig.show()
        figures_points.append(fig)

    for season in seasons:
        df = df_matchup_home_away_all_data.loc[
            (df_matchup_home_away_all_data['season'].astype(str) == str(season)) &
            (df_matchup_home_away_all_data['season_type'].astype(str) == "regular")
            ]
        df['spread_counts'] = 1
        fig = px.histogram(
            df,
            x="result_of_the_spread",
            y="spread_counts",
            barmode="group",
            color='team',
            color_discrete_map=team_colors
        )
        fig.update_xaxes(type='category')
        figures_spread.append(fig)

    fig = make_subplots(
        rows=2,
        cols=subplot_col_number,
        subplot_titles=[str(season) for season in seasons] * 2,
        shared_yaxes=True
    )

    # Track which teams have been added to the legend
    added_teams = set()

    for i, figure in enumerate(figures_points):
        for trace in figure.data:
            if trace.name in added_teams:
                trace.showlegend = False
            else:
                trace.showlegend = True
                added_teams.add(trace.name)
            fig.add_trace(trace, row=1, col=i + 1)

    for i, figure in enumerate(figures_spread):
        for trace in figure.data:
            if trace.name in added_teams:
                trace.showlegend = False
            else:
                trace.showlegend = True
                added_teams.add(trace.name)
            fig.add_trace(trace, row=2, col=i + 1)

    fig.update_layout(
        height=1200,
        width=1200,
        title_text=subplot_title,
        showlegend=True,
        xaxis=dict(tickmode='linear'),
        # yaxis=dict(tickmode='linear'),
        margin=dict(t=100, b=100, l=50, r=50)  # Adjust margins to prevent clipping

    )

    for col in range(1, subplot_col_number + 1):
        fig.update_xaxes(
            tickmode='linear',
            tickangle=45,
            row=1,
            col=col
        )
        fig.update_yaxes(
            showticklabels=True,
            showgrid=True,
            row=1,
            col=col
        )
        fig.update_xaxes(
            tickmode='linear',
            tickangle=45,
            row=2,
            col=col
        )
        fig.update_yaxes(
            showticklabels=True,
            showgrid=True,
            row=2,
            col=col
        )
    #fig.show()
    return (fig)


def page_3(reporting_year, df_matchup_home_away_all_data, subplot_title, home_team, away_team, team_colors):
    def matchup_stats_by_report_year_line(df_in, x_value, y_value, home_team, away_team, reporting_year, team_colors):
        df = df_in.loc[((df_in['team'] == home_team) | (df_in['team'] == away_team)) & (
                    df_in['season'].astype(str) == reporting_year)]
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

    fig_offense_passing_success_report_year_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'offense.passingPlays.successRate', home_team, away_team,
        reporting_year, team_colors)
    fig_defense_passing_success_report_year_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'defense.passingPlays.successRate', home_team, away_team,
        reporting_year, team_colors)

    fig_offense_rushing_success_report_year_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'offense.rushingPlays.successRate', home_team, away_team,
        reporting_year, team_colors)

    fig_defense_rushing_success_report_year_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'defense.rushingPlays.successRate', home_team, away_team,
        reporting_year, team_colors)

    fig_offense_successRate_report_year_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'offense.successRate', home_team, away_team, reporting_year,
        team_colors)
    fig_defense_successRate_report_year_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'defense.successRate', home_team, away_team, reporting_year,
        team_colors)

    subplot_rows = 3
    subplot_cols = 2
    fig = make_subplots(
        rows=subplot_rows,
        cols=subplot_cols,
        subplot_titles=[
            'Offense Passing Success Rate',
            'Defense Passing Success Rate',
            'Offense Rushing Success Rate',
            'Defense Rushing Success Rate',
            'Offense Success Rate',
            'Defense Success Rate'
        ],
        shared_yaxes=False
    )

    # Track which teams have been added to the legend
    added_teams = set()

    for trace in fig_offense_passing_success_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=1, col=1)

    for trace in fig_defense_passing_success_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=1, col=2)

    for trace in fig_offense_rushing_success_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=2, col=1)

    for trace in fig_defense_rushing_success_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=2, col=2)

    for trace in fig_offense_successRate_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=3, col=1)

    for trace in fig_defense_successRate_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=3, col=2)

    # Update layout
    fig.update_layout(
        height=1200,
        width=1200,
        title_text=subplot_title,
        showlegend=True
    )
    for row in range(1, subplot_rows + 1):
        for col in range(1, subplot_cols + 1):
            fig.update_xaxes(
                tickmode='linear',
                tickangle=45,
                row=row,
                col=col
            )
            fig.update_yaxes(
                showticklabels=True,
                showgrid=True,
                row=row,
                col=col
            )
    #fig.show()
    return fig


def page_4(reporting_year, df_matchup_home_away_all_data, subplot_title, home_team, away_team, team_colors):
    def matchup_stats_by_report_year_line(df_in, x_value, y_value, home_team, away_team, reporting_year, team_colors):
        df = df_in.loc[((df_in['team'] == home_team) | (df_in['team'] == away_team)) & (
                df_in['season'].astype(str) == reporting_year)]
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
        # fig.show()
        return fig

    fig_offense_netPassingYards_report_year_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'offense.successRate', home_team, away_team, reporting_year,
        team_colors)
    fig_offense_rushingYards_report_year_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'defense.successRate', home_team, away_team, reporting_year,
        team_colors)
    fig_epa_offense_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'offense.ppa', home_team, away_team, reporting_year, team_colors)
    fig_epa_defense_line = matchup_stats_by_report_year_line(
        df_matchup_home_away_all_data, 'week', 'defense.ppa', home_team, away_team, reporting_year, team_colors)
    fig_epa_per_game_offense_by_season_box = matchup_stats_by_report_year_box(
        df_matchup_home_away_all_data, 'season', 'epa_per_game_offense.overall', home_team, away_team,
        team_colors)
    fig_epa_per_game_defense_by_season_box = matchup_stats_by_report_year_box(
        df_matchup_home_away_all_data, 'season', 'epa_per_game_defense.overall', home_team, away_team,
        team_colors)

    subplot_rows = 3
    subplot_cols = 2

    fig = make_subplots(
        rows=subplot_rows,
        cols=subplot_cols,
        subplot_titles=[
            'Offense Net Passing Yards',
            'Offense Rushing Yards',
            'Offensive EPA',
            'Defense EPA',
            'Offense EPA Per Game by Season',
            'Defense EPA Per Game by Season'
        ],
        shared_yaxes=False,
    )
    # Track which teams have been added to the legend
    added_teams = set()

    for trace in fig_offense_netPassingYards_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=1, col=1)

    for trace in fig_offense_rushingYards_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=1, col=2)

    for trace in fig_epa_offense_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=2, col=1)

    for trace in fig_epa_defense_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=2, col=2)

    for trace in fig_epa_per_game_offense_by_season_box.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=3, col=1)

    for trace in fig_epa_per_game_defense_by_season_box.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=3, col=2)

    fig.update_layout(
        height=1200,
        width=1200,
        title_text=subplot_title,
        showlegend=True,
        xaxis=dict(tickmode='linear'),
    )

    for row in range(1, subplot_rows + 1):
        for col in range(1, subplot_cols + 1):
            fig.update_xaxes(
                tickmode='linear',
                tickangle=45,
                row=row,
                col=col
            )
            fig.update_yaxes(
                showticklabels=True,
                showgrid=True,
                row=row,
                col=col
            )
    #fig.show()
    return fig


def page_5(reporting_year, df_matchup_home_away_all_data, subplot_title, home_team, away_team, team_colors):
    def matchup_stats_by_multi_year_line(df_in, x_value, y_value, home_team, away_team, team_colors):
        df = df_in.loc[((df_in['team'] == home_team) | (df_in['team'] == away_team))]
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

    fig_offense_zscore_final_report_year_line = matchup_stats_by_multi_year_line(
        df_matchup_home_away_all_data, 'season', 'offense_zscore_final', home_team, away_team,
        team_colors)
    fig_defense_zscore_final_report_year_line = matchup_stats_by_multi_year_line(
        df_matchup_home_away_all_data, 'season', 'defense_zscore_final', home_team, away_team,
        team_colors)
    fig_specialteams_zscore_final_report_year_line = matchup_stats_by_multi_year_line(
        df_matchup_home_away_all_data, 'season', 'specialteams_zscore_final', home_team, away_team, team_colors)
    fig_total_zscore_report_year_line = matchup_stats_by_multi_year_line(
        df_matchup_home_away_all_data, 'season', 'total_zscore', home_team, away_team, team_colors)

    subplot_rows = 2
    subplot_cols = 2

    fig = make_subplots(
        rows=subplot_rows,
        cols=subplot_cols,
        subplot_titles=[
            'Offense Zscore',
            'Defense Zscore',
            'Special Teams Zscore',
            'Total Zscore',
        ],
        shared_yaxes=False,
    )

    # Track which teams have been added to the legend
    added_teams = set()

    for trace in fig_offense_zscore_final_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=1, col=1)

    for trace in fig_defense_zscore_final_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=1, col=2)

    for trace in fig_specialteams_zscore_final_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=2, col=1)

    for trace in fig_total_zscore_report_year_line.data:
        if trace.name in added_teams:
            trace.showlegend = False
        else:
            trace.showlegend = True
            added_teams.add(trace.name)
        fig.add_trace(trace, row=2, col=2)

    fig.update_layout(
        height=1200,
        width=1200,
        title_text=subplot_title,
        showlegend=True
    )

    for row in range(1, subplot_rows + 1):
        for col in range(1, subplot_cols + 1):
            fig.update_xaxes(
                tickmode='linear',
                tickangle=45,
                row=row,
                col=col
            )
            fig.update_yaxes(
                showticklabels=True,
                showgrid=True,
                row=row,
                col=col
            )

    #fig.show()
    return fig


def page_6(cfb_season_stats_by_season, home_team, away_team, subplot_title):
    fig_matchup_stats_offense_table = matchup_stats_table(cfb_season_stats_by_season, home_team,
                                                                away_team, 'offense')
    fig_matchup_stats_offense_downs_table = matchup_stats_table(cfb_season_stats_by_season, home_team,
                                                                      away_team, 'offense_downs')

    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=[
            'Offense Stats',
            'Offense Downs Stats',
        ],
        specs=[[{"type": "table"}],
               [{"type": "table"}],
               ]
    )
    for trace in fig_matchup_stats_offense_table.data:
        fig.add_trace(trace, row=1, col=1)
    for trace in fig_matchup_stats_offense_downs_table.data:
        fig.add_trace(trace, row=2, col=1)


    fig.update_layout(
        height=1200,  # Adjust height as needed
        width=1200,  # Adjust width as needed
        title_text=subplot_title,
    )
    # fig.show()
    return fig

def page_7(cfb_season_stats_by_season, home_team, away_team, subplot_title):
    fig_matchup_stats_defense_table = matchup_stats_table(cfb_season_stats_by_season, home_team,
                                                                away_team, 'defense')
    fig_matchup_stats_special_teams_table = matchup_stats_table(cfb_season_stats_by_season, home_team,
                                                                      away_team, 'special_teams')

    fig = make_subplots(
        rows=2,
        cols=1,
        subplot_titles=[
            'Defense Stats',
            'Special Teams Stats',
        ],
        specs=[[{"type": "table"}],
               [{"type": "table"}],
               ]
    )
    for trace in fig_matchup_stats_defense_table.data:
        fig.add_trace(trace, row=1, col=1)
    for trace in fig_matchup_stats_special_teams_table.data:
        fig.add_trace(trace, row=2, col=1)

    fig.update_layout(
        height=1200,  # Adjust height as needed
        width=1200,  # Adjust width as needed
        title_text=subplot_title,
    )
    # fig.show()
    return fig

def page_8(player_stat_data_report_year, home_team, away_team, report_year, subplot_title):
    player_data = player_stat_data_report_year.loc[((player_stat_data_report_year['team_roster'] == home_team) | \
                                                    (player_stat_data_report_year['team_roster'] == away_team)) & \
                                                   (player_stat_data_report_year['season_roster'].astype(str) == report_year)]
    player_data.sort_values(by=['team_roster', 'season_roster', 'position', 'year'],
                            ascending=[True, True, True, False], inplace=True)
    player_data_col = ['team_roster', 'season_roster', 'playerId', 'player', 'position', 'year', 'team_stat',
                       'season_stat']

    player_data_qb = player_data.loc[(player_data['position'] == "QB")]
    player_data_qb_stat_col = player_data.filter(regex='passing|rushing|fumbles').columns.tolist()
    player_data_qb_report_col = player_data_col + player_data_qb_stat_col
    player_data_qb_stat = player_data_qb[player_data_qb_report_col]
    player_data_qb_stat_home = player_data_qb_stat.loc[player_data_qb_stat['team_roster'] == home_team]
    player_data_qb_stat_away = player_data_qb_stat.loc[player_data_qb_stat['team_roster'] == away_team]

    def wrap_text_on_hyphen(text):
        return '<br>'.join(text.split('_'))

    wrapped_qb_headers = [wrap_text_on_hyphen(col) for col in player_data_qb_report_col]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}],
               [{"type": "table"}]]
    )

    # Check if the home team table is empty
    if not player_data_qb_stat_home.empty:
        fig.add_trace(go.Table(
            header=dict(
                values=wrapped_qb_headers,
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=player_data_qb_stat_home.transpose().values.tolist(),
                align="left"
            )
        ), row=1, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["No Data Available"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[["No Data Available"]],
                align="left"
            )
        ), row=1, col=1)

    # Check if the away team table is empty
    if not player_data_qb_stat_away.empty:
        fig.add_trace(go.Table(
            header=dict(
                values=wrapped_qb_headers,
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=player_data_qb_stat_away.transpose().values.tolist(),
                align="left"
            )
        ), row=2, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["No Data Available"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[["No Data Available"]],
                align="left"
            )
        ), row=2, col=1)

    fig.update_layout(
        height=1200,
        width=1200,
        showlegend=False,
        title_text=subplot_title
    )
    # fig.show()
    return fig


def page_9(player_stat_data_report_year, home_team, away_team, report_year, subplot_title):
    player_data = player_stat_data_report_year.loc[((player_stat_data_report_year['team_roster'] == home_team) | (
                player_stat_data_report_year['team_roster'] == away_team)) & (player_stat_data_report_year[
                                                                                  'season_roster'] == report_year)]
    player_data.sort_values(by=['team_roster', 'season_roster', 'position', 'year'],
                            ascending=[True, True, True, False], inplace=True)
    player_data_col = ['team_roster', 'season_roster', 'playerId', 'player', 'position', 'year', 'team_stat',
                       'season_stat']

    player_data_wr = player_data.loc[(player_data['position'] == "WR")]
    player_data_wr_stat_col = player_data.filter(regex='recieving|rushing|fumbles').columns.tolist()
    player_data_wr_report_col = player_data_col + player_data_wr_stat_col
    player_data_wr_stat = player_data_wr[player_data_wr_report_col]
    player_data_wr_stat_home = player_data_wr_stat.loc[player_data_wr_stat['team_roster'] == home_team]
    player_data_wr_stat_away = player_data_wr_stat.loc[player_data_wr_stat['team_roster'] == away_team]

    def wrap_text_on_hyphen(text):
        return '<br>'.join(text.split('_'))

    wrapped_wr_headers = [wrap_text_on_hyphen(col) for col in player_data_wr_report_col]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}],
               [{"type": "table"}]]
    )

    # Check if the home team table is empty
    if not player_data_wr_stat_home.empty:
        fig.add_trace(go.Table(
            header=dict(
                values=wrapped_wr_headers,
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=player_data_wr_stat_home.transpose().values.tolist(),
                align="left"
            )
        ), row=1, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["No Data Available"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[["No Data Available"]],
                align="left"
            )
        ), row=1, col=1)

    # Check if the away team table is empty
    if not player_data_wr_stat_away.empty:
        fig.add_trace(go.Table(
            header=dict(
                values=wrapped_wr_headers,
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=player_data_wr_stat_away.transpose().values.tolist(),
                align="left"
            )
        ), row=2, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["No Data Available"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[["No Data Available"]],
                align="left"
            )
        ), row=2, col=1)

    fig.update_layout(
        height=1200,
        width=1200,
        showlegend=False,
        title_text=subplot_title
    )
    # fig.show()
    return fig


def page_10(player_stat_data_report_year, home_team, away_team, report_year, subplot_title):
    player_data = player_stat_data_report_year.loc[((player_stat_data_report_year['team_roster'] == home_team) | (
                player_stat_data_report_year['team_roster'] == away_team)) & (player_stat_data_report_year[
                                                                                  'season_roster'] == report_year)]
    player_data.sort_values(by=['team_roster', 'season_roster', 'position', 'year'],
                            ascending=[True, True, True, False], inplace=True)
    player_data_col = ['team_roster', 'season_roster', 'playerId', 'player', 'position', 'year', 'team_stat',
                       'season_stat']

    player_data_rb = player_data.loc[(player_data['position'] == "RB")]
    player_data_rb_stat_col = player_data.filter(regex='rushing|fumbles').columns.tolist()
    player_data_rb_report_col = player_data_col + player_data_rb_stat_col
    player_data_rb_stat = player_data_rb[player_data_rb_report_col]
    player_data_rb_stat_home = player_data_rb_stat.loc[player_data_rb_stat['team_roster'] == home_team]
    player_data_rb_stat_away = player_data_rb_stat.loc[player_data_rb_stat['team_roster'] == away_team]

    def wrap_text_on_hyphen(text):
        return '<br>'.join(text.split('_'))

    wrapped_rb_headers = [wrap_text_on_hyphen(col) for col in player_data_rb_report_col]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}],
               [{"type": "table"}]]
    )

    # Check if the home team table is empty
    if not player_data_rb_stat_home.empty:
        fig.add_trace(go.Table(
            header=dict(
                values=wrapped_rb_headers,
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=player_data_rb_stat_home.transpose().values.tolist(),
                align="left"
            )
        ), row=1, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["No Data Available"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[["No Data Available"]],
                align="left"
            )
        ), row=1, col=1)

    # Check if the away team table is empty
    if not player_data_rb_stat_away.empty:
        fig.add_trace(go.Table(
            header=dict(
                values=wrapped_rb_headers,
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=player_data_rb_stat_away.transpose().values.tolist(),
                align="left"
            )
        ), row=2, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["No Data Available"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[["No Data Available"]],
                align="left"
            )
        ), row=2, col=1)

    fig.update_layout(
        height=1200,
        width=1200,
        showlegend=False,
        title_text=subplot_title
    )
    # fig.show()
    return fig


def page_11(player_stat_data_report_year, home_team, away_team, report_year, subplot_title):
    player_data = player_stat_data_report_year.loc[((player_stat_data_report_year['team_roster'] == home_team) | (
                player_stat_data_report_year['team_roster'] == away_team)) & (player_stat_data_report_year[
                                                                                  'season_roster'] == report_year)]
    player_data.sort_values(by=['team_roster', 'season_roster', 'position', 'year'],
                            ascending=[True, True, True, False], inplace=True)
    player_data_col = ['team_roster', 'season_roster', 'playerId', 'player', 'position', 'year', 'team_stat',
                       'season_stat']

    player_data_te = player_data.loc[(player_data['position'] == "TE")]
    player_data_te_stat_col = player_data.filter(regex='recieving|rushing|fumbles').columns.tolist()
    player_data_te_report_col = player_data_col + player_data_te_stat_col
    player_data_te_stat = player_data_te[player_data_te_report_col]
    player_data_te_stat_home = player_data_te_stat.loc[player_data_te_stat['team_roster'] == home_team]
    player_data_te_stat_away = player_data_te_stat.loc[player_data_te_stat['team_roster'] == away_team]

    def wrap_text_on_hyphen(text):
        return '<br>'.join(text.split('_'))

    wrapped_te_headers = [wrap_text_on_hyphen(col) for col in player_data_te_report_col]

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.03,
        specs=[[{"type": "table"}],
               [{"type": "table"}]]
    )

    # Check if the home team table is empty
    if not player_data_te_stat_home.empty:
        fig.add_trace(go.Table(
            header=dict(
                values=wrapped_te_headers,
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=player_data_te_stat_home.transpose().values.tolist(),
                align="left"
            )
        ), row=1, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["No Data Available"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[["No Data Available"]],
                align="left"
            )
        ), row=1, col=1)

    # Check if the away team table is empty
    if not player_data_te_stat_away.empty:
        fig.add_trace(go.Table(
            header=dict(
                values=wrapped_te_headers,
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=player_data_te_stat_away.transpose().values.tolist(),
                align="left"
            )
        ), row=2, col=1)
    else:
        fig.add_trace(go.Table(
            header=dict(
                values=["No Data Available"],
                font=dict(size=10),
                align="left"
            ),
            cells=dict(
                values=[["No Data Available"]],
                align="left"
            )
        ), row=2, col=1)

    fig.update_layout(
        height=1200,
        width=1200,
        showlegend=False,
        title_text=subplot_title
    )
    # fig.show()
    return fig

def figures_to_pdf(file_path_report, matchup, figures):
    filename_team_report = file_path_report + str(matchup) + ".pdf"
    pdf_pages = matplotlib.backends.backend_pdf.PdfPages(filename_team_report)
    
    def plotly_to_image(fig):
        return pio.to_image(fig, format='png', width=fig.layout.width, height=fig.layout.height)
    
    dpi = 300
    for fig in figures:
        # Convert Plotly figure to image
        img_data = plotly_to_image(fig)
        img_stream = io.BytesIO(img_data)
        img = plt.imread(img_stream, format='png')
        fig_width, fig_height = img.shape[1] / dpi, img.shape[0] / dpi
        plt.figure(figsize=(fig_width * 1.9, fig_height * 1.9), dpi=dpi)
        plt.imshow(img)
        plt.axis('off')
        pdf_pages.savefig()
        plt.close()
        img_stream.close()
    
    pdf_pages.close()
    print('Report Generated for ' + str(matchup))