import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from playbook import load
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

cfb_team_season_games_all_stats = load.sqlite_query_table('cfb_reporting_team_season_games_all_stats')
cfb_season_games_matchups = load.sqlite_query_table('cfb_reporting_season_games_matchups')
cfb_season_summary = load.sqlite_query_table('cfb_reporting_season_summary')
cfb_player_season_stats = load.sqlite_query_table('cfb_reporting_player_stats_by_season')
cfb_reporting_schedule = load.sqlite_query_table('cfb_reporting_schedule')


# Initialize Dash app
app = dash.Dash(__name__)

# Define dropdown options from your DataFrame
season_options = [{'label': str(s), 'value': str(s)} for s in
                  sorted(cfb_reporting_schedule['season'].unique(), reverse=True)]
seasonType_options = [{'label': st, 'value': st} for st in cfb_reporting_schedule['seasonType'].unique()]
week_options = [{'label': str(w), 'value': str(w)} for w in cfb_reporting_schedule['week'].unique()]

del cfb_reporting_schedule

# Layout for the Dash app
app.layout = html.Div([
    html.H1("BlitzAnalytics: College Football Matchup Dashboard"),

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

    dcc.Graph(id='matchup-summary-table'),
    dcc.Graph(id='matchup-current-season-table', style={"width": "100%"}),
    dcc.Graph(id='points-by-season-bar'),
    dcc.Graph(id='spread-by-season-hist'),
    html.Div([
        dcc.Graph(id='offense-pass-success-line', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='offense-rush-success-line', style={'display': 'inline-block', 'width': '49%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='defense-pass-success-line', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='defense-rush-success-line', style={'display': 'inline-block', 'width': '49%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='offense-successRate-line', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='defense-successRate-line', style={'display': 'inline-block', 'width': '49%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='offense-ppa-line', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='defense-ppa-line', style={'display': 'inline-block', 'width': '49%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='offense-epa-box', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='defense-epa-box', style={'display': 'inline-block', 'width': '49%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='offense-zscore-line', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='defense-zscore-line', style={'display': 'inline-block', 'width': '49%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),
    html.Div([
        dcc.Graph(id='specialteams-zscore-line', style={'display': 'inline-block', 'width': '49%'}),
        dcc.Graph(id='total-zscore-line', style={'display': 'inline-block', 'width': '49%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'}),

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

    ],
    [Input('matchup-dropdown', 'value')]
)
def generate_visualization_figures(matchup):
    # Define the list of Output IDs for the tuple below
    output_graphs = [
    ]
    # If no matchup is selected, return an empty figure for each graph dynamically
    if matchup is None:
        return {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}

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

    home_team_color = df_matchup_home_away_all_data.loc[
        df_matchup_home_away_all_data['team'] == home_team, 'color'].iloc[0]

    away_team_color = df_matchup_home_away_all_data.loc[
        df_matchup_home_away_all_data['team'] == away_team, 'color'].iloc[0]

    team_colors = {
        home_team: home_team_color,
        away_team: away_team_color
    }
    # Create Figures for Matchup Dashboard

    #Matchup Quick Summary Table
    fig_matchup_table = vis_matchup_summary_table(df_matchup_home_away_all_data, matchup, season)

    #Matchup Current Season Summary Table
    fig_matchup_current_season_table = vis_matchup_current_season_table(df_matchup_home_away_all_data, season)

    #Matchup Seasons Summary Table


    #Points and Spread by Season
    fig_points_by_season_bar = vis_points_by_season(df_matchup_home_away_all_data, team_colors)
    fig_spread_by_season_hist = vis_spread_by_season(df_matchup_home_away_all_data, team_colors)
    #Success Rates by Week
    fig_offense_pass_success_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                            'week',
                                                                            'offense.passingPlays.successRate',
                                                                            'Offense Passing Plays Success Rate')
    fig_offense_rush_success_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                            'week',
                                                                            'offense.rushingPlays.successRate',
                                                                            'Offense Rushing Plays Success Rate')
    fig_defense_pass_success_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                            'week',
                                                                            'defense.passingPlays.successRate',
                                                                            'Defense Passing Plays Success Rate')
    fig_defense_rush_success_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                    'week',
                                                                    'defense.rushingPlays.successRate',
                                                                    'Defense Rushing Plays Success Rate')
    fig_offense_success_rate_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'offense.successRate',
                                                                   'Offense Success Rate')
    fig_defense_success_rate_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'defense.successRate',
                                                                   'Defense Success Rate')
    #EPA and PPA
    fig_offense_ppa_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'offense.ppa',
                                                                   'Offense PPA')
    fig_defense_ppa_line = vis_stats_by_matchup_week_line(df_matchup_home_away_all_data, season, team_colors,
                                                                   'week',
                                                                   'defense.ppa',
                                                                   'Defense PPA')
    fig_epa_offense_by_season_box = vis_stats_by_matchup_season_box(df_matchup_home_away_all_data, team_colors,
                                                                   'season',
                                                                   'epa_per_game_offense.overall',
                                                                   'Offense EPA by Season')
    fig_epa_defense_by_season_box = vis_stats_by_matchup_season_box(df_matchup_home_away_all_data, team_colors,
                                                                   'season',
                                                                   'epa_per_game_defense.overall',
                                                                   'Defense EPA by Season')
    #Zscore Reports
    fig_offense_zscore_line = vis_stats_by_matchup_season_line(df_matchup_home_away_season_summary, team_colors,
                                                                   'season',
                                                                   'offense_zscore_final',
                                                                   'Offense Zscore by Season')
    fig_defense_zscore_line = vis_stats_by_matchup_season_line(df_matchup_home_away_season_summary, team_colors,
                                                                   'season',
                                                                   'defense_zscore_final',
                                                                   'Defense Zscore by Season')
    fig_specialteams_zscore_line = vis_stats_by_matchup_season_line(df_matchup_home_away_season_summary, team_colors,
                                                                   'season',
                                                                   'specialteams_zscore_final',
                                                                   'Special Teams ZScore by Season')
    fig_total_zscore_line = vis_stats_by_matchup_season_line(df_matchup_home_away_season_summary, team_colors,
                                                                   'season',
                                                                   'total_zscore',
                                                                   'Total Zscore by Season')
    return (fig_matchup_table, fig_matchup_current_season_table, fig_points_by_season_bar, fig_spread_by_season_hist,
            fig_offense_pass_success_line, fig_offense_rush_success_line, fig_defense_pass_success_line,
            fig_defense_rush_success_line, fig_offense_success_rate_line, fig_defense_success_rate_line,
            fig_offense_ppa_line, fig_defense_ppa_line, fig_epa_offense_by_season_box, fig_epa_defense_by_season_box,
            fig_offense_zscore_line, fig_defense_zscore_line, fig_specialteams_zscore_line, fig_total_zscore_line
            )

def vis_matchup_summary_table(df, matchup, season):
    df = df.loc[(df['Game Matchup'].astype(str) == str(matchup)) & (df['season'].astype(str) == str(season))]
    df_matchup_data = df[['team', 'conference', 'home_vs_away', 'AP Top 25', 'season', 'season_type', 'week']]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[col for col in df_matchup_data.columns],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df_matchup_data[col].tolist() for col in df_matchup_data.columns],
            align="left"
        )
    )]
    )
    return fig
def vis_matchup_current_season_table(df, season):
    df_sel_col = df[['team', 'conference', 'home_vs_away', 'AP Top 25', 'season', 'season_type', 'week',
                          'Game Matchup', 'win_loss','box_score','result_of_the_spread']]
    df_matchup_data = df_sel_col.loc[df_sel_col['season'].astype(str) == str(season)]

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[col for col in df_matchup_data.columns],
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df_matchup_data[col].tolist() for col in df_matchup_data.columns],
            align="left"
        )
    )]
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
        category_orders={"season": unique_seasons, "season_type": unique_season_types}
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


def matchup_report():
    print("Starting Matchup Report")
    # These are the default dash host and ports
    host = '127.0.0.1'
    port = 8050
    # Start the Dash server
    print(f"Dash app is running on http://{host}:{port}/")
    app.run_server(host=host, port=port, debug=True)
