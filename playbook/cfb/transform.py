import pandas as pd
import sqlite3
from datetime import date
from datetime import datetime
from .pregame import timestamp

def sqlite_query_table_by_year(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    #query = f"SELECT * FROM {table_name}"
    query = f"""
        SELECT t1.*
        FROM {table_name} t1
        JOIN (
            SELECT season, MAX(timestamp) AS max_timestamp
            FROM {table_name}
            GROUP BY season
        ) t2
        ON t1.season = t2.season AND t1.timestamp = t2.max_timestamp
    """
    df_table = pd.read_sql_query(query, conn)
    conn.close()
    return df_table

def sqlite_query_table(table_name):
    conn = sqlite3.connect('blitzanalytics.db')
    #query = f"SELECT * FROM {table_name}"
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE timestamp = (SELECT MAX(timestamp) FROM {table_name} )
        """
    df_table = pd.read_sql_query(query, conn)
    conn.close()
    return df_table

def insert_cfbd_to_sqlite(cfb_table_name,df_cfbd_data):
    conn = sqlite3.connect('blitzanalytics.db')

    if 'timestamp' not in df_cfbd_data.columns:
        df_cfbd_data['timestamp'] = timestamp
    df_cfbd_data.to_sql(cfb_table_name, conn, if_exists='replace', index=False)
    conn.close()

def season_stats(years):
    print('Transforming Season Stats')
    df_season_stats = sqlite_query_table('cfb_extract_season_stats')

    # Convert list to df with pivot table
    df_cfb_season_stats_all_original = df_season_stats.pivot(index=['team', 'season'], columns='statName', values='statValue').reset_index()
    #Rename the columns based on offense/defense/special teams
    df_cfb_season_stats_all_original.rename(columns = lambda col: f"offense_{col}"
                                                    if col in ("possessionTime", "firstDowns", "fourthDownConversions", "fourthDowns", "fumblesLost", "passAttempts",
                                                               "netPassingYards", "passesIntercepted", "passCompletions", "passingTDs", "rushingAttempts", "rushingTDs",
                                                               "rushingYards", "thirdDownConversions", "thirdDowns", "totalYards", "turnovers")
                                                    else col, inplace=True)
    df_cfb_season_stats_all_original.rename(columns=lambda col: f"defense_{col}"
                                                    if col in ("fumblesRecovered", "interceptionTDs", "interceptionYards", "interceptions", "tacklesForLoss", "sacks")
                                                    else col, inplace=True)
    df_cfb_season_stats_all_original.rename(columns=lambda col: f"specialteams_{col}"
                                                    if col in ("kickReturnTDs", "kickReturnYards", "kickReturns", "puntReturnTDs", "puntReturnYards", "puntReturns")
                                                    else col, inplace=True)
    df_cfb_season_stats_all_for_loop = df_cfb_season_stats_all_original.copy()
    list_df_cfb_season_stats_all_for_loop_by_year = []
    for year in years:
        df_cfb_season_stats_all_for_loop = df_cfb_season_stats_all_original.loc[df_cfb_season_stats_all_original['season'].astype(str).str.contains(str(year))]
        #Calculate Offense Stats
        #Possession Time
        df_cfb_season_stats_all_for_loop['offense_possessionTime_zscore'] = (df_cfb_season_stats_all_for_loop['offense_possessionTime'] - df_cfb_season_stats_all_for_loop['offense_possessionTime'].mean()) / df_cfb_season_stats_all_for_loop['offense_possessionTime'].std()
        #First Downs
        df_cfb_season_stats_all_for_loop['offense_firstDowns_zscore'] = (df_cfb_season_stats_all_for_loop['offense_firstDowns'] - df_cfb_season_stats_all_for_loop['offense_firstDowns'].mean()) / df_cfb_season_stats_all_for_loop['offense_firstDowns'].std()
        #Fourth Downs
        df_cfb_season_stats_all_for_loop['offense_fourthDownConversions_zscore'] = (df_cfb_season_stats_all_for_loop['offense_fourthDownConversions'] - df_cfb_season_stats_all_for_loop['offense_fourthDownConversions'].mean()) / df_cfb_season_stats_all_for_loop['offense_fourthDownConversions'].std()
        #Pass Attempts and Completions
        df_cfb_season_stats_all_for_loop['offense_passCompletions_zscore'] = (df_cfb_season_stats_all_for_loop['offense_passCompletions'] - df_cfb_season_stats_all_for_loop['offense_passCompletions'].mean()) / df_cfb_season_stats_all_for_loop['offense_passCompletions'].std()
        #Calculate Actual Pass Completion Percentage
        df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent'] = (df_cfb_season_stats_all_for_loop['offense_passCompletions'] / df_cfb_season_stats_all_for_loop['offense_passAttempts'])
        df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent_zscore'] = (df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent'] - df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent'].mean()) / df_cfb_season_stats_all_for_loop['offense_passCompletion_Conversions_percent'].std()
        #Rushing Attempts and Total Yards
        df_cfb_season_stats_all_for_loop['offense_rushingYards_zscore'] = (df_cfb_season_stats_all_for_loop['offense_rushingYards'] - df_cfb_season_stats_all_for_loop['offense_rushingYards'].mean()) / df_cfb_season_stats_all_for_loop['offense_rushingYards'].std()
        #Calculate Average Rushing Yards
        df_cfb_season_stats_all_for_loop['offense_rushingYards_average'] = (df_cfb_season_stats_all_for_loop['offense_rushingYards'] / df_cfb_season_stats_all_for_loop['offense_rushingAttempts'])
        df_cfb_season_stats_all_for_loop['offense_rushingYards_average_zscore'] = (df_cfb_season_stats_all_for_loop['offense_rushingYards_average'] - df_cfb_season_stats_all_for_loop['offense_rushingYards_average'].mean()) / df_cfb_season_stats_all_for_loop['offense_rushingYards_average'].std()
        #Third Downs and Third Down conversions
        df_cfb_season_stats_all_for_loop['offense_thirdDownConversions_zscore'] = (df_cfb_season_stats_all_for_loop['offense_thirdDownConversions'] - df_cfb_season_stats_all_for_loop['offense_thirdDownConversions'].mean()) / df_cfb_season_stats_all_for_loop['offense_thirdDownConversions'].std()
        #Totals and other stats
        df_cfb_season_stats_all_for_loop['offense_rushingTDs_zscore'] = (df_cfb_season_stats_all_for_loop['offense_rushingTDs'] - df_cfb_season_stats_all_for_loop['offense_rushingTDs'].mean()) / df_cfb_season_stats_all_for_loop['offense_rushingTDs'].std()
        df_cfb_season_stats_all_for_loop['offense_totalYards_zscore'] = (df_cfb_season_stats_all_for_loop['offense_totalYards'] - df_cfb_season_stats_all_for_loop['offense_totalYards'].mean()) / df_cfb_season_stats_all_for_loop['offense_totalYards'].std()
        df_cfb_season_stats_all_for_loop['offense_netPassingYards_zscore'] = (df_cfb_season_stats_all_for_loop['offense_netPassingYards'] - df_cfb_season_stats_all_for_loop['offense_netPassingYards'].mean()) / df_cfb_season_stats_all_for_loop['offense_netPassingYards'].std()
        df_cfb_season_stats_all_for_loop['offense_passingTDs_zscore'] = (df_cfb_season_stats_all_for_loop['offense_passingTDs'] - df_cfb_season_stats_all_for_loop['offense_passingTDs'].mean()) / df_cfb_season_stats_all_for_loop['offense_passingTDs'].std()
        #Calculate zscore for offensive stats that need to be subtracted (minus)
        df_cfb_season_stats_all_for_loop['offense_passesIntercepted_zscore_minus'] = (df_cfb_season_stats_all_for_loop['offense_passesIntercepted'] - df_cfb_season_stats_all_for_loop['offense_passesIntercepted'].mean()) / df_cfb_season_stats_all_for_loop['offense_passesIntercepted'].std()
        df_cfb_season_stats_all_for_loop['offense_fumblesLost_zscore_minus'] = (df_cfb_season_stats_all_for_loop['offense_fumblesLost'] - df_cfb_season_stats_all_for_loop['offense_fumblesLost'].mean()) / df_cfb_season_stats_all_for_loop['offense_fumblesLost'].std()
        df_cfb_season_stats_all_for_loop['offense_turnovers_zscore_minus'] = (df_cfb_season_stats_all_for_loop['offense_turnovers'] - df_cfb_season_stats_all_for_loop['offense_turnovers'].mean()) / df_cfb_season_stats_all_for_loop['offense_turnovers'].std()
        #Calculate zscore for Defense Stats
        df_cfb_season_stats_all_for_loop['defense_fumblesRecovered_zscore'] = (df_cfb_season_stats_all_for_loop['defense_fumblesRecovered'] - df_cfb_season_stats_all_for_loop['defense_fumblesRecovered'].mean()) / df_cfb_season_stats_all_for_loop['defense_fumblesRecovered'].std()
        df_cfb_season_stats_all_for_loop['defense_interceptionTDs_zscore'] = (df_cfb_season_stats_all_for_loop['defense_interceptionTDs'] - df_cfb_season_stats_all_for_loop['defense_interceptionTDs'].mean()) / df_cfb_season_stats_all_for_loop['defense_interceptionTDs'].std()
        df_cfb_season_stats_all_for_loop['defense_interceptionYards_zscore'] = (df_cfb_season_stats_all_for_loop['defense_interceptionYards'] - df_cfb_season_stats_all_for_loop['defense_interceptionYards'].mean()) / df_cfb_season_stats_all_for_loop['defense_interceptionYards'].std()
        df_cfb_season_stats_all_for_loop['defense_interceptions_zscore'] = (df_cfb_season_stats_all_for_loop['defense_interceptions'] - df_cfb_season_stats_all_for_loop['defense_interceptions'].mean()) / df_cfb_season_stats_all_for_loop['defense_interceptions'].std()
        df_cfb_season_stats_all_for_loop['defense_tacklesForLoss_zscore'] = (df_cfb_season_stats_all_for_loop['defense_tacklesForLoss'] - df_cfb_season_stats_all_for_loop['defense_tacklesForLoss'].mean()) / df_cfb_season_stats_all_for_loop['defense_tacklesForLoss'].std()
        df_cfb_season_stats_all_for_loop['sacks_zscore'] = (df_cfb_season_stats_all_for_loop['defense_sacks'] - df_cfb_season_stats_all_for_loop['defense_sacks'].mean()) / df_cfb_season_stats_all_for_loop['defense_sacks'].std()
        #Calculate zscore for special teams stats
        df_cfb_season_stats_all_for_loop['specialteams_kickReturnTDs_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_kickReturnTDs'] - df_cfb_season_stats_all_for_loop['specialteams_kickReturnTDs'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_kickReturnTDs'].std()
        df_cfb_season_stats_all_for_loop['specialteams_kickReturnYards_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_kickReturnYards'] - df_cfb_season_stats_all_for_loop['specialteams_kickReturnYards'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_kickReturnYards'].std()
        df_cfb_season_stats_all_for_loop['specialteams_kickReturns_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_kickReturns'] - df_cfb_season_stats_all_for_loop['specialteams_kickReturns'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_kickReturns'].std()
        df_cfb_season_stats_all_for_loop['specialteams_puntReturnTDs_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_puntReturnTDs'] - df_cfb_season_stats_all_for_loop['specialteams_puntReturnTDs'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_puntReturnTDs'].std()
        df_cfb_season_stats_all_for_loop['specialteams_puntReturnYards_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_puntReturnYards'] - df_cfb_season_stats_all_for_loop['specialteams_puntReturnYards'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_puntReturnYards'].std()
        df_cfb_season_stats_all_for_loop['specialteams_puntReturns_zscore'] = (df_cfb_season_stats_all_for_loop['specialteams_puntReturns'] - df_cfb_season_stats_all_for_loop['specialteams_puntReturns'].mean()) / df_cfb_season_stats_all_for_loop['specialteams_puntReturns'].std()
        #Fill NA with 0 and Sum zscore columns
        df_cfb_season_stats_all_for_loop.fillna(0,inplace=True)
        df_cfb_season_stats_all_for_loop['offense_plus_zscore_sum'] = df_cfb_season_stats_all_for_loop.filter(regex='offense_[a-zA-Z]+_zscore').sum(axis=1)
        df_cfb_season_stats_all_for_loop['offense_minus_zscore_sum'] = df_cfb_season_stats_all_for_loop.filter(regex='offense_[a-zA-Z]+_zscore_minus').sum(axis=1)
        df_cfb_season_stats_all_for_loop['offense_zscore_final'] = df_cfb_season_stats_all_for_loop['offense_plus_zscore_sum'] - df_cfb_season_stats_all_for_loop['offense_minus_zscore_sum']
        df_cfb_season_stats_all_for_loop['defense_zscore_final'] = df_cfb_season_stats_all_for_loop.filter(regex='defense_[a-zA-Z]+_zscore').sum(axis=1)
        df_cfb_season_stats_all_for_loop['specialteams_zscore_final'] = df_cfb_season_stats_all_for_loop.filter(regex='specialteams_[a-zA-Z]+_zscore').sum(axis=1)
        df_cfb_season_stats_all_for_loop['total_zscore'] = df_cfb_season_stats_all_for_loop['offense_zscore_final'] + df_cfb_season_stats_all_for_loop['defense_zscore_final'] + df_cfb_season_stats_all_for_loop['specialteams_zscore_final']
        list_df_cfb_season_stats_all_for_loop_by_year.append(df_cfb_season_stats_all_for_loop)
    df_cfb_season_stats_all = pd.concat(list_df_cfb_season_stats_all_for_loop_by_year)

    #Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_season_stats', df_cfb_season_stats_all)

def games_and_stats():
    print('Transforming Game Matchups')
    df_cfb_team_info = sqlite_query_table('cfb_extract_team_info')
    df_cfb_season_games_all = sqlite_query_table_by_year('cfb_extract_season_games')
    # Clean up Team Info Data
    df_cfb_teaminfo_drop = df_cfb_team_info.dropna(subset=['conference'])
    df_select_col_cfb_teaminfo = df_cfb_teaminfo_drop[["id", "school", "conference", "location.venue_id","location.name","location.zip"]]

    #Add Columns for Game Matchup and Date without timestamps
    df_cfb_season_games_all["Game Matchup"] = df_cfb_season_games_all[['away_team', 'home_team']].apply(" @ ".join, axis=1)
    df_cfb_season_games_all['start_date'] = df_cfb_season_games_all['start_date'].str.replace('.000Z', '')
    df_cfb_season_games_all['start_date'] = pd.to_datetime(df_cfb_season_games_all['start_date'])
    df_cfb_season_games_all["date"] = df_cfb_season_games_all["start_date"].dt.date
    cfb_season_games_all_date_col = df_cfb_season_games_all['date']
    df_cfb_season_games_all.drop(labels=['date'], axis=1, inplace=True)
    df_cfb_season_games_all.insert(6, 'date', cfb_season_games_all_date_col)
    df_cfb_season_games_all["Season + Week"] = df_cfb_season_games_all["season"].astype(str) + "_" + df_cfb_season_games_all["week"].astype(str)

    #Split the home v away into 2 df
    df_cfb_season_games_all_home = df_cfb_season_games_all[["id", "Game Matchup", "season", "season_type", "week", "start_date", "date", "conference_game", "home_team", "home_conference", "home_points"]]
    df_cfb_season_games_all_home.rename(columns={"home_team": "team", "home_conference": "conference","home_points": "points"},inplace=True)
    df_cfb_season_games_all_home.insert(7, "home_vs_away", 'home')
    df_cfb_season_games_all_away = df_cfb_season_games_all[["id", "Game Matchup", "season", "season_type", "week", "start_date","date", "conference_game", "away_team", "away_conference", "away_points"]]
    df_cfb_season_games_all_away.rename(columns={"away_team": "team", "away_conference": "conference", "away_points": "points"},inplace=True)
    df_cfb_season_games_all_away.insert(7, "home_vs_away", 'away')

    #Merge home and away df back together and sort them into order
    df_cfb_season_games_all_append = pd.concat([df_cfb_season_games_all_home, df_cfb_season_games_all_away])
    df_cfb_season_games_all_append.sort_values(by=['start_date','id'], inplace=True, ascending=True)

    #Select Columns from original dataframe cfb_season_games_all to join onto updated dataframe. This will include more home and away info
    df_cfb_season_games_original_sel_col = df_cfb_season_games_all[['id', 'home_team', 'home_points', 'home_line_scores', 'away_team', 'away_points', 'away_line_scores']]
    df_cfb_season_games_all_append_and_original_sel_col_joined = pd.merge(df_cfb_season_games_all_append,
                                                          df_cfb_season_games_original_sel_col,
                                                          left_on='id', right_on='id', how='left')
    #Rename the dataframe and fill NA rows
    df_cfb_season_games_all_updated = df_cfb_season_games_all_append_and_original_sel_col_joined
    df_cfb_season_games_all_updated.fillna(0, inplace=True)
    #df_cfb_season_games_all_updated['points'].replace('None', '0').astype(float)
    df_cfb_season_games_all_updated['points'].astype(float).astype(int)

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_season_games_stats_updated', df_cfb_season_games_all_updated)
    insert_cfbd_to_sqlite('cfb_transform_season_games_stats_all', df_cfb_season_games_all)

def games_and_aggregate_scores():
    print('Transforming Home and Away Aggregate Scores')
    df_cfb_season_games_all = sqlite_query_table_by_year('cfb_extract_season_games')

    #Transform average scores for home and away
    #Transform Home game scores
    df_cfb_season_games_home_group_scores = df_cfb_season_games_all[['home_team', 'home_points', 'season']]
    df_cfb_season_games_home_group_scores = df_cfb_season_games_home_group_scores.rename(columns={"home_team": "team"})
    df_cfb_season_games_home_group_scores_grouped_by_season = df_cfb_season_games_home_group_scores.groupby(['team','season']).agg(home_points_season_mean = ('home_points','mean'), home_points_season_max = ('home_points', 'max'), home_points_season_min = ('home_points', 'min')).reset_index()
    df_cfb_season_games_home_group_scores_grouped_by_total_years = df_cfb_season_games_home_group_scores.groupby(['team']).agg(home_points_mean_over_the_years = ('home_points','mean'), home_points_max_over_the_years = ('home_points', 'max'), home_points_min_over_the_years = ('home_points', 'min')).reset_index()
    df_cfb_season_games_home_agg_scores_merged = pd.merge(df_cfb_season_games_home_group_scores_grouped_by_season, df_cfb_season_games_home_group_scores_grouped_by_total_years, left_on='team', right_on='team', how='left')

    #Transform Away game scores
    df_cfb_season_games_away_group_scores = df_cfb_season_games_all[['away_team', 'away_points', 'season']]
    df_cfb_season_games_away_group_scores = df_cfb_season_games_away_group_scores.rename(columns={"away_team": "team"})
    df_cfb_season_games_away_group_scores_grouped_by_season = df_cfb_season_games_away_group_scores.groupby(['team','season']).agg(away_points_season_mean = ('away_points','mean'), away_points_season_max = ('away_points', 'max'), away_points_season_min = ('away_points', 'min')).reset_index()
    df_cfb_season_games_away_group_scores_grouped_by_total_years = df_cfb_season_games_away_group_scores.groupby(['team']).agg(away_points_mean_over_the_years = ('away_points','mean'), away_points_max_over_the_years = ('away_points', 'max'), away_points_min_over_the_years = ('away_points', 'min')).reset_index()
    df_cfb_season_games_away_agg_scores_merged = pd.merge(df_cfb_season_games_away_group_scores_grouped_by_season, df_cfb_season_games_away_group_scores_grouped_by_total_years, left_on='team', right_on='team', how='left')
    #Transform Merge Home and Away scores together
    df_cfb_season_games_agg_scores = pd.merge(df_cfb_season_games_home_agg_scores_merged, df_cfb_season_games_away_agg_scores_merged, left_on=['team','season'], right_on=['team','season'], how='left')

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_season_games_agg_scores', df_cfb_season_games_agg_scores)

def odds():
    print('Transforming Odds/Spread')
    df_cfb_odds_per_game_all = sqlite_query_table_by_year('cfb_extract_odds_per_game')
    df_cfb_season_games_all = sqlite_query_table_by_year('cfb_extract_season_games')

    #Transform odds per game
    #Prep the odds data
    df_cfb_odds_per_game_rename = df_cfb_odds_per_game_all.rename(columns={"gameId": "id", "homeWinProb": "home_team_WinProb" })
    df_cfb_odds_per_game_all_select_col = df_cfb_odds_per_game_rename.drop(columns=['season', 'week', 'homeTeam', 'awayTeam','seasonType'])
    df_cfb_season_games_all_for_odds = df_cfb_season_games_all[['id','season','week','home_team', 'home_points', 'away_team', 'away_points']]

    #Join the odds data on to the existing season games all data from above and rename it
    df_cfb_season_games_all_updated_odds_per_game_join = pd.merge(df_cfb_season_games_all_for_odds, df_cfb_odds_per_game_all_select_col, left_on=['id'],right_on=['id'], how='left')
    df_cfb_season_games_odds = df_cfb_season_games_all_updated_odds_per_game_join

    #Calculate the game point difference between to compare against the spread
    df_cfb_season_games_odds['game_point_diff'] = df_cfb_season_games_odds['away_points'] - df_cfb_season_games_odds['home_points']

    #Determine if the home team covered the spread with text and with an integer for additional analytics
    df_cfb_season_games_odds['home_team_result_of_the_spread'] = 'no result'
    df_cfb_season_games_odds.loc[df_cfb_season_games_odds['game_point_diff'] < df_cfb_season_games_odds['spread'],'home_team_result_of_the_spread'] = 'covered the spread'
    df_cfb_season_games_odds.loc[df_cfb_season_games_odds['game_point_diff'] == df_cfb_season_games_odds['spread'],'home_team_result_of_the_spread'] = 'tied the spread'
    df_cfb_season_games_odds.loc[df_cfb_season_games_odds['game_point_diff'] > df_cfb_season_games_odds['spread'],'home_team_result_of_the_spread'] = 'failed to cover the spread'
    df_cfb_season_games_odds['home_team_result_of_the_spread_int'] = '0'
    df_cfb_season_games_odds['home_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("covered the spread", case=False, na=False)] = '1'
    df_cfb_season_games_odds['home_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("tied the spread", case=False, na=False)] = '0'
    df_cfb_season_games_odds['home_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("failed to cover the spread", case=False, na=False)] = '0'

    # Determine if the away team covered the spread with text and with an integer for additional analytics
    df_cfb_season_games_odds['away_team_result_of_the_spread'] = 'no result'
    df_cfb_season_games_odds['away_team_result_of_the_spread'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("covered the spread", case=False, na=False)] = 'failed to cover the spread'
    df_cfb_season_games_odds['away_team_result_of_the_spread'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("tied the spread", case=False, na=False)] = 'tied the spread'
    df_cfb_season_games_odds['away_team_result_of_the_spread'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("failed to cover the spread", case=False, na=False)] = 'covered the spread'
    df_cfb_season_games_odds['away_team_result_of_the_spread_int'] = '0'
    df_cfb_season_games_odds['away_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("covered the spread", case=False, na=False)] = '0'
    df_cfb_season_games_odds['away_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("tied the spread", case=False, na=False)] = '0'
    df_cfb_season_games_odds['away_team_result_of_the_spread_int'].loc[df_cfb_season_games_odds['home_team_result_of_the_spread'].str.contains("failed to cover the spread", case=False, na=False)] = '1'

    #Make the result of the spread an integer
    df_cfb_season_games_odds_astype = df_cfb_season_games_odds.astype({"away_team_result_of_the_spread_int": int,"home_team_result_of_the_spread_int": int })

    #Drop any row with null data in the spread column
    df_cfb_season_games_odds_drop_na = df_cfb_season_games_odds_astype[df_cfb_season_games_odds_astype['spread'].notnull()]

    #Calculate the average and total spread by year for the home team using group bys
    df_cfb_season_games_odds_groupby_home = df_cfb_season_games_odds_drop_na.groupby(['home_team', 'season']).agg(home_team_average_number_of_times_covered_the_spread_per_year = ('home_team_result_of_the_spread_int','mean'), home_team_number_of_times_covered_the_spread_per_year = ('home_team_result_of_the_spread_int', 'sum')).round(2).reset_index()
    df_cfb_season_games_odds_groupby_home["home_team_average_spread_covered_by_year"] = df_cfb_season_games_odds_groupby_home[['season', 'home_team_average_number_of_times_covered_the_spread_per_year']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_games_odds_groupby_home["home_team_total_spread_covered_by_year"] = df_cfb_season_games_odds_groupby_home[['season', 'home_team_number_of_times_covered_the_spread_per_year']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_games_odds_groupby_combined_rows_home = df_cfb_season_games_odds_groupby_home.groupby('home_team')[['home_team_average_spread_covered_by_year','home_team_total_spread_covered_by_year']].agg(", ".join).reset_index()
    df_cfb_season_games_odds_groupby_combined_rows_home['home_team_average_spread_covered_by_year'] = 'Spread AVG While Home: ' + df_cfb_season_games_odds_groupby_combined_rows_home['home_team_average_spread_covered_by_year']
    df_cfb_season_games_odds_groupby_combined_rows_home['home_team_total_spread_covered_by_year'] = 'Spread Covered While Home: ' + df_cfb_season_games_odds_groupby_combined_rows_home['home_team_total_spread_covered_by_year']
    df_cfb_season_games_odds_groupby_combined_rows_home["home_vs_away"] = 'home'

    # Calculate the average and total spread by year for the away team using groupbys
    df_cfb_season_games_odds_groupby_away = df_cfb_season_games_odds_drop_na.groupby(['away_team', 'season']).agg(away_team_average_number_of_times_covered_the_spread_per_year = ('away_team_result_of_the_spread_int','mean'), away_team_number_of_times_covered_the_spread_per_year = ('away_team_result_of_the_spread_int', 'sum')).round(2).reset_index()
    df_cfb_season_games_odds_groupby_away["away_team_average_spread_covered_by_year"] = df_cfb_season_games_odds_groupby_away[['season', 'away_team_average_number_of_times_covered_the_spread_per_year']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_games_odds_groupby_away["away_team_total_spread_covered_by_year"] = df_cfb_season_games_odds_groupby_away[['season', 'away_team_number_of_times_covered_the_spread_per_year']].astype(str).apply(" : ".join,axis=1)
    df_cfb_season_games_odds_groupby_combined_rows_away = df_cfb_season_games_odds_groupby_away.groupby('away_team')[['away_team_average_spread_covered_by_year','away_team_total_spread_covered_by_year']].agg(", ".join).reset_index()
    df_cfb_season_games_odds_groupby_combined_rows_away['away_team_average_spread_covered_by_year'] = 'Spread AVG While Away: ' + df_cfb_season_games_odds_groupby_combined_rows_away['away_team_average_spread_covered_by_year']
    df_cfb_season_games_odds_groupby_combined_rows_away['away_team_total_spread_covered_by_year'] = 'Spread Covered While Away: ' + df_cfb_season_games_odds_groupby_combined_rows_away['away_team_total_spread_covered_by_year']
    df_cfb_season_games_odds_groupby_combined_rows_away["home_vs_away"] = 'away'

    #Join the home team calculated spread data on to the original odds data, then rename and drop columns for upcoming appending
    df_cfb_season_games_odds_join_groupby_combined_rows_home = pd.merge(df_cfb_season_games_odds_drop_na, df_cfb_season_games_odds_groupby_combined_rows_home, left_on=['home_team'], right_on=['home_team'], how='left')
    df_cfb_season_games_odds_join_groupby_combined_rows_home_rename = df_cfb_season_games_odds_join_groupby_combined_rows_home.rename(columns={"home_team": "team", "home_points": "points",
                                                                                                                                               "home_team_result_of_the_spread": "result_of_the_spread", "home_team_average_spread_covered_by_year": "average_spread_covered_by_year",
                                                                                                                                                "home_team_total_spread_covered_by_year": "total_spread_covered_by_year" })
    df_cfb_season_games_odds_join_groupby_combined_rows_home_rename_drop = df_cfb_season_games_odds_join_groupby_combined_rows_home_rename.loc[:, ~df_cfb_season_games_odds_join_groupby_combined_rows_home_rename.columns.str.contains('^away_', case=False)].drop(columns=['home_team_result_of_the_spread_int'])

    #Join the away team calculated spread data on to the original odds data, then rename and drop columns for upcoming appending
    df_cfb_season_games_odds_join_groupby_combined_rows_away = pd.merge(df_cfb_season_games_odds_drop_na, df_cfb_season_games_odds_groupby_combined_rows_away, left_on=['away_team'], right_on=['away_team'], how='left')
    df_cfb_season_games_odds_join_groupby_combined_rows_away_rename = df_cfb_season_games_odds_join_groupby_combined_rows_away.rename(columns={"away_team": "team", "away_points": "points",
                                                                                                                                               "away_team_result_of_the_spread": "result_of_the_spread", "away_team_average_spread_covered_by_year": "average_spread_covered_by_year",
                                                                                                                                                "away_team_total_spread_covered_by_year": "total_spread_covered_by_year","home_vs_away": "h_vs_a" })
    df_cfb_season_games_odds_join_groupby_combined_rows_away_rename_drop = df_cfb_season_games_odds_join_groupby_combined_rows_away_rename.loc[:, ~df_cfb_season_games_odds_join_groupby_combined_rows_away_rename.columns.str.contains('^home_', case=False)].drop(columns=['away_team_result_of_the_spread_int'])
    df_cfb_season_games_odds_join_groupby_combined_rows_away_rename_drop = df_cfb_season_games_odds_join_groupby_combined_rows_away_rename_drop.rename(columns={"h_vs_a": "home_vs_away" })

    #Append the away odds data with spread calculations onto the home odds data with spread calculations and sort
    df_cfb_season_games_odds_append = pd.concat([df_cfb_season_games_odds_join_groupby_combined_rows_home_rename_drop, df_cfb_season_games_odds_join_groupby_combined_rows_away_rename_drop])
    df_cfb_season_games_odds_append.sort_values(by=['id'], inplace=True, ascending=True)

    #Group odds data for summmary view
    df_cfb_season_games_odds_groupby_home_for_summary = df_cfb_season_games_odds_groupby_home.rename(columns={"home_team": "team"})
    df_cfb_season_games_odds_groupby_away_for_summary = df_cfb_season_games_odds_groupby_away.rename(columns={"away_team": "team"})
    df_cfb_season_games_odds_groupby_join_home_and_away_for_summary = pd.merge(df_cfb_season_games_odds_groupby_home_for_summary, df_cfb_season_games_odds_groupby_away_for_summary,
                                                         left_on=['team', 'season'], right_on=['team', 'season'], how='left')
    df_cfb_season_games_odds_groupby_join_home_and_away_for_summary_drop = df_cfb_season_games_odds_groupby_join_home_and_away_for_summary.loc[:, ~df_cfb_season_games_odds_groupby_join_home_and_away_for_summary.columns.str.contains('by_year', case=False)]

    df_cfb_season_games_odds_for_summary = df_cfb_season_games_odds_groupby_join_home_and_away_for_summary_drop

    #Select on the odds columns needed for joining onto the main dataframe
    df_cfb_season_games_odds_append_sel_col = df_cfb_season_games_odds_append[['id','team','spread','home_team_WinProb','game_point_diff','result_of_the_spread', 'average_spread_covered_by_year','total_spread_covered_by_year',]]
    df_cfb_odds_per_game_with_calc = df_cfb_season_games_odds_append_sel_col

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_odds_per_game_with_calc', df_cfb_odds_per_game_with_calc)
    insert_cfbd_to_sqlite('cfb_transform_odds_for_summary', df_cfb_season_games_odds_for_summary)

def epa():
    df_cfb_epa_per_game_all = sqlite_query_table_by_year('cfb_extract_epa')
    print('Transforming EPA')
    #Transform EPA
    df_cfb_epa_per_game_all_rename_col = df_cfb_epa_per_game_all.rename(columns={"gameId": "id"})
    df_cfb_epa_per_game_all_rename_col.columns = df_cfb_epa_per_game_all_rename_col.columns.str.replace("^offense", "epa_per_game_offense", regex=True)
    df_cfb_epa_per_game_all_rename_col.columns = df_cfb_epa_per_game_all_rename_col.columns.str.replace("^defense", "epa_per_game_defense", regex=True)
    df_cfb_epa_per_game_all_rename_col_with_epa = df_cfb_epa_per_game_all_rename_col.loc[:,df_cfb_epa_per_game_all_rename_col.columns.str.contains('^epa_per_game', case=False)]
    column_names = df_cfb_epa_per_game_all_rename_col_with_epa.columns.values.tolist()
    df_cfb_epa_per_game_all_rename_col_looped = pd.DataFrame
    for column_name in column_names:
        df_cfb_epa_per_game_all_rename_col[column_name] = df_cfb_epa_per_game_all_rename_col[column_name].astype(float).round(2)

    df_cfb_epa_per_game = df_cfb_epa_per_game_all_rename_col

    df_cfb_epa_per_game_all_rename_col_groupby = df_cfb_epa_per_game_all_rename_col.groupby(['team', 'season']).agg(epa_per_game_offense_overall_avg_per_season = ('epa_per_game_offense.overall', 'mean'),
                                                                                                                    epa_per_game_defense_overall_avg_per_season = ('epa_per_game_defense.overall', 'mean')).round(2).reset_index()
    df_cfb_epa_per_season_for_summary = df_cfb_epa_per_game_all_rename_col_groupby

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_epa_per_game', df_cfb_epa_per_game)
    insert_cfbd_to_sqlite('cfb_transform_epa_per_season_for_summary', df_cfb_epa_per_season_for_summary)

def polls():
    df_cfb_ranking_all = sqlite_query_table_by_year('cfb_extract_rankings')

    print('Transforming Polls/Rankings')
    df_cfb_ranking_all_rm_null_ap = df_cfb_ranking_all[df_cfb_ranking_all['AP Top 25'].notnull()]
    df_cfb_ranking_all_rename = df_cfb_ranking_all_rm_null_ap.rename(columns={"school": "team"})
    df_cfb_ranking_all_drop = df_cfb_ranking_all_rename.drop(columns=['AFCA Division II Coaches Poll','AFCA Division III Coaches Poll','FCS Coaches Poll'], errors='ignore')
    df_cfb_ranking_all_drop['AP Top 25'] = df_cfb_ranking_all_drop['AP Top 25'].astype(int).astype(str)
    df_cfb_ranking_all_drop['Week with prefix'] = 'w' + df_cfb_ranking_all_drop['week'].astype(str)
    df_cfb_ranking_all_drop["AP Top 25 by Week"] = df_cfb_ranking_all_drop[
        ['Week with prefix', 'AP Top 25']].astype(str).apply(":".join, axis=1)
    df_cfb_ranking_groupby_ap = df_cfb_ranking_all_drop.groupby(['team', 'season'])['AP Top 25 by Week'].agg(", ".join).reset_index()
    df_cfb_ranking_all_updated = df_cfb_ranking_all_drop

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_rankings_groupby_ap', df_cfb_ranking_groupby_ap)
    insert_cfbd_to_sqlite('cfb_transform_rankings_all_updated', df_cfb_ranking_all_updated)


def team_records():
    print('Transforming Team Records')
    df_cfb_team_record_all = sqlite_query_table_by_year('cfb_extract_team_records')

    #Transform Team Records
    #df_cfb_team_record_all_rename = df_cfb_team_record_all.rename(columns={"year": "season"})
    df_cfb_team_record_all_select_col = df_cfb_team_record_all[["team", "season", "total.wins", "total.losses", "conferenceGames.wins", "conferenceGames.losses"]]

    #Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_team_record',  df_cfb_team_record_all_select_col)

def stats_per_game():
    print('Transforming Stats per game')
    df_cfb_stats_per_game_all = sqlite_query_table_by_year('cfb_extract_stats_per_game')

    #Transform Stats per Game
    df_cfb_stats_per_game_rename = df_cfb_stats_per_game_all.rename(columns={"gameId": "id"})
    df_cfb_stats_per_game = df_cfb_stats_per_game_rename.drop(columns=['opponent'])

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_stats_per_game', df_cfb_stats_per_game)

def team_info():
    df_cfb_team_info = sqlite_query_table('cfb_extract_team_info')

    df_cfb_team_info_rename = df_cfb_team_info.rename(columns={"school": "team"})
    df_cfb_team_info_updated = df_cfb_team_info_rename.loc[df_cfb_team_info_rename['classification'].str.contains("fbs|fcs", case=False, na=False)]

    #Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_reporting_team_info', df_cfb_team_info_updated)


def reporting_week(arg_report_week):
    print('Calculating reporting week')
    df_cfb_season_games_all = sqlite_query_table_by_year('cfb_transform_season_games_stats_all')
    date_today = datetime.combine(date.today(), datetime.min.time())
    date_today_day = date.today().strftime('%A')

    df_cfb_date_group_bys = df_cfb_season_games_all.groupby(['season', 'week'])['date'].last().reset_index()

    df_cfb_date_group_bys['date'] = pd.to_datetime(df_cfb_date_group_bys['date'])

    date_compare = (df_cfb_date_group_bys["date"].shift() < date_today) & (df_cfb_date_group_bys["date"] > date_today)
    df_date_compare_result = df_cfb_date_group_bys[date_compare]
    current_week = df_date_compare_result['week'].to_string(index=False)
    return (current_week)

def reporting_year(arg_report_year):
    print('Calculating reporting year')
    if arg_report_year is not None:
        report_year = arg_report_year
        return (report_year)
    else:
        report_year = date.today().year
        return (report_year)

def combine_data_for_summary(reporting_year):
    print('Transforming Summary Dataset')
    # CFB Seasons Stats zscores for summary
    df_cfb_season_stats_all = sqlite_query_table('cfb_transform_season_stats')
    df_cfb_season_games_agg_scores = sqlite_query_table('cfb_transform_season_games_agg_scores')
    df_cfb_team_record_all_select_col = sqlite_query_table('cfb_transform_team_record')
    df_cfb_ranking_groupby_ap = sqlite_query_table('cfb_transform_rankings_groupby_ap')
    df_cfb_epa_per_season_for_summary = sqlite_query_table('cfb_transform_epa_per_season_for_summary')


    df_cfb_season_stats_zscores_for_summary = df_cfb_season_stats_all[[
        'team', 'season', 'games', 'offense_plus_zscore_sum', 'offense_minus_zscore_sum', 'offense_zscore_final',
        'defense_zscore_final', 'specialteams_zscore_final', 'total_zscore']]

    #CFB Season Games Score Calculation for summary
    df_cfb_season_games_agg_scores_for_summary = df_cfb_season_games_agg_scores[['team','season','home_points_season_mean','home_points_mean_over_the_years','away_points_season_mean','away_points_mean_over_the_years']]

    #CFB Team Wins and Losses by Year for summary
    df_cfb_team_record_all_select_col_for_summary = df_cfb_team_record_all_select_col

    #CFB Top 25 Ranking for summary
    df_cfb_ranking_for_summary = df_cfb_ranking_groupby_ap

    # CFB Join dataframes for summary
    cfb_summary_join_record_and_rankings = pd.merge(df_cfb_team_record_all_select_col_for_summary,
                                                    df_cfb_ranking_for_summary,
                                                    left_on=['team', 'season'],
                                                    right_on=['team', 'season'], how='left')
    cfb_summary_join_record_rank_and_agg_scores = pd.merge(cfb_summary_join_record_and_rankings,
                                                           df_cfb_season_games_agg_scores_for_summary,
                                                           left_on=['team', 'season'],
                                                           right_on=['team', 'season'], how='left')
    cfb_summary_join_record_rank_agg_and_zscores_scores = pd.merge(cfb_summary_join_record_rank_and_agg_scores,
                                                                   df_cfb_season_stats_zscores_for_summary,
                                                                   left_on=['team', 'season'],
                                                                   right_on=['team', 'season'], how='left')
    cfb_summary_join_record_rank_agg_zscores_epa = pd.merge(cfb_summary_join_record_rank_agg_and_zscores_scores,
                                                            df_cfb_epa_per_season_for_summary,
                                                            left_on=['team', 'season'],
                                                            right_on=['team', 'season'], how='left')
    cfb_summary_all_joins = cfb_summary_join_record_rank_agg_zscores_epa.sort_values(by=['team', 'season'], ascending=True, na_position='first')

    cfb_summary_all_joins_loc = cfb_summary_all_joins.loc[
        ~cfb_summary_all_joins['season'].astype(str).str.contains(str(reporting_year), regex=False, case=False, na=False)]
    cfb_summary_all_joins_loc_groupby = cfb_summary_all_joins_loc.groupby('team')["season"].count().reset_index()
    cfb_summary_all_joins_loc_groupby['season'] = str(reporting_year)
    cfb_summary_all_joins_loc_groupby_merged = pd.concat([cfb_summary_all_joins, cfb_summary_all_joins_loc_groupby])
    cfb_summary_all_joins_loc_groupby_merged_fillna = cfb_summary_all_joins_loc_groupby_merged.fillna(0)
    cfb_summary_join_record_rank_agg_zscores_epa_sorted = cfb_summary_all_joins_loc_groupby_merged_fillna.sort_values(by=['team', 'season'], ascending=True, na_position='first')

    cfb_summary = cfb_summary_join_record_rank_agg_zscores_epa_sorted.fillna(0)

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_reporting_summary', cfb_summary)

def prep_data_for_reporting():
    def remove_df_timestamp(df):
        df_without_timestamp = df.loc[:, ~df.columns.str.startswith('timestamp')]
        return(df_without_timestamp)
    def remove_df_season(df):
        df_without_season_ = df.loc[:, ~df.columns.str.startswith('season_y')]
        df_renamed = df_without_season_.rename(columns={"season_x": "season"})
        return(df_renamed)

    print('Transforming datasets for loading')
    df_cfb_season_stats_all = remove_df_timestamp(sqlite_query_table('cfb_transform_season_stats'))
    df_cfb_season_games_all_updated = remove_df_timestamp(sqlite_query_table('cfb_transform_season_games_stats_updated'))
    df_cfb_season_games_agg_scores = remove_df_timestamp(sqlite_query_table('cfb_transform_season_games_agg_scores'))
    df_cfb_team_record_all_select_col = remove_df_timestamp(sqlite_query_table('cfb_transform_team_record'))
    df_cfb_ranking_all_updated = remove_df_timestamp(sqlite_query_table('cfb_transform_rankings_all_updated'))
    df_cfb_epa_per_game = remove_df_timestamp(sqlite_query_table('cfb_transform_epa_per_game'))
    df_cfb_stats_per_game = remove_df_timestamp(sqlite_query_table('cfb_transform_stats_per_game'))
    df_cfb_season_games_all = remove_df_timestamp(sqlite_query_table('cfb_transform_season_games_stats_all'))
    df_cfb_odds_per_game_with_calc = remove_df_timestamp(sqlite_query_table('cfb_transform_odds_per_game_with_calc'))

    #Transform df's with stats and merge on games
    df_cfb_games_and_stats = pd.merge(df_cfb_season_games_all_updated, df_cfb_season_stats_all,
                                      left_on=['team','season'], right_on=['team','season'], how='left')

    #Transform merge (games and stats) with (agg scores)
    df_cfb_games_stats_agg_scores = pd.merge(df_cfb_games_and_stats, df_cfb_season_games_agg_scores,
                                             left_on=['team','season'], right_on=['team','season'], how='left')

    #Transform Join Coach Poll / Rankings with Games/Stats/Agg Scores df
    df_cfb_games_stats_agg_scores_rankings = pd.merge(df_cfb_games_stats_agg_scores,df_cfb_ranking_all_updated ,
                                                      left_on=['team','week','season'],right_on=['team','week','season'], how='left', suffixes=('_x', '_y'))

    #Transform Join Rankings/Games/Stats/Agg Scores with Records
    df_cfb_games_stats_agg_scores_rankings_team_records = pd.merge(df_cfb_games_stats_agg_scores_rankings, df_cfb_team_record_all_select_col,
                                                                   left_on=['team','season'],right_on=['team','season'], how='left')

    #Transform Join EPA per Game on Rankings/Games/Stats/Agg Scores with Records
    df_cfb_epa_per_game_all_select_col = df_cfb_epa_per_game.drop(
        columns=['season', 'week', 'conference', 'opponent'])
    df_cfb_games_stats_agg_scores_rankings_team_records_epa = pd.merge(df_cfb_games_stats_agg_scores_rankings_team_records, df_cfb_epa_per_game_all_select_col,
        left_on=['id', 'team'], right_on=['id', 'team'], how='left')

    #Transform Join Rankings/Games/Stats/Agg Scores/EPA with Odds
    df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds = pd.merge(df_cfb_games_stats_agg_scores_rankings_team_records_epa, df_cfb_odds_per_game_with_calc,
        left_on=['id', 'team'], right_on=['id', 'team'], how='left')
    for col in df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds:
        # get dtype for column
        datatype = df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds[col].dtype
        # check if it is a number
        if datatype == int or datatype == float:
            df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds[col].fillna(0, inplace=True)
        else:
            df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds[col].fillna("No Data", inplace=True)


    #Transform Join Rankings/Games/Stats/Agg Scores/Records with Stats per game
    df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds_statspergame_org = pd.merge(df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds,
                                                                   df_cfb_stats_per_game,
                                                                   left_on=['team', 'week', 'id'],
                                                                   right_on=['team', 'week', 'id'], how='left')
    df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds_statspergame = remove_df_season(df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds_statspergame_org)

    #Transform Join Coach Poll / Rankings with Games/Stats/Agg Scores df
    df_cfb_season_games_all_updated_join_rankings = pd.merge(df_cfb_season_games_all_updated, df_cfb_ranking_all_updated,
                                                      left_on=['team', 'week', 'season'],
                                                      right_on=['team', 'week', 'season'], how='left')

    #Transform Join Game Matchups with Stats per game
    df_cfb_season_games_all_updated_join_stats_per_game = pd.merge(df_cfb_season_games_all_updated, df_cfb_stats_per_game,
                                                      left_on=['team', 'week', 'id'],
                                                      right_on=['team', 'week', 'id'], how='left')

    #General Game data joined with odds
    df_cfb_season_games_all_updated_join_odds = pd.merge(df_cfb_season_games_all_updated, df_cfb_odds_per_game_with_calc,
                                                        left_on=['id', 'team'], right_on=['id', 'team'], how='left')
    for col in df_cfb_season_games_all_updated_join_odds:
        # get dtype for column
        datatype = df_cfb_season_games_all_updated_join_odds[col].dtype
        # check if it is a number
        if datatype == int or datatype == float:
            df_cfb_season_games_all_updated_join_odds[col].fillna(0, inplace=True)
        else:
            df_cfb_season_games_all_updated_join_odds[col].fillna("No Data", inplace=True)

    #CFB Games/Matchups by Season and Week
    df_cfb_season_games_all['season'] = df_cfb_season_games_all['season'].astype(str)
    cfb_season_week_matchups = df_cfb_season_games_all
    cfb_season_week_matchups_home_updated = df_cfb_season_games_all_updated

    #CFB Season Games Score Calculation
    cfb_season_games_agg_scores = df_cfb_season_games_agg_scores
    cfb_season_games_agg_scores = cfb_season_games_agg_scores.fillna(0)

    #CFB Team Wins and Losses by Year
    cfb_team_record_by_year = df_cfb_team_record_all_select_col
    cfb_team_record_by_year = cfb_team_record_by_year.fillna(0)

    #CFB Games with odds/spread
    cfb_games_with_spread_analytics = df_cfb_season_games_all_updated_join_odds
    cfb_games_with_spread_analytics = cfb_games_with_spread_analytics.fillna(0)

    #CFB Games with all advanced stats
    cfb_season_stats_by_season = df_cfb_season_stats_all
    cfb_season_stats_by_season = cfb_season_stats_by_season.fillna(0)

    #CFB Stats per Game
    cfb_stats_per_game = df_cfb_stats_per_game
    cfb_stats_per_game = cfb_stats_per_game.fillna(0)

    #CFB Stats per Game with Matchup
    cfb_matchup_with_stats_per_game = df_cfb_season_games_all_updated_join_stats_per_game
    cfb_matchup_with_stats_per_game = cfb_matchup_with_stats_per_game.fillna(0)

    #CFB All Data
    df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds_statspergame['season'] = df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds_statspergame['season'].astype(str)
    cfb_all_data = df_cfb_games_stats_agg_scores_rankings_team_records_epa_odds_statspergame
    cfb_all_data = cfb_all_data.fillna(0)

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_reporting_all_data', cfb_all_data)
    insert_cfbd_to_sqlite('cfb_reporting_games_with_spread_analytics', cfb_games_with_spread_analytics)
    insert_cfbd_to_sqlite('cfb_reporting_season_stats_by_season', cfb_season_stats_by_season)
    insert_cfbd_to_sqlite('cfb_reporting_season_week_matchups', cfb_season_week_matchups)
    insert_cfbd_to_sqlite('cfb_reporting_season_week_matchups_home_updated', cfb_season_week_matchups_home_updated)
    insert_cfbd_to_sqlite('cfb_reporting_stats_per_game', cfb_stats_per_game)
    insert_cfbd_to_sqlite('cfb_reporting_matchup_with_stats_per_game', cfb_matchup_with_stats_per_game)
    insert_cfbd_to_sqlite('cfb_reporting_season_games_agg_scores', cfb_season_games_agg_scores)
    insert_cfbd_to_sqlite('cfb_reporting_team_record_by_years', cfb_team_record_by_year)
