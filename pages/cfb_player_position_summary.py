import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
from cfb.cfbd import load
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pc
import pandas as pd

cfb_player_season_stats = load.sqlite_query_table('cfb_reporting_player_stats_by_season')
cfb_team_info = load.sqlite_query_table('cfb_reporting_team_info')

def hex_to_rgba(hex_color, alpha=0.4):
    if hex_color.startswith('rgba'):
        return hex_color  # Already rgba, return it
    rgb_color = pc.hex_to_rgb(hex_color)
    return f'rgba({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, {alpha})'

# Initialize Dash app
dash.register_page(
    __name__,
    title='CFB Player Position Summary',
    name='CFB Player Position Summary'
)

# Define dropdown options
cfb_reporting_schedule = load.sqlite_query_table('cfb_reporting_schedule')
season_options = [{'label': str(s), 'value': str(s)} for s in
                  sorted(cfb_reporting_schedule['season'].unique(), reverse=True)]
seasonType_options = [{'label': st, 'value': st} for st in cfb_reporting_schedule['seasonType'].unique()]
week_options = [{'label': str(w), 'value': str(w)} for w in cfb_reporting_schedule['week'].unique()]
team_options = [{'label': str(w), 'value': str(w)} for w in cfb_team_info['team'].unique()]

# Layout for the Dash app
layout = html.Div([
    html.H1("Accretion Data: College Football Player Summary Dashboard", style={'color': 'white'}),

    # Flexbox container to arrange the dropdowns and graph side by side
    html.Div([
        # Left side: Dropdowns (40% of the width)
        html.Div([
            dcc.Dropdown(
                id='season-dropdown',
                options=season_options,
                value=season_options[0]['value'],
                style={"width": "100%"}
            ),
            dcc.Dropdown(
                id='team-dropdown',
                options=team_options,
                value=None,
                style={"width": "100%"}
            ),

        ], style={"width": "40%", "display": "flex", "flex-direction": "column"}),
    ], style={"display": "flex", "flex-direction": "row"}),

    dcc.Graph(id='players-summary-table-qb', style={"width": "100%", "margin-top": "20px"}),
    dcc.Graph(id='players-summary-table-wr', style={"width": "100%", "margin-top": "20px"}),
    dcc.Graph(id='players-summary-table-rb', style={"width": "100%", "margin-top": "20px"}),
    dcc.Graph(id='players-summary-table-te', style={"width": "100%", "margin-top": "20px"}),
])

@callback(
    Output('players-summary-table-qb', 'figure'),
    Output('players-summary-table-wr', 'figure'),
    Output('players-summary-table-rb', 'figure'),
    Output('players-summary-table-te', 'figure'),
    [Input('season-dropdown', 'value'),
     Input('team-dropdown', 'value')]
    )
def players_from_team_filter(season, team):
    # Check if a specific team is selected
    if team:
        df_players_season_team = cfb_player_season_stats.loc[
            (cfb_player_season_stats['season_roster'].astype(str) == str(season)) &
            (cfb_player_season_stats['team_roster'].astype(str) == str(team))
            ]

        # Set color for selected team
        team_colors = {team: cfb_team_info.loc[cfb_team_info['team'] == team, 'color'].values[0]
        if not cfb_team_info.loc[cfb_team_info['team'] == team].empty
        else '#FFFFFF'}

        figures = []

        player_stats_table_qb = vis_matchup_player_stats_table(
            df_players_season_team, 'qb', season, team_colors, "QB Stats")
        figures.append(player_stats_table_qb)

        player_stats_table_wr = vis_matchup_player_stats_table(
            df_players_season_team, 'wr', season, team_colors, "WR Stats")
        figures.append(player_stats_table_wr)

        player_stats_table_rb = vis_matchup_player_stats_table(
            df_players_season_team, 'rb', season, team_colors, "RB Stats")
        figures.append(player_stats_table_rb)

        player_stats_table_te = vis_matchup_player_stats_table(
            df_players_season_team, 'te', season, team_colors, "TE Stats")
        figures.append(player_stats_table_te)
        return figures

    else:
        # If no team is selected, select data for all teams
        df_players_season_team = cfb_player_season_stats.loc[
            (cfb_player_season_stats['season_roster'].astype(str) == str(season))
        ]

        figures = []

        player_stats_table_qb = vis_matchup_player_stats_no_color_table(
            df_players_season_team, 'qb', season, "QB Stats")
        figures.append(player_stats_table_qb)

        player_stats_table_wr = vis_matchup_player_stats_no_color_table(
            df_players_season_team, 'wr', season, "WR Stats")
        figures.append(player_stats_table_wr)

        player_stats_table_rb = vis_matchup_player_stats_no_color_table(
            df_players_season_team, 'rb', season, "RB Stats")
        figures.append(player_stats_table_rb)

        player_stats_table_te = vis_matchup_player_stats_no_color_table(
            df_players_season_team, 'te', season, "TE Stats")
        figures.append(player_stats_table_te)
        return figures

def vis_matchup_player_stats_table(df, stat_type, season_stat, team_colors, player_stat_title):
    player_data = df.loc[(df['season_stat'].astype(str) == str(season_stat))]
    player_data.sort_values(by=['team_roster', 'season_roster', 'position', 'year'],
                            ascending=[True, True, True, False], inplace=True)
    player_data_col = ['team_roster', 'season_roster', 'playerId', 'player', 'position', 'year', 'team_stat',
                       'season_stat']

    if stat_type == 'qb':
        player_data_pos = player_data.loc[(player_data['position'] == "QB")]
        player_data_pos_stat_col = player_data.filter(regex='passing|rushing|fumbles').columns.tolist()
        player_data_pos_report_col = player_data_col + player_data_pos_stat_col
        player_data_pos_stat = player_data_pos[player_data_pos_report_col]
        player_data_pos_stat.sort_values(by=['passing_YDS', 'passing_PCT', 'passing_TD', 'rushing_TD', 'rushing_YDS'],
                                ascending=[False, False, False, False, False], inplace=True)

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

def vis_matchup_player_stats_no_color_table(df, stat_type, season_stat, player_stat_title):
    player_data = df.loc[(df['season_stat'].astype(str) == str(season_stat))]
    player_data.sort_values(by=['team_roster', 'season_roster', 'position', 'year'],
                            ascending=[True, True, True, False], inplace=True)
    player_data_col = ['team_roster', 'season_roster', 'playerId', 'player', 'position', 'year', 'team_stat',
                       'season_stat']

    if stat_type == 'qb':
        player_data_pos = player_data.loc[(player_data['position'] == "QB")]
        player_data_pos_stat_col = player_data.filter(regex='passing|rushing|fumbles').columns.tolist()
        player_data_pos_report_col = player_data_col + player_data_pos_stat_col
        player_data_pos_stat = player_data_pos[player_data_pos_report_col]
        player_data_pos_stat.sort_values(by=['passing_YDS', 'passing_PCT', 'passing_TD', 'rushing_TD', 'rushing_YDS'],
                                ascending=[False, False, False, False, False], inplace=True)

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


    fig = go.Figure(go.Table(
        header=dict(
            values=wrapped_pos_headers,
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[player_data_pos_stat[col].tolist() for col in player_data_pos_stat.columns],
            align="left",
        )
    ))
    fig.update_layout(
        height=800,
        title_text=player_stat_title
    )
    return fig