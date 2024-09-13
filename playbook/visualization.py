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

# Layout for the Dash app
app.layout = html.Div([
    html.H1("BlitzAnalytics: College Football Matchup Dashboard"),

    dcc.Dropdown(
        id='season-dropdown',
        options=season_options,
        value=season_options[0]['value']  # Default to the latest season
    ),

    dcc.Dropdown(
        id='seasonType-dropdown',
        options=seasonType_options,
        value=seasonType_options[0]['value']  # Default to first season type
    ),

    dcc.Dropdown(
        id='week-dropdown',
        options=week_options,
        value=week_options[0]['value']  # Default to first week
    ),

    dcc.Dropdown(
        id='matchup-dropdown',
        options=[],  # Initially empty, will be filled by callback
        value=None,
        searchable=True
    ),

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
    Output('points-by-season-bar', 'figure'),
    Output('spread-by-season-hist', 'figure'),
    Output('offense-pass-success-line', 'figure'),
    Output('offense-rush-success-line', 'figure'),
    Output('defense-pass-success-line', 'figure'),
    Output('defense-rush-success-line', 'figure')
    ],
    [Input('matchup-dropdown', 'value')]
)
def generate_visualization_figures(matchup):
    # Define the list of Output IDs for the tuple below
    output_graphs = [
        'points-by-season-bar',
        'spread-by-season-hist',
        'offense-pass-success-line',
        'offense-rush-success-line',
        'defense-pass-success-line',
        'defense-rush-success-line',
    ]
    # If no matchup is selected, return an empty figure for each graph dynamically
    if matchup is None:
        return tuple({} for _ in range(len(output_graphs)))

    # Filter data based on selected matchup
    df_matchup = cfb_season_games_matchups.loc[
        (cfb_season_games_matchups['Game Matchup'] == matchup)
    ]
    season = df_matchup['season'].values[0]
    home_team = df_matchup['home_team'].tolist()
    away_team = df_matchup['away_team'].tolist()

    # Get the data for home and away teams
    df_matchup_home_away_all_data = cfb_team_season_games_all_stats.loc[
        cfb_team_season_games_all_stats['team'].isin(home_team + away_team)
    ]

    # Create Figures for Matchup Dashboard
    fig_points_by_season_bar = vis_points_by_season(df_matchup_home_away_all_data)
    fig_spread_by_season_hist = vis_spread_by_season(df_matchup_home_away_all_data)
    fig_offense_pass_success_line = vis_stats_by_matchup_year_line(df_matchup_home_away_all_data, season,
                                                                            'week',
                                                                            'offense.passingPlays.successRate',
                                                                            'Offense Passing Plays Success Rate')
    fig_offense_rush_success_line = vis_stats_by_matchup_year_line(df_matchup_home_away_all_data, season,
                                                                            'week',
                                                                            'offense.rushingPlays.successRate',
                                                                            'Offense Rushing Plays Success Rate')
    fig_defense_pass_success_line = vis_stats_by_matchup_year_line(df_matchup_home_away_all_data, season,
                                                                            'week',
                                                                            'defense.passingPlays.successRate',
                                                                            'Defense Passing Plays Success Rate')
    fig_defense_pass_success_line = vis_stats_by_matchup_year_line(df_matchup_home_away_all_data, season,
                                                                            'week',
                                                                            'defense.rushingPlays.successRate',
                                                                            'Defense Rushing Plays Success Rate')
    return (fig_points_by_season_bar, fig_spread_by_season_hist, fig_offense_pass_success_line,
            fig_offense_rush_success_line, fig_defense_pass_success_line, fig_defense_pass_success_line )

def vis_points_by_season(df):
    unique_seasons = sorted(df['season'].unique())  # Sort if needed
    unique_season_types = sorted(df['season_type'].unique())

    # Create the figure
    fig = px.bar(
        df,
        x="week",
        y="points",
        color="team",
        #color_discrete_map="color",
        barmode="group",
        facet_col="season",
        facet_row="season_type",
        category_orders={"season": unique_seasons, "season_type": unique_season_types}
    )
    return fig

def vis_spread_by_season(df):
    df['spread_counts'] = 1
    fig = px.histogram(
        df,
        x="result_of_the_spread",
        y="spread_counts",
        barmode="group",
        facet_col="season",
        color='team',
        #color_discrete_map=team_colors
    )
    fig.update_xaxes(type='category')
    return fig

def vis_stats_by_matchup_year_line(df, season, x_value, y_value, vis_title):
    df = df.loc[df['season'].astype(str) == str(season)]
    fig = px.line(
        df,
        x=x_value,
        y=y_value,
        markers=True,
        color='team',
        height=400,
        width=800,
        title=vis_title
        #color_discrete_map=team_colors
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
