import pandas
import os

def data_to_excel():
    print('Loading Datasets to xlsx')
    with pd.ExcelWriter(str(file_path_cfb) + '/cfb.xlsx') as writer:
        cfb_summary.to_excel(writer, sheet_name='cfb_summary', engine='xlsxwriter')
        cfb_games_with_spread_analytics.to_excel(writer, sheet_name='cfb_games_spread', engine='xlsxwriter')
        cfb_season_stats_by_season.to_excel(writer, sheet_name='cfb_season_stats_by_season', engine='xlsxwriter')
        cfb_season_games_agg_scores.to_excel(writer, sheet_name='cfb_games_scores', engine='xlsxwriter')
        cfb_team_record_by_year.to_excel(writer, sheet_name='cfb_team_record', engine='xlsxwriter')
        cfb_stats_per_game.to_excel(writer, sheet_name=' cfb_stats_per_game', engine='xlsxwriter')
        cfb_all_data.to_excel(writer, sheet_name='cfb_all_data', engine='xlsxwriter')