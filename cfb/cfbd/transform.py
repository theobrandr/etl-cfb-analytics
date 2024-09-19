import pandas as pd
import sqlite3
from datetime import date
from datetime import datetime
from .pregame import timestamp

def sqlite_query_table_by_year(table_name):
    conn = sqlite3.connect('databases/cfb_cfbd.db')
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
    conn = sqlite3.connect('databases/cfb_cfbd.db')
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
    conn = sqlite3.connect('databases/cfb_cfbd.db')

    if 'timestamp' not in df_cfbd_data.columns:
        df_cfbd_data['timestamp'] = timestamp
    df_cfbd_data.to_sql(cfb_table_name, conn, if_exists='replace', index=False)
    conn.close()

def remove_df_timestamp(df):
    df_without_timestamp = df.loc[:, ~df.columns.str.startswith('timestamp')]
    return(df_without_timestamp)

def season_stats():
    print('Transforming Season Stats')
    df_season_stats = sqlite_query_table_by_year('cfb_extract_season_stats')

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
    df_cfb_season_stats_all_original_fillna = df_cfb_season_stats_all_original.fillna(0)

    df_cfb_years_to_transform = df_cfb_season_stats_all_original_fillna.groupby('season').size().reset_index(name='Count')
    years_to_transform = df_cfb_years_to_transform['season'].tolist()

    list_df_cfb_season_stats_all_for_loop_by_year = []
    for year in years_to_transform:
        df_cfb_season_stats_all_for_loop = df_cfb_season_stats_all_original_fillna.loc[df_cfb_season_stats_all_original_fillna['season'].astype(str).str.contains(str(year))]
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
    column_to_move = 'Game Matchup'
    df_cfb_season_games_all = df_cfb_season_games_all[[df_cfb_season_games_all.columns[0]] +
                                    [column_to_move] + [col for col in df_cfb_season_games_all.columns
                                            if col != df_cfb_season_games_all.columns[0] and col != column_to_move]]
    df_cfb_season_games_all['start_date'] = df_cfb_season_games_all['start_date'].str.replace('.000Z', '')
    df_cfb_season_games_all['start_date'] = pd.to_datetime(df_cfb_season_games_all['start_date'])
    df_cfb_season_games_all["date"] = df_cfb_season_games_all["start_date"].dt.date
    cfb_season_games_all_date_col = df_cfb_season_games_all['date']
    df_cfb_season_games_all.drop(labels=['date'], axis=1, inplace=True)
    df_cfb_season_games_all.insert(6, 'date', cfb_season_games_all_date_col)

    # Correct data types of original matchup columns
    df_cfb_season_games_all.fillna(0, inplace=True)
    columns_to_int_original_df = ['id', 'season', 'week', 'home_points', 'away_points']
    df_cfb_season_games_all[columns_to_int_original_df] = df_cfb_season_games_all[columns_to_int_original_df].apply(
        pd.to_numeric, errors='coerce')
    df_cfb_season_games_all[columns_to_int_original_df] = df_cfb_season_games_all[columns_to_int_original_df].astype(
        'float').astype('int')

    df_cfb_season_games_all['home_win_loss_calc'] = df_cfb_season_games_all['home_points'] - df_cfb_season_games_all['away_points']
    df_cfb_season_games_all['home_win_loss'] = df_cfb_season_games_all['home_win_loss_calc'].apply(
        lambda x: 'win' if x > 0 else ('loss' if x < 0 else 'No Data'))
    df_cfb_season_games_all['away_win_loss_calc'] = df_cfb_season_games_all['away_points'] - df_cfb_season_games_all['home_points']
    df_cfb_season_games_all['away_win_loss'] = df_cfb_season_games_all['away_win_loss_calc'].apply(
        lambda x: 'win' if x > 0 else ('loss' if x < 0 else 'No Data'))
    #df_cfb_season_games_all["Season + Week"] = df_cfb_season_games_all["season"].astype(str) + "_" + df_cfb_season_games_all["week"].astype(str)

    #Split the home v away into 2 df
    df_cfb_season_games_all_home = df_cfb_season_games_all[["id", "Game Matchup", "season", "season_type", "week", "start_date", "date", "conference_game", "home_team", "home_conference", "home_points", "home_line_scores", "home_win_loss"]]
    df_cfb_season_games_all_home.rename(columns={"home_team": "team", "home_conference": "conference", "home_points": "points", "home_line_scores": "box_score", "home_win_loss": "win_loss"},inplace=True)
    df_cfb_season_games_all_home.insert(7, "home_vs_away", 'home')
    df_cfb_season_games_all_away = df_cfb_season_games_all[["id", "Game Matchup", "season", "season_type", "week", "start_date","date", "conference_game", "away_team", "away_conference", "away_points", "away_line_scores", "away_win_loss"]]
    df_cfb_season_games_all_away.rename(columns={"away_team": "team", "away_conference": "conference", "away_points": "points", "away_line_scores": "box_score", "away_win_loss": "win_loss"},inplace=True)
    df_cfb_season_games_all_away.insert(7, "home_vs_away", 'away')

    #Merge home and away df back together and sort them into order
    df_cfb_season_games_all_append = pd.concat([df_cfb_season_games_all_home, df_cfb_season_games_all_away])
    df_cfb_season_games_all_append.sort_values(by=['start_date','id'], inplace=True, ascending=True)

    #Select Columns from original dataframe cfb_season_games_all to join onto updated dataframe. This will include more home and away info
    df_cfb_season_games_original_sel_col = df_cfb_season_games_all[['id', 'home_team', 'home_points', 'home_line_scores', 'home_win_loss', 'home_win_loss_calc', 'away_team', 'away_points', 'away_line_scores','away_win_loss', 'away_win_loss_calc' ]]
    df_cfb_season_games_all_append_and_original_sel_col_joined = pd.merge(df_cfb_season_games_all_append,
                                                          df_cfb_season_games_original_sel_col,
                                                          left_on='id', right_on='id', how='left')

    #Rename the dataframe and fill NA rows
    df_cfb_season_games_all_updated = df_cfb_season_games_all_append_and_original_sel_col_joined
    df_cfb_season_games_all_updated.fillna(0, inplace=True)
    columns_to_int = ['id', 'season', 'week', 'points']
    df_cfb_season_games_all_updated[columns_to_int] = df_cfb_season_games_all_updated[columns_to_int].apply(pd.to_numeric, errors='coerce')
    df_cfb_season_games_all_updated[columns_to_int] = df_cfb_season_games_all_updated[columns_to_int].astype('float').astype('int')

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_season_games_expand_matchup', df_cfb_season_games_all_updated)
    insert_cfbd_to_sqlite('cfb_transform_season_games_matchups', df_cfb_season_games_all)

def games_and_aggregate_scores():
    print('Transforming Home and Away Aggregate Scores')
    df_cfb_season_games_all = sqlite_query_table_by_year('cfb_extract_season_games')
    columns_to_check = df_cfb_season_games_all.drop(['notes', 'highlights'], axis=1).columns
    columns_with_none = columns_to_check[df_cfb_season_games_all[columns_to_check].isna().any()]
    df_cfb_season_games_all[columns_with_none] = df_cfb_season_games_all[columns_with_none].fillna(0)
    df_cfb_season_games_all[columns_with_none] = df_cfb_season_games_all[columns_with_none].astype('float32')
    df_cfb_season_games_all['season'] = df_cfb_season_games_all['season'].astype(int)

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
    df_cfb_season_games_agg_scores.fillna(0, inplace=True)
    df_cfb_season_games_agg_scores[df_cfb_season_games_agg_scores.select_dtypes(include=['number']).columns] = \
        df_cfb_season_games_agg_scores.select_dtypes(include=['number']).astype('int')

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_season_games_agg_scores', df_cfb_season_games_agg_scores)

def odds():
    print('Transforming Odds/Spread')
    df_cfb_odds_per_game_all = sqlite_query_table_by_year('cfb_extract_odds_per_game')
    df_cfb_season_games_all = sqlite_query_table_by_year('cfb_extract_season_games')
    columns_to_check = df_cfb_season_games_all.drop(['notes', 'highlights'], axis=1).columns
    columns_with_none = columns_to_check[df_cfb_season_games_all[columns_to_check].isna().any()]
    df_cfb_season_games_all[columns_with_none] = df_cfb_season_games_all[columns_with_none].fillna(0)
    df_cfb_season_games_all[columns_with_none] = df_cfb_season_games_all[columns_with_none].astype('float32')
    df_cfb_season_games_all['season'] = df_cfb_season_games_all['season'].astype(int)

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
    columns_to_int = ['id', 'season', 'week', 'points', 'spread', 'game_point_diff']
    df_cfb_season_games_odds_append[columns_to_int] = df_cfb_season_games_odds_append[columns_to_int].astype('int')

    #Group odds data for summmary view
    df_cfb_season_games_odds_groupby_home_for_summary = df_cfb_season_games_odds_groupby_home.rename(columns={"home_team": "team"})
    df_cfb_season_games_odds_groupby_away_for_summary = df_cfb_season_games_odds_groupby_away.rename(columns={"away_team": "team"})
    df_cfb_season_games_odds_groupby_join_home_and_away_for_summary = pd.merge(df_cfb_season_games_odds_groupby_home_for_summary, df_cfb_season_games_odds_groupby_away_for_summary,
                                                         left_on=['team', 'season'], right_on=['team', 'season'], how='left')
    df_cfb_season_games_odds_groupby_join_home_and_away_for_summary_drop = df_cfb_season_games_odds_groupby_join_home_and_away_for_summary.loc[:, ~df_cfb_season_games_odds_groupby_join_home_and_away_for_summary.columns.str.contains('by_year', case=False)]

    df_cfb_season_games_odds_for_summary = df_cfb_season_games_odds_groupby_join_home_and_away_for_summary_drop

    #Select on the odds columns needed for joining onto the main dataframe
    df_cfb_season_games_odds_append_sel_col = df_cfb_season_games_odds_append[['id','season','week','team','spread','home_team_WinProb','game_point_diff','result_of_the_spread']]
    df_cfb_odds_per_game_with_calc = df_cfb_season_games_odds_append_sel_col
    df_cfb_odds_per_game_with_calc.fillna(0, inplace=True)
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
    df_cfb_ranking_all_drop.fillna(0, inplace=True)
    df_cfb_ranking_all_drop['Playoff Committee Rankings'] = df_cfb_ranking_all_drop['Playoff Committee Rankings'].replace(r'^\s*$', 0, regex=True).fillna(0).astype(str)
    columns_to_int = ['Playoff Committee Rankings', 'Coaches Poll', 'AP Top 25']
    df_cfb_ranking_all_drop[columns_to_int] = df_cfb_ranking_all_drop[columns_to_int].apply(pd.to_numeric, errors='coerce').astype('int')
    df_cfb_ranking_all_drop['season_type'] = "regular"
    df_cfb_ranking_all_updated = df_cfb_ranking_all_drop

    # Insert the transformed data into the DB
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
    df_cfb_stats_per_game.fillna(0, inplace=True)
    columns_to_int = ['id', 'season', 'week']
    df_cfb_stats_per_game[columns_to_int] = df_cfb_stats_per_game[columns_to_int].astype('int')
    columns_to_int_stats = df_cfb_stats_per_game.filter(like='offense').columns.tolist() + df_cfb_stats_per_game.filter(like='defense').columns.tolist()
    df_cfb_stats_per_game[columns_to_int_stats] = df_cfb_stats_per_game[columns_to_int_stats].fillna(0)
    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_stats_per_game', df_cfb_stats_per_game)

def team_info():
    df_cfb_team_info = sqlite_query_table('cfb_extract_team_info')

    df_cfb_team_info_rename = df_cfb_team_info.rename(columns={"school": "team"})
    df_cfb_team_info_updated = df_cfb_team_info_rename.loc[df_cfb_team_info_rename['classification'].str.contains("fbs|fcs", case=False, na=False)]
    df_cfb_team_info_updated['color'].fillna('#000000', inplace=True)

    #Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_transform_team_info', df_cfb_team_info_updated)

def schedule():
    df_cfb_schedule = sqlite_query_table('cfb_extract_schedule')
    df_cfb_schedule_loc = df_cfb_schedule.loc[
        ((df_cfb_schedule['seasonType'] == 'postseason') & (df_cfb_schedule['week'] == 1)) |
        (df_cfb_schedule['seasonType'] == 'regular')
        ]
    df_cfb_schedule_loc['lastGameStart'] = pd.to_datetime(df_cfb_schedule_loc['lastGameStart']).dt.strftime('%Y-%m-%d %H:%M:%S')
    df_cfb_schedule_loc['firstGameStart'] = pd.to_datetime(df_cfb_schedule_loc['firstGameStart']).dt.strftime('%Y-%m-%d %H:%M:%S')
    #Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_reporting_schedule', df_cfb_schedule_loc)

def player_stats_and_team_roster():
    print('Transforming Player Stats and Roster')
    df_player_season_stats = sqlite_query_table_by_year('cfb_extract_player_stats_per_season')
    df_player_season_stats.rename(columns={"season": "season_stat"}, inplace=True)
    df_player_season_stats.rename(columns={"team": "team_stat"}, inplace=True)

    df_player_team_roster = sqlite_query_table_by_year('cfb_extract_player_team_roster')
    df_player_team_roster.rename(columns={"id": "playerId"},inplace=True)
    df_player_team_roster.rename(columns={"team": "team_roster"}, inplace=True)
    df_player_team_roster.rename(columns={"season": "season_roster"}, inplace=True)
    df_player_team_roster_sel_col = df_player_team_roster[['playerId', 'team_roster', 'position', 'season_roster', 'year', 'timestamp']]

    df_player_season_stats['stat'] = df_player_season_stats['stat'].fillna(0).astype(float)
    df_player_season_stats['category_statType'] = df_player_season_stats['category'] + '_' + df_player_season_stats[
        'statType']

    df_player_season_stats_pivot = df_player_season_stats.pivot(
        index=['playerId', 'player', 'team_stat', 'conference', 'season_stat'],
        columns='category_statType',
        values='stat').reset_index()

    df_player_roster_season_stats_join = pd.merge(df_player_team_roster_sel_col,df_player_season_stats_pivot,
                                                  on=['playerId'], how='outer')
    df_player_roster_season_stats_join.sort_values(by=['playerId', 'season_roster', 'season_stat'], ascending=False, inplace=True)
    df_player_roster_season_stats_join.reset_index(inplace=True)
    #Remove Season Stats after Season Roster Year
    df_player_roster_season_stats_join_drop = df_player_roster_season_stats_join[df_player_roster_season_stats_join['season_stat'] <= df_player_roster_season_stats_join['season_roster']]

    insert_cfbd_to_sqlite('cfb_reporting_player_stats_by_season', df_player_roster_season_stats_join_drop)
    insert_cfbd_to_sqlite('cfb_reporting_player_team_roster', df_player_team_roster)


def prep_data_for_reporting():
    print('Transforming datasets for Season and Week Reporting')
    df_cfb_expand_matchup = remove_df_timestamp(sqlite_query_table('cfb_transform_season_games_expand_matchup'))
    df_cfb_ranking_all_updated = remove_df_timestamp(sqlite_query_table('cfb_transform_rankings_all_updated'))
    df_cfb_epa_per_game = remove_df_timestamp(sqlite_query_table('cfb_transform_epa_per_game'))
    df_cfb_stats_per_game = remove_df_timestamp(sqlite_query_table('cfb_transform_stats_per_game'))
    df_cfb_odds_per_game_with_calc = remove_df_timestamp(sqlite_query_table('cfb_transform_odds_per_game_with_calc'))
    df_cfb_season_games_matchups = remove_df_timestamp(sqlite_query_table('cfb_transform_season_games_matchups'))
    df_cfb_team_info = remove_df_timestamp(sqlite_query_table('cfb_transform_team_info'))
    df_cfb_season_stats_all = remove_df_timestamp(sqlite_query_table('cfb_transform_season_stats'))

    # Get unique values from multiple columns
    unique_teams = df_cfb_expand_matchup['team'].unique()
    unique_seasons = df_cfb_expand_matchup['season'].unique()
    unique_weeks = df_cfb_expand_matchup['week'].unique()
    unique_season_type = df_cfb_expand_matchup['season_type'].unique()

    postseason_data = df_cfb_expand_matchup[df_cfb_expand_matchup['season_type'] == 'postseason']
    unique_postseason_weeks = postseason_data['week'].unique()
    df_regular_season_combinations = pd.MultiIndex.from_product([unique_teams, unique_seasons, unique_weeks, ['regular']], names=['team', 'season', 'week', 'season_type']).to_frame(index=False)
    df_postseason_combinations = pd.MultiIndex.from_product([unique_teams, unique_seasons, unique_postseason_weeks, ['postseason']], names=['team', 'season', 'week', 'season_type']).to_frame(index=False)
    df_base_season_games = pd.concat([df_regular_season_combinations, df_postseason_combinations], ignore_index=True)
    df_base_season_games['sort_order'] = df_base_season_games['season_type'].apply(lambda x: 1 if x == 'postseason' else 0)
    df_base_season_games.sort_values(by=['team', 'season', 'sort_order', 'week'], ascending=[True, True, True, True], inplace=True)
    df_base_season_games.drop(columns='sort_order', inplace=True)

    df_cfb_expand_matchup_sel_col = df_cfb_expand_matchup[['team', 'season', 'week', 'season_type',
                                                           'Game Matchup', 'points', 'home_vs_away', 'id', 'box_score', 'win_loss' ]]
    df_cfb_team_info_sel_col = df_cfb_team_info[['team','abbreviation','conference','classification','color','alt_color']]

    df_base_team_season_games = pd.merge(df_base_season_games,
                                                 df_cfb_team_info_sel_col,
                                                 on=['team'],
                                                 how='left')

    #Transform df's with stats and merge on games
    df_base_team_season_games_matchup = pd.merge(df_base_team_season_games,
                                                 df_cfb_expand_matchup_sel_col,
                                                 on=['team', 'season', 'season_type', 'week'],
                                                 how='left')

    df_base_team_season_games_matchup_ranking = pd.merge(df_base_team_season_games_matchup,
                                        df_cfb_ranking_all_updated,
                                        on=['team', 'season', 'week', 'season_type'],
                                        how='left')
    df_base_team_season_games_matchup_ranking_epa = pd.merge(df_base_team_season_games_matchup_ranking,
                                        df_cfb_epa_per_game,
                                        on=['id', 'team'],
                                        suffixes=('', '_right_df'),
                                        how='left')
    df_base_team_season_games_matchup_ranking_epa = df_base_team_season_games_matchup_ranking_epa.drop(
        df_base_team_season_games_matchup_ranking_epa.filter(like='_right_df').columns, axis=1)

    df_base_team_season_games_matchup_ranking_epa_odds = pd.merge(df_base_team_season_games_matchup_ranking_epa,
                                        df_cfb_odds_per_game_with_calc,
                                        on=['id', 'team'],
                                        suffixes=('', '_right_df'),
                                        how='left')
    df_base_team_season_games_matchup_ranking_epa_odds = df_base_team_season_games_matchup_ranking_epa_odds.drop(
        df_base_team_season_games_matchup_ranking_epa_odds.filter(like='_right_df').columns, axis=1)

    df_base_team_season_games_matchup_ranking_epa_odds_stats = pd.merge(df_base_team_season_games_matchup_ranking_epa_odds,
                                        df_cfb_stats_per_game,
                                        on=['id', 'team'],
                                        suffixes=('', '_right_df'),
                                        how='left')

    df_base_team_season_games_matchup_ranking_epa_odds_stats = df_base_team_season_games_matchup_ranking_epa_odds_stats.drop(
        df_base_team_season_games_matchup_ranking_epa_odds_stats.filter(like='_right_df').columns, axis=1)

    cfb_team_season_games_all_stats = df_base_team_season_games_matchup_ranking_epa_odds_stats.fillna(0)
    cfb_season_games_matchups = df_cfb_season_games_matchups

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_reporting_team_season_games_all_stats', cfb_team_season_games_all_stats)
    insert_cfbd_to_sqlite('cfb_reporting_season_games_matchups', cfb_season_games_matchups)

    print('Transforming Summary Dataset')
    #CFB Seasons Stats zscores for summary
    df_cfb_season_games_agg_scores = remove_df_timestamp(sqlite_query_table('cfb_transform_season_games_agg_scores'))
    df_cfb_team_record_all_select_col = remove_df_timestamp(sqlite_query_table('cfb_transform_team_record'))
    df_cfb_epa_per_season_for_summary = remove_df_timestamp(sqlite_query_table('cfb_transform_epa_per_season_for_summary'))
    df_cfb_schedule = remove_df_timestamp(sqlite_query_table('cfb_reporting_schedule'))
    df_cfb_odds = remove_df_timestamp(sqlite_query_table('cfb_transform_odds_for_summary'))

    df_cfb_season_stats_zscores_for_summary = df_cfb_season_stats_all

    #CFB Season Games Score Calculation for summary
    df_cfb_season_games_agg_scores_for_summary = df_cfb_season_games_agg_scores[['team','season','home_points_season_mean','home_points_mean_over_the_years','away_points_season_mean','away_points_mean_over_the_years']]

    #CFB Team Wins and Losses by Year for summary
    df_cfb_team_record_all_select_col_for_summary = df_cfb_team_record_all_select_col

    # CFB Join dataframes for summary
    cfb_summary_join_record_rank_and_agg_scores = pd.merge(df_cfb_team_record_all_select_col_for_summary,
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
    cfb_summary_join_record_rank_agg_zscores_epa = cfb_summary_join_record_rank_agg_zscores_epa.drop(\
        columns=cfb_summary_join_record_rank_agg_zscores_epa.filter(like='timestamp').columns)

    cfb_summary_join_record_rank_agg_zscores_epa_odds = pd.merge(cfb_summary_join_record_rank_agg_zscores_epa,
                                                            df_cfb_odds,
                                                            left_on=['team', 'season'],
                                                            right_on=['team', 'season'], how='left')

    cfb_summary_all_joins = cfb_summary_join_record_rank_agg_zscores_epa_odds.sort_values(by=['team', 'season'], ascending=True, na_position='first')

    df_cfb_summary_years = cfb_summary_all_joins.groupby('season').size().reset_index(name='Count')
    cfb_summary_years_set = set(df_cfb_summary_years ['season'].tolist())
    df_cfb_schedule_years = df_cfb_schedule.groupby('season').size().reset_index(name='Count')
    cfb_schedule_years_set = set(df_cfb_schedule_years['season'].astype(int).tolist())

    years_to_fill = cfb_schedule_years_set.difference(cfb_summary_years_set)
    if len(years_to_fill) == 1:
        years_to_fill = str(next(iter(years_to_fill)))  # Extract single element
        # Use .contains() for exact matching
        cfb_summary_all_joins_loc = cfb_summary_all_joins.loc[
            ~cfb_summary_all_joins['season'].astype(str).str.contains(years_to_fill, regex=False, case=False, na=False)
        ]
    else:
        # Handle multiple elements using .isin()
        years_to_fill = list(map(str, years_to_fill))
        cfb_summary_all_joins_loc = cfb_summary_all_joins.loc[
            ~cfb_summary_all_joins['season'].astype(str).isin(years_to_fill)
        ]

    cfb_summary_all_joins_loc_groupby = cfb_summary_all_joins_loc.groupby('team')["season"].count().reset_index()
    cfb_summary_all_joins_loc_groupby['season'] = str(years_to_fill)
    cfb_summary_all_joins_loc_groupby_merged = pd.concat([cfb_summary_all_joins, cfb_summary_all_joins_loc_groupby])
    cfb_summary_all_joins_loc_groupby_merged_fillna = cfb_summary_all_joins_loc_groupby_merged.fillna(0)
    cfb_summary_join_record_rank_agg_zscores_epa_sorted = cfb_summary_all_joins_loc_groupby_merged_fillna.sort_values(by=['team', 'season'], ascending=True, na_position='first')
    #cfb_summary[cfb_summary.select_dtypes(include=['number']).columns] = cfb_summary.select_dtypes(include=['number']).astype('int')
    df_unique_team_season_combinations = pd.MultiIndex.from_product(
        [unique_teams, unique_seasons],names=['team', 'season']).to_frame(index=False)

    cfb_summary = pd.merge(df_unique_team_season_combinations,cfb_summary_join_record_rank_agg_zscores_epa_sorted,
                                                                 left_on=['team', 'season'],
                                                                 right_on=['team', 'season'], how='left')
    cfb_summary.fillna(0, inplace=True)
    cfb_summary[cfb_summary.select_dtypes(include=['number']).columns] = cfb_summary.select_dtypes(include=['number']).astype('float32')

    # Insert the transformed data into the DB
    insert_cfbd_to_sqlite('cfb_reporting_season_summary', cfb_summary)

