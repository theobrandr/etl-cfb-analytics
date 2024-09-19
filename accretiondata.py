import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from playbook import load
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pc
import pandas as pd

cfb_team_season_games_all_stats = load.sqlite_query_table('cfb_reporting_team_season_games_all_stats')
cfb_season_games_matchups = load.sqlite_query_table('cfb_reporting_season_games_matchups')
cfb_season_summary = load.sqlite_query_table('cfb_reporting_season_summary')
cfb_player_season_stats = load.sqlite_query_table('cfb_reporting_player_stats_by_season')
cfb_reporting_schedule = load.sqlite_query_table('cfb_reporting_schedule')


def hex_to_rgba(hex_color, alpha=0.4):
    rgb_color = pc.hex_to_rgb(hex_color)
    return f'rgba({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, {alpha})'


# Initialize Dash app
app = dash.Dash(__name__)

# Define dropdown options from your DataFrame
season_options = [{'label': str(s), 'value': str(s)} for s in
                  sorted(cfb_reporting_schedule['season'].unique(), reverse=True)]
seasonType_options = [{'label': st, 'value': st} for st in cfb_reporting_schedule['seasonType'].unique()]
week_options = [{'label': str(w), 'value': str(w)} for w in cfb_reporting_schedule['week'].unique()]

del cfb_reporting_schedule

'''# Layout for the Dash app
app.layout = html.Div([
    html.H1("Accretion Data: College Football Matchup Dashboard"),

    dcc.Dropdown(
        id='season-dropdown',
        options=season_options,
        value=season_options[0]['value'],  # Default to the latest season
        style={"width": "50%"}
    ),

    dcc.Dropdown(
        id='seasonType-dropdown',
        options=seasonType_options,
        value=seasonType_options[0]['value'],  # Default to first season type
        style={"width": "50%"}
    ),

    dcc.Dropdown(
        id='week-dropdown',
        options=week_options,
        value=week_options[0]['value'],  # Default to first week
        style={"width": "50%"}
    ),

    dcc.Dropdown(
        id='matchup-dropdown',
        options=[],  # Initially empty, will be filled by callback
        value=None,
        searchable=True,
        style={"width": "50%"}
    ),

    dcc.Graph(id='matchup-summary-table'),'''
# Layout for the Dash app
app.layout = html.Div([
    html.H1("Accretion Data: College Football Matchup Dashboard"),

    # Flexbox container to arrange the dropdowns and graph side by side
    html.Div([
        # Left side: Dropdowns (40% of the width)
        html.Div([
            dcc.Dropdown(
                id='season-dropdown',
                options=season_options,
                value=season_options[0]['value'],  # Default to the latest season
                style={"width": "100%"}  # Full width of the 40% container
            ),

            dcc.Dropdown(
                id='seasonType-dropdown',
                options=seasonType_options,
                value=seasonType_options[0]['value'],  # Default to first season type
                style={"width": "100%"}  # Full width of the 40% container
            ),

            dcc.Dropdown(
                id='week-dropdown',
                options=week_options,
                value=week_options[0]['value'],  # Default to first week
                style={"width": "100%"}  # Full width of the 40% container
            ),

            dcc.Dropdown(
                id='matchup-dropdown',
                options=[],
                value=None,
                searchable=True,
                style={"width": "100%"}
            ),
        ], style={"width": "40%", "padding": "5px"}),

        # Right side: Graph (60% of the width)
        html.Div([
            dcc.Graph(id='matchup-summary-table')
        ], style={"width": "60%", "padding": "5px"})
    ], style={"display": "flex", "flex-direction": "row"}),
    dcc.Graph(id='matchup-alls-seasons-summary-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='matchup-current-season-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='points-by-season-bar', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='spread-by-season-hist', style={"width": "100%", "margin-bottom": "5px"}),
    html.Div([
        dcc.Graph(id='offense-pass-success-line',
                  style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"}),
        dcc.Graph(id='offense-rush-success-line',
                  style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='defense-pass-success-line',
                  style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"}),
        dcc.Graph(id='defense-rush-success-line',
                  style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='offense-successRate-line',
                  style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"}),
        dcc.Graph(id='defense-successRate-line',
                  style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='offense-ppa-line', style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"}),
        dcc.Graph(id='defense-ppa-line', style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='offense-epa-box', style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"}),
        dcc.Graph(id='defense-epa-box', style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='offense-zscore-line', style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"}),
        dcc.Graph(id='defense-zscore-line', style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='specialteams-zscore-line',
                  style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"}),
        dcc.Graph(id='total-zscore-line', style={'display': 'inline-block', 'width': '49%', "margin-bottom": "5px"})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    dcc.Graph(id='stats-offense-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='stats-offense-downs-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='stats-defense-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='stats-specialteams-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='stats-player-qb-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='stats-player-wr-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='stats-player-rb-table', style={"width": "100%", "margin-bottom": "5px"}),
    dcc.Graph(id='stats-player-te-table', style={"width": "100%", "margin-bottom": "5px"}),

])


# Callback to update the matchup dropdown based on selected season, seasonType, and week
@app.callback(
    Output('matchup-dropdown', 'options'),
    [Input('season-dropdown', 'value'),
     Input('seasonType-dropdown', 'value'),
     Input('week-dropdown', 'value')]
)
def update_matchup_dropdown(season, seasonType, week):
    matchups = matchup_from_filter(season, seasonType, week, cfb_season_games_matchups)
    return [{'label': m, 'value': m} for m in matchups]


def matchup_from_filter(season, season_type, week, cfb_season_games_matchups):
    df = cfb_season_games_matchups.loc[
        (cfb_season_games_matchups['season'].astype(str).str.contains(str(season), na=False)) &
        (cfb_season_games_matchups['week'].astype(str) == (str(week))) &
        (cfb_season_games_matchups['season_type'].astype(str).str.contains(str(season_type), na=False))
        ]
    matchup = df['Game Matchup'].unique()
    return matchup


# Callback to update the graph based on selected matchup
@app.callback(
    [
        Output('matchup-summary-table', 'figure'),
        Output('matchup-alls-seasons-summary-table', 'figure'),
        Output('matchup-current-season-table', 'figure'),
        Output('points-by-season-bar', 'figure'),
        Output('spread-by-season-hist', 'figure'),
        Output('offense-pass-success-line', 'figure'),
        Output('offense-rush-success-line', 'figure'),
        Output('defense-pass-success-line', 'figure'),
        Output('defense-rush-success-line', 'figure'),
        Output('offense-successRate-line', 'figure'),
        Output('defense-successRate-line', 'figure'),
        Output('offense-ppa-line', 'figure'),
        Output('defense-ppa-line', 'figure'),
        Output('offense-epa-box', 'figure'),
        Output('defense-epa-box', 'figure'),
        Output('offense-zscore-line', 'figure'),
        Output('defense-zscore-line', 'figure'),
        Output('specialteams-zscore-line', 'figure'),
        Output('total-zscore-line', 'figure'),
        Output('stats-offense-table', 'figure'),
        Output('stats-offense-downs-table', 'figure'),
        Output('stats-defense-table', 'figure'),
        Output('stats-specialteams-table', 'figure'),
        Output('stats-player-qb-table', 'figure'),
        Output('stats-player-wr-table', 'figure'),
        Output('stats-player-rb-table', 'figure'),
        Output('stats-player-te-table', 'figure'),
    ],
    [Input('matchup-dropdown', 'value')]
)
def generate_visualization_figures(matchup):
    # Define the list of Output IDs for the tuple below
    output_graphs = [
    ]
    # If no matchup is selected, return an empty figure for each graph dynamically
    if matchup is None:
        return {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

    # Filter data based on selected matchup
    df_matchup = cfb_season_games_matchups.loc[
        (cfb_season_games_matchups['Game Matchup'] == matchup)
    ]
    season = df_matchup['season'].values[0]
    home_team = df_matchup['home_team'].values[0]
    away_team = df_matchup['away_team'].values[0]
    # Get the data for home and away teams
    df_matchup_home_away_all_data = cfb_team_season_games_all_stats.loc[
        (cfb_team_season_games_all_stats['team'] == home_team) | (cfb_team_season_games_all_stats['team'] == away_team)
        ]
    df_matchup_home_away_season_summary = cfb_season_summary.loc[
        (cfb_season_summary['team'] == home_team) | (cfb_season_summary['team'] == away_team)
        ]
    df_matchup_player_season_stats = cfb_player_season_stats.loc[
        (cfb_player_season_stats['team_roster'] == home_team) | (cfb_player_season_stats['team_roster'] == away_team)
        ]

    # Filter Color Information for visualization
    home_team_color = df_matchup_home_away_all_data.loc[
        df_matchup_home_away_all_data['team'] == home_team, 'color'].iloc[0]

    away_team_color = df_matchup_home_away_all_data.loc[
        df_matchup_home_away_all_data['team'] == away_team, 'color'].iloc[0]

    team_colors = {
        home_team: home_team_color,
        away_team: away_team_color
    }
    # Create Figures for Matchup Dashboard
    figures = []
    # Matchup Quick Summary Table
    fig_matchup_table = vis_matchup_summary_table(df_matchup_home_away_all_data, matchup, season, team_colors)
    figures.append(fig_matchup_table)

    # Matchup Seasons Summary Table
    fig_matchup_all_seasons_summary_table = vis_matchup_all_seasons_summary_table(df_matchup_home_away_season_summary,
                                                                                  team_colors)
    figures.append(fig_matchup_all_seasons_summary_table)

    # Matchup Current Season Summary Table
    fig_matchup_current_season_table = vis_matchup_current_season_table(df_matchup_home_away_all_data, season,
                                                                        team_colors)
    figures.append(fig_matchup_current_season_table)

    # Points and Spread by Season
    fig_points_by_season_bar = vis_points_by_season(df_matchup_home_away_all_data, team_colors)
    figures.append(fig_points_by_season_bar)
    fig_spread_by_season_hist = vis_spread_by_season(df_matchup_home_away_all_data, team_colors)
    figures.append(fig_spread_by_season_hist)
    # Success Rates by Week
    fig_offense_pass_success_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'offense.passingPlays.successRate',
                                                                   'Offense Passing Plays Success Rate')
    figures.append(fig_offense_pass_success_line)
    fig_offense_rush_success_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'offense.rushingPlays.successRate',
                                                                   'Offense Rushing Plays Success Rate')
    figures.append(fig_offense_rush_success_line)
    fig_defense_pass_success_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'defense.passingPlays.successRate',
                                                                   'Defense Passing Plays Success Rate')
    figures.append(fig_defense_pass_success_line)
    fig_defense_rush_success_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'defense.rushingPlays.successRate',
                                                                   'Defense Rushing Plays Success Rate')
    figures.append(fig_defense_rush_success_line)
    fig_offense_success_rate_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'offense.successRate',
                                                                   'Offense Success Rate')
    figures.append(fig_offense_success_rate_line)
    fig_defense_success_rate_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'defense.successRate',
                                                                   'Defense Success Rate')
    figures.append(fig_defense_success_rate_line)
    # EPA and PPA
    fig_offense_ppa_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                          'week',
                                                          'offense.ppa',
                                                          'Offense PPA')
    figures.append(fig_offense_ppa_line)
    fig_defense_ppa_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                          'week',
                                                          'defense.ppa',
                                                          'Defense PPA')
    figures.append(fig_defense_ppa_line)
    fig_epa_offense_by_season_box = vis_stats_by_matchup_season_box(df_matchup_home_away_all_data, team_colors,
                                                                    'season',
                                                                    'epa_per_game_offense.overall',
                                                                    'Offense EPA by Season')
    figures.append(fig_epa_offense_by_season_box)
    fig_epa_offense_by_season_box = vis_stats_by_matchup_season_box(df_matchup_home_away_all_data, team_colors,
                                                                    'season',
                                                                    'epa_per_game_defense.overall',
                                                                    'Defense EPA by Season')
    figures.append(fig_epa_offense_by_season_box)
    # Zscore Reports
    fig_offense_zscore_line = vis_stats_by_matchup_season_line(df_matchup_home_away_season_summary, team_colors,
                                                               'season',
                                                               'offense_zscore_final',
                                                               'Offense Zscore by Season')
    figures.append(fig_offense_zscore_line)
    fig_defense_zscore_line = vis_stats_by_matchup_season_line(df_matchup_home_away_season_summary, team_colors,
                                                               'season',
                                                               'defense_zscore_final',
                                                               'Defense Zscore by Season')
    figures.append(fig_defense_zscore_line)
    fig_specialteams_zscore_line = vis_stats_by_matchup_season_line(df_matchup_home_away_season_summary, team_colors,
                                                                    'season',
                                                                    'specialteams_zscore_final',
                                                                    'Special Teams ZScore by Season')
    figures.append(fig_specialteams_zscore_line)
    fig_total_zscore_line = vis_stats_by_matchup_season_line(df_matchup_home_away_season_summary, team_colors,
                                                             'season',
                                                             'total_zscore',
                                                             'Total Zscore by Season')
    figures.append(fig_total_zscore_line)
    # Season Stat Tables
    fig_matchup_stats_offense_table = vis_matchup_stats_table(df_matchup_home_away_season_summary,
                                                              'offense', season, team_colors)
    figures.append(fig_matchup_stats_offense_table)
    fig_matchup_stats_offense_downs_table = vis_matchup_stats_table(df_matchup_home_away_season_summary,
                                                                    'offense_downs', season, team_colors)
    figures.append(fig_matchup_stats_offense_downs_table)
    fig_matchup_stats_defense_table = vis_matchup_stats_table(df_matchup_home_away_season_summary,
                                                              'defense', season, team_colors)
    figures.append(fig_matchup_stats_defense_table)
    fig_matchup_stats_special_teams_table = vis_matchup_stats_table(df_matchup_home_away_season_summary,
                                                                    'special_teams', season, team_colors)
    figures.append(fig_matchup_stats_special_teams_table)

    fig_matchup_player_stats_qb_table = vis_matchup_player_stats_table(df_matchup_player_season_stats,
                                                                       'qb', season, team_colors, "QB Stats")
    figures.append(fig_matchup_player_stats_qb_table)
    fig_matchup_player_stats_wr_table = vis_matchup_player_stats_table(df_matchup_player_season_stats,
                                                                       'wr', season, team_colors, "WR Stats")
    figures.append(fig_matchup_player_stats_wr_table)
    fig_matchup_player_stats_rb_table = vis_matchup_player_stats_table(df_matchup_player_season_stats,
                                                                       'rb', season, team_colors, "RB Stats")
    figures.append(fig_matchup_player_stats_rb_table)
    fig_matchup_player_stats_te_table = vis_matchup_player_stats_table(df_matchup_player_season_stats,
                                                                       'te', season, team_colors, "TE Stats")
    figures.append(fig_matchup_player_stats_te_table)

    return figures


def vis_matchup_summary_table(df, matchup, season, team_colors):
    df = df.loc[(df['Game Matchup'].astype(str) == str(matchup)) & (df['season'].astype(str) == str(season))]
    df_matchup_data = df[['team', 'conference', 'home_vs_away', 'AP Top 25', 'season', 'season_type', 'week']]

    team_colors_rgba = {team: hex_to_rgba(color) for team, color in team_colors.items()}
    cell_colors = [team_colors_rgba.get(team, 'rgba(255, 255, 255, 0.4)') for team in df_matchup_data['team']]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[col for col in df_matchup_data.columns],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df_matchup_data[col].tolist() for col in df_matchup_data.columns],
            align="left",
            fill=dict(
                color=[cell_colors + ['rgba(255, 255, 255, 0.4)'] * (len(df_matchup_data.columns) - 1)
                       ] * len(df_matchup_data)
            )
        ))]
    )
    return fig


def vis_matchup_all_seasons_summary_table(df, team_colors):
    season_summary_columns = ['season', 'team', 'total.wins', 'total.losses', 'home_points_season_mean',
                              'away_points_season_mean', 'epa_per_game_offense_overall_avg_per_season',
                              'epa_per_game_offense_overall_avg_per_season']

    team_colors_rgba = {team: hex_to_rgba(color) for team, color in team_colors.items()}
    cell_colors = [team_colors_rgba.get(team, 'rgba(255, 255, 255, 0.4)') for team in df['team']]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=season_summary_columns,
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df[col].tolist() for col in season_summary_columns],
            align="left",
            fill=dict(
                color=[cell_colors + ['rgba(255, 255, 255, 0.4)'] * (len(season_summary_columns) - 1)
                       ] * len(df)
            )
        ))]
    )
    return fig


def vis_matchup_current_season_table(df, season, team_colors):
    df_sel_col = df[['team', 'conference', 'home_vs_away', 'AP Top 25', 'season', 'season_type', 'week',
                     'Game Matchup', 'win_loss', 'points', 'box_score', 'result_of_the_spread']]
    df_matchup_data = df_sel_col.loc[df_sel_col['season'].astype(str) == str(season)]

    team_colors_rgba = {team: hex_to_rgba(color) for team, color in team_colors.items()}
    cell_colors = [team_colors_rgba.get(team, 'rgba(255, 255, 255, 0.4)') for team in df_matchup_data['team']]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[col for col in df_matchup_data.columns],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df_matchup_data[col].tolist() for col in df_matchup_data.columns],
            align="left",
            fill=dict(
                color=[cell_colors + ['rgba(255, 255, 255, 0.4)'] * (len(df_matchup_data.columns) - 1)
                       ] * len(df_matchup_data),
            )
        ))]
    )
    fig.update_layout(
        height=800
    )
    return fig


def vis_points_by_season(df, team_colors):
    unique_seasons = sorted(df['season'].unique())  # Sort if needed
    unique_season_types = sorted(df['season_type'].unique())

    # Create the figure
    fig = px.bar(
        df,
        x="week",
        y="points",
        color="team",
        color_discrete_map=team_colors,
        barmode="group",
        facet_col="season",
        facet_row="season_type",
        category_orders={"season": unique_seasons, "season_type": unique_season_types},
        height=800,
    )
    return fig


def vis_spread_by_season(df, team_colors):
    df['spread_counts'] = 1
    fig = px.histogram(
        df,
        x="result_of_the_spread",
        y="spread_counts",
        barmode="group",
        facet_col="season",
        color='team',
        color_discrete_map=team_colors
    )
    fig.update_xaxes(type='category')
    return fig


def vis_stats_by_matchup_week_line(df, season, team_colors, x_value, y_value, vis_title):
    df = df.loc[df['season'].astype(str) == str(season)]
    fig = px.line(
        df,
        x=x_value,
        y=y_value,
        markers=True,
        color='team',
        height=600,
        width=800,
        title=vis_title,
        color_discrete_map=team_colors
    )
    unique_tick = sorted(df[x_value].unique())
    fig.update_xaxes(tickmode='array', tickvals=unique_tick, tickangle=0, dtick=1)
    return fig


def vis_stats_by_matchup_season_box(df, team_colors, x_value, y_value, vis_title):
    fig = px.box(
        df,
        x=x_value,
        y=y_value,
        color='team',
        height=600,
        width=800,
        title=vis_title,
        color_discrete_map=team_colors
    )
    unique_tick = sorted(df[x_value].unique())
    fig.update_xaxes(tickmode='array', tickvals=unique_tick, tickangle=0, dtick=1)
    return fig


def vis_stats_by_matchup_season_line(df, team_colors, x_value, y_value, vis_title):
    fig = px.line(
        df,
        x=x_value,
        y=y_value,
        markers=True,
        color='team',
        height=600,
        width=800,
        title=vis_title,
        color_discrete_map=team_colors
    )
    unique_tick = sorted(df[x_value].unique())
    fig.update_xaxes(tickmode='array', tickvals=unique_tick, tickangle=0, dtick=1)
    return fig


def vis_matchup_stats_table(df, stat_type, season, team_colors):
    if stat_type == 'offense':
        stat_type_columns = ['team', 'season', 'offense_possessionTime', 'offense_totalYards',
                             'offense_netPassingYards', 'offense_passAttempts', 'offense_passCompletions',
                             'offense_passingTDs', 'offense_rushingYards', 'offense_rushingAttempts',
                             'offense_rushingTDs', 'offense_turnovers', 'offense_fumblesLost',
                             'offense_passesIntercepted']
    elif stat_type == 'offense_downs':
        stat_type_columns = ['team', 'season', 'offense_firstDowns', 'offense_thirdDowns',
                             'offense_thirdDownConversions',
                             'offense_fourthDowns', 'offense_fourthDownConversions', 'offense_turnovers',
                             'offense_fumblesLost', 'offense_passesIntercepted']
    elif stat_type == 'defense':
        stat_type_columns = ['team', 'season', 'defense_tacklesForLoss', 'defense_sacks', 'defense_fumblesRecovered',
                             'defense_interceptions', 'defense_interceptionTDs']
    elif stat_type == 'special_teams':
        stat_type_columns = ['team', 'season', 'specialteams_kickReturns', 'specialteams_kickReturnYards',
                             'specialteams_kickReturnTDs',
                             'specialteams_puntReturnYards', 'specialteams_puntReturns', 'specialteams_puntReturnTDs']

    df = df.loc[(df['season'].astype(str) == str(season))]
    team_colors_rgba = {team: hex_to_rgba(color) for team, color in team_colors.items()}
    cell_colors = [team_colors_rgba.get(team, 'rgba(255, 255, 255, 0.4)') for team in
                   df['team']]

    fig = go.Figure(go.Table(
        header=dict(
            values=list(stat_type_columns),
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df[col].tolist() for col in list(stat_type_columns)],
            align="left",
            fill=dict(
                color=[cell_colors + ['rgba(255, 255, 255, 0.4)'] * (len(stat_type_columns) - 1)
                       ] * len(df),
            )
        )
    )
    )
    return fig


def vis_matchup_player_stats_table(df, stat_type, season_roster, team_colors, player_stat_title):
    player_data = df.loc[(df['season_roster'].astype(str) == str(season_roster))]
    player_data.sort_values(by=['team_roster', 'season_roster', 'position', 'year'],
                            ascending=[True, True, True, False], inplace=True)
    player_data_col = ['team_roster', 'season_roster', 'playerId', 'player', 'position', 'year', 'team_stat',
                       'season_stat']

    if stat_type == 'qb':
        player_data_pos = player_data.loc[(player_data['position'] == "QB")]
        player_data_pos_stat_col = player_data.filter(regex='passing|rushing|fumbles').columns.tolist()
        player_data_pos_report_col = player_data_col + player_data_pos_stat_col
        player_data_pos_stat = player_data_pos[player_data_pos_report_col]

    elif stat_type == 'wr':
        player_data_pos = player_data.loc[(player_data['position'] == "WR")]
        player_data_pos_stat_col = player_data.filter(regex='recieving|rushing|fumbles').columns.tolist()
        player_data_pos_report_col = player_data_col + player_data_pos_stat_col
        player_data_pos_stat = player_data_pos[player_data_pos_report_col]

    elif stat_type == 'rb':
        player_data_pos = player_data.loc[(player_data['position'] == "RB")]
        player_data_pos_stat_col = player_data.filter(regex='rushing|fumbles').columns.tolist()
        player_data_pos_report_col = player_data_col + player_data_pos_stat_col
        player_data_pos_stat = player_data_pos[player_data_pos_report_col]

    elif stat_type == 'te':
        player_data_pos = player_data.loc[(player_data['position'] == "TE")]
        player_data_pos_stat_col = player_data.filter(regex='recieving|rushing|fumbles').columns.tolist()
        player_data_pos_report_col = player_data_col + player_data_pos_stat_col
        player_data_pos_stat = player_data_pos[player_data_pos_report_col]

    def wrap_text_on_hyphen(text):
        return '<br>'.join(text.split('_'))

    wrapped_pos_headers = [wrap_text_on_hyphen(col) for col in player_data_pos_report_col]

    team_colors_rgba = {team: hex_to_rgba(color) for team, color in team_colors.items()}
    cell_colors = [team_colors_rgba.get(team, 'rgba(255, 255, 255, 0.4)') for team in
                   player_data_pos_stat['team_roster']]

    fig = go.Figure(go.Table(
        header=dict(
            values=wrapped_pos_headers,
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[player_data_pos_stat[col].tolist() for col in player_data_pos_stat.columns],
            align="left",
            fill=dict(
                color=[
                          cell_colors + ['rgba(255, 255, 255, 0.4)'] * (len(wrapped_pos_headers) - 1)
                      ] * len(player_data_pos_stat),
            )
        )
    ))
    fig.update_layout(
        height=800,
        title_text=player_stat_title
    )
    return fig


def matchup_report():
    print("Starting Matchup Report")
    # These are the default dash host and ports
    host = '127.0.0.1'
    port = 8050
    # Start the Dash server
    print(f"Dash app is running on http://{host}:{port}/")
    app.run_server(host=host, port=port, debug=True)

matchup_report()