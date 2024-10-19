import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
from cfb.cfbd import load
import plotly.graph_objects as go
import plotly.express as px
import plotly.colors as pc
import pandas as pd

cfb_team_season_games_all_stats = load.sqlite_query_table('cfb_reporting_season_weeks_teams_all_stats')
cfb_season_games_matchups = load.sqlite_query_table('cfb_reporting_season_games_matchups')
cfb_season_summary = load.sqlite_query_table('cfb_reporting_season_summary')
cfb_player_season_stats = load.sqlite_query_table('cfb_reporting_player_stats_by_season')
cfb_reporting_schedule = load.sqlite_query_table('cfb_reporting_schedule')

def hex_to_rgba(hex_color, alpha=0.4):
    rgb_color = pc.hex_to_rgb(hex_color)
    return f'rgba({rgb_color[0]}, {rgb_color[1]}, {rgb_color[2]}, {alpha})'

# Initialize Dash app
dash.register_page(
    __name__,
    title='CFB Matchup Summary  Analytics',
    name='CFB Matchup Summary Analytics'
)

# Define dropdown options from your DataFrame
season_options = [{'label': str(s), 'value': str(s)} for s in
                  sorted(cfb_reporting_schedule['season'].unique(), reverse=True)]
seasonType_options = [{'label': st, 'value': st} for st in cfb_reporting_schedule['seasonType'].unique()]
week_options = [{'label': str(w), 'value': str(w)} for w in cfb_reporting_schedule['week'].unique()]

# Layout for the Dash app
layout = html.Div([
    html.H1("Accretion Data: College Football Matchup Dashboard", style={'color': 'white'}),

    # Flexbox container to arrange the dropdowns and graph side by side
    html.Div([
        # Left side: Dropdowns (40% of the width)
        html.Div([
            dcc.Dropdown(
                id='season-dropdown',
                options=season_options,
                value=season_options[0]['value'],  # Default to the latest season
                style={"width": "100%"}
            ),
            dcc.Dropdown(
                id='seasonType-dropdown',
                options=seasonType_options,
                value=seasonType_options[0]['value'],  # Default to first season type
                style={"width": "100%"}
            ),
            dcc.Dropdown(
                id='week-dropdown',
                options=week_options,
                value=week_options[0]['value'],  # Default to first week
                style={"width": "100%"}
            ),
        ], style={"width": "40%", "display": "flex", "flex-direction": "column"}),
    ], style={"display": "flex", "flex-direction": "row"}),

    dcc.Graph(id='all-matchups-summary-table', style={"width": "100%", "margin-top": "20px"}),
])

@callback(
    Output('all-matchups-summary-table', 'figure'),
    [Input('season-dropdown', 'value'),
     Input('seasonType-dropdown', 'value'),
     Input('week-dropdown', 'value')]
)
def matchups_from_filter(season, season_type, week):
    df_matchups = cfb_team_season_games_all_stats.loc[
        (cfb_team_season_games_all_stats['season'].astype(str) == str(season)) &
        (cfb_team_season_games_all_stats['week'].astype(str) == str(week)) &
        (cfb_team_season_games_all_stats['season_type'].astype(str) == str(season_type))
    ]

    df_season_summary = cfb_season_summary.loc[
        (cfb_season_summary['season'].astype(str) == str(season))
    ]

    df_matchups_with_season_summary = pd.merge(df_matchups, df_season_summary,
                                               left_on=['team', 'season'],
                                               right_on=['team', 'season'],
                                               how='left')

    return vis_matchup_summary_table(df_matchups_with_season_summary)


def vis_matchup_summary_table(df_matchups_with_season_summary):
    df_sel_col = df_matchups_with_season_summary[
        ['Game Matchup', 'start_date', 'team', 'total.wins', 'total.losses', 'home_points_season_mean', 'away_points_season_mean',
         'epa_per_game_offense_overall_avg_per_season', 'epa_per_game_defense_overall_avg_per_season',
         'offense_firstDowns', 'offense_thirdDownConversions', 'offense_totalYards',
         'offense_rushingYards', 'offense_rushingYards_average',
         'offense_netPassingYards', 'offense_passCompletion_Conversions_percent',
         'offense_passesIntercepted', 'offense_fumblesLost',
         'defense_sacks', 'defense_tacklesForLoss', 'defense_interceptions']]
    df_sel_col.sort_values(by=['start_date', 'Game Matchup'], ascending=[True, True], inplace=True)
    df = df_sel_col[df_sel_col['Game Matchup'].astype(str) != '0']

    num_rows = len(df)
    row_height = 30  # Adjust row height if needed
    header_height = 40
    total_height = header_height + (num_rows * row_height)

    # Create the table figure
    fig = go.Figure(data=[go.Table(
        header=dict(
            values=[col.replace('_', '<br>') for col in df.columns],  # Replaces '_' with line breaks
            font=dict(size=10),
            align="left"
        ),
        cells=dict(
            values=[df[col].tolist() for col in df.columns],
            align="left"
        )
    )])

    # Adjust the layout to match the height of the data
    fig.update_layout(
        height=total_height,  # Set figure height to accommodate all rows
        margin=dict(l=0, r=0, t=20, b=0)  # Optional: reduce margins
    )

    return fig

