import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from playbook import load

cwd = os.getcwd()
file_path_cfb = cwd

def matchups(reporting_year, reporting_week, report_season_type):
    print('Generating Reports for current week of the year')
    reporting_year = str(reporting_year)
    file_path_cfb_reports = cwd + '/reports/cfb/'
    file_path_cfb_reports_reporting_year = file_path_cfb_reports + str(reporting_year) + '/'
    file_path_cfb_reports_reporting_year_week_season_type = file_path_cfb_reports_reporting_year + str(report_season_type) + '/'
    file_path_cfb_reports_reporting_year_week = file_path_cfb_reports_reporting_year_week_season_type + 'Week_' + str(reporting_week) + '/'

    cfb_season_week_matchups = load.sqlite_query_table('cfb_reporting_season_week_matchups')
    cfb_all_data = load.sqlite_query_table('cfb_reporting_all_data')
    cfb_team_info = load.sqlite_query_table('cfb_reporting_team_info')
    cfb_summary = load.sqlite_query_table('cfb_reporting_summary')
    cfb_season_stats_by_season = load.sqlite_query_table('cfb_reporting_season_stats_by_season')

    df_cfb_for_reporting_game_matchup = cfb_season_week_matchups[cfb_season_week_matchups['season'].astype(str).str.contains(reporting_year)]
    df_cfb_for_reporting_game_matchup_reporting_week = df_cfb_for_reporting_game_matchup.loc[(df_cfb_for_reporting_game_matchup['week'] == int(reporting_week)) & (df_cfb_for_reporting_game_matchup['season_type'] == str(report_season_type))]
    cfb_all_data_reporting_year = cfb_all_data.loc[cfb_all_data['season'] == str(reporting_year)]

    for index, row in df_cfb_for_reporting_game_matchup_reporting_week.iterrows():
        home_team = row['home_team']
        away_team = row['away_team']
        matchup = row['Game Matchup']
        df_home_team_all_data = cfb_all_data.loc[cfb_all_data['team'] == home_team]
        df_away_team_all_data = cfb_all_data.loc[cfb_all_data['team'] == away_team]
        home_team_color = cfb_team_info.loc[cfb_team_info['team'] == home_team, 'color'].iloc[0]
        away_team_color = cfb_team_info.loc[cfb_team_info['team'] == away_team, 'color'].iloc[0]

        df_matchup_home_away_all_data = pd.concat([df_home_team_all_data, df_away_team_all_data], ignore_index=True)
        df_matchup_home_away_all_data_current_season = df_matchup_home_away_all_data.loc[
            df_matchup_home_away_all_data['season'] == str(reporting_year)]

        df_cfb_summary_home_team = cfb_summary.loc[cfb_summary['team'] == (home_team)]
        df_cfb_summary_away_team = cfb_summary.loc[cfb_summary['team'] == (away_team)]
        df_cfb_summary_home_away_append = pd.concat([df_cfb_summary_home_team, df_cfb_summary_away_team], ignore_index=True).reset_index()

        df_cfb_season_stats_by_season_home_team = cfb_season_stats_by_season.loc[cfb_season_stats_by_season['team'] == (home_team)]
        df_cfb_season_stats_by_season_away_team = cfb_season_stats_by_season.loc[cfb_season_stats_by_season['team'] == (away_team)]
        df_cfb_season_stats_by_season_home_away_append = pd.concat([df_cfb_season_stats_by_season_home_team, df_cfb_season_stats_by_season_away_team], ignore_index=True)
        df_cfb_season_stats_by_season_home_away_append.sort_values(by=['season','team'], inplace=True, ascending=False)

        #Create DF for Matchup Summary
        df_matchup_home_away_all_data_sel_col = df_matchup_home_away_all_data[['Game Matchup', 'team', 'AP Top 25', 'season', 'season_type',
                                                            'week', 'start_date', 'conference_game']]

        condition_matchup_summary = (
                (df_matchup_home_away_all_data_sel_col['season'] == str(reporting_year)) &
                (df_matchup_home_away_all_data_sel_col['week'] == int(reporting_week)) &
                (df_matchup_home_away_all_data_sel_col['season_type'] == str(report_season_type))
        )

        df_matchup_summary = df_matchup_home_away_all_data_sel_col.loc[condition_matchup_summary]
        '''
        df_matchup_summary = df_matchup_home_away_all_data_sel_col.loc[
            df_matchup_home_away_all_data_sel_col['season'] == str(reporting_year)].loc[
            (df_matchup_home_away_all_data_sel_col['week'] == int(reporting_week)) & (df_cfb_for_reporting_game_matchup['season_type'] == str(report_season_type))]
        '''
        #Create DF for Matchup Summary Current Season Table
        df_matchup_home_away_all_data_current_season_sel_col = df_matchup_home_away_all_data_current_season[[
            'team', 'season', 'season_type', 'week', 'conference_game', 'home_vs_away', 'points', 'home_team', 'home_points',
            'home_line_scores', 'away_team', 'away_points', 'away_line_scores']]

        #Create DF additional Matchup Summary High Level Stats Info
        df_cfb_summary_home_away_append_sel_col = df_cfb_summary_home_away_append[['season', 'team', 'total.wins', 'total.losses',
                                                           'home_points_season_mean', 'away_points_season_mean',
                                                           'epa_per_game_offense_overall_avg_per_season',
                                                           'epa_per_game_offense_overall_avg_per_season']].reset_index()
        df_cfb_summary_matchup_reporting_year = df_cfb_summary_home_away_append_sel_col

        #Create figure for Matchup Summary Tables
        fig_df_matchup_summary = plt.figure("fig_matchup_summary", figsize=(10, 5))
        fig_df_matchup_summary.ax1 = fig_df_matchup_summary.add_subplot(311)
        fig_df_matchup_summary.ax1.axis('off')
        fig_df_matchup_summary.ax1.table(cellText=df_matchup_summary.values, colLabels=df_matchup_summary.columns)

        fig_df_matchup_summary.ax2 = fig_df_matchup_summary.add_subplot(312)
        fig_df_matchup_summary.ax2.axis('off')
        fig_df_matchup_summary.ax2.table(cellText=df_cfb_summary_matchup_reporting_year.values, colLabels=df_cfb_summary_matchup_reporting_year.columns)

        fig_df_matchup_summary.ax3 = fig_df_matchup_summary.add_subplot(313)
        fig_df_matchup_summary.ax3.axis('off')
        fig_df_matchup_summary.ax3.table(cellText=df_matchup_home_away_all_data_current_season_sel_col.values,
                  colLabels=df_matchup_home_away_all_data_current_season_sel_col.columns)

        #Create DF and figure for Season Stats Table
        df_matchup_season_stats_offense = df_cfb_season_stats_by_season_home_away_append[
            ['team', 'season', 'offense_possessionTime','offense_totalYards','offense_netPassingYards',
             'offense_passAttempts','offense_passCompletions','offense_passingTDs','offense_rushingYards',
             'offense_rushingAttempts','offense_rushingTDs','offense_turnovers','offense_fumblesLost','offense_passesIntercepted']]
        df_matchup_season_stats_offense_reporting_year = df_matchup_season_stats_offense.loc[
            df_matchup_season_stats_offense['season'] == str(reporting_year)]

        df_matchup_season_stats_offense_downs_and_turnovers = df_cfb_season_stats_by_season_home_away_append[
            ['team', 'season', 'offense_firstDowns','offense_thirdDowns','offense_thirdDownConversions',
             'offense_fourthDowns','offense_fourthDownConversions','offense_turnovers',
             'offense_fumblesLost','offense_passesIntercepted']]
        df_matchup_season_stats_offense_downs_and_turnovers_reporting_year = df_matchup_season_stats_offense_downs_and_turnovers.loc[
            df_matchup_season_stats_offense_downs_and_turnovers['season'] == str(reporting_year)]

        df_matchup_season_stats_defense = df_cfb_season_stats_by_season_home_away_append[
            ['team', 'season', 'defense_tacklesForLoss','defense_sacks','defense_fumblesRecovered',
             'defense_interceptions','defense_interceptionTDs']]
        df_matchup_season_stats_defense_reporting_year = df_matchup_season_stats_defense.loc[
            df_matchup_season_stats_defense['season'] == str(reporting_year)]

        df_matchup_season_stats_special_teams = df_cfb_season_stats_by_season_home_away_append[
            ['team', 'season', 'specialteams_kickReturns','specialteams_kickReturnYards','specialteams_kickReturnTDs',
             'specialteams_puntReturnYards','specialteams_puntReturns','specialteams_puntReturnTDs']]
        df_matchup_season_stats_special_teams_reporting_year = df_matchup_season_stats_special_teams.loc[
            df_matchup_season_stats_special_teams['season'] == str(reporting_year)]

        #Create Figure for Matchup Season Stats Offense
        fig_df_matchup_season_stats_offense = plt.figure("fig_matchup_season_stats", figsize=(10, 5))
        ax1 = fig_df_matchup_season_stats_offense.add_subplot(211)
        ax1 = plt.table(cellText=df_matchup_season_stats_offense.values,colLabels=df_matchup_season_stats_offense.columns)
        ax1 = plt.axis('off')

        ax2 = fig_df_matchup_season_stats_offense.add_subplot(212)
        ax2 = plt.table(cellText=df_matchup_season_stats_offense_downs_and_turnovers.values,colLabels=df_matchup_season_stats_offense_downs_and_turnovers.columns)
        ax2 = plt.axis('off')

        #Create Figure for Matchup Season Stats Defense and Special Teams
        fig_df_matchup_season_stats_defense_special_teams = plt.figure("fig_matchup_season_stats_defense_special_teams", figsize=(10, 5))
        ax1 = fig_df_matchup_season_stats_defense_special_teams.add_subplot(211)
        ax1 = plt.table(cellText=df_matchup_season_stats_defense.values,colLabels=df_matchup_season_stats_defense.columns)
        ax1 = plt.axis('off')

        ax2 = fig_df_matchup_season_stats_defense_special_teams.add_subplot(212)
        ax2 = plt.table(cellText=df_matchup_season_stats_special_teams.values,colLabels=df_matchup_season_stats_special_teams.columns)
        ax2 = plt.axis('off')

        #Create figures for report
        list_figures = []

        fig_matchup_team_points = sns.catplot(data=df_matchup_home_away_all_data, x="week", y="points",
                                              col="season", kind='bar', hue="team",
                                              height=4, aspect=1,
                                              palette={home_team:home_team_color, away_team:away_team_color})
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        list_figures.append(fig_matchup_team_points)

        fig_matchup_result_of_the_spread = sns.catplot(data=df_matchup_home_away_all_data, x="result_of_the_spread",
                                                       kind="count", col="season", hue="team",
                                                       height=4, aspect=1,
                                                       palette={home_team:home_team_color, away_team:away_team_color})
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        fig_matchup_result_of_the_spread.set_xticklabels(rotation=65, horizontalalignment='right')
        list_figures.append(fig_matchup_result_of_the_spread)

        fig_matchup_passing_success, axes = plt.subplots(1, 2)
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        sns.set(rc={"figure.figsize": (8, 4)})
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="offense.passingPlays.successRate",
                     hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[0],
                     marker="o")
        axes[0].set(xticks=df_matchup_home_away_all_data_current_season['week'])
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="defense.passingPlays.successRate",
                     hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[1], marker="o")
        axes[1].set(xticks=df_matchup_home_away_all_data_current_season['week'])
        fig_matchup_passing_success.tight_layout()
        list_figures.append(fig_matchup_passing_success)

        fig_matchup_rushing_success, axes = plt.subplots(1, 2)
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        sns.set(rc={"figure.figsize": (8, 4)})
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="offense.rushingPlays.successRate",
                     hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[0],
                     marker="o")
        axes[0].set(xticks=df_matchup_home_away_all_data_current_season['week'])
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="defense.rushingPlays.successRate",
                     hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[1],
                     marker="o")
        axes[1].set(xticks=df_matchup_home_away_all_data_current_season['week'])
        fig_matchup_rushing_success.tight_layout()
        list_figures.append(fig_matchup_rushing_success)

        fig_matchup_passing_rushing_yards, axes = plt.subplots(1, 2)
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        sns.set(rc={"figure.figsize": (8, 4)})
        sns.lineplot(data=df_matchup_home_away_all_data, x="season", y="offense_netPassingYards", hue="team",
                     palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[0], marker="o")
        sns.lineplot(data=df_matchup_home_away_all_data, x="season", y="offense_rushingYards", hue="team",
                     palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[1], marker="o")
        fig_matchup_passing_rushing_yards.tight_layout()
        list_figures.append(fig_matchup_passing_rushing_yards)

        fig_matchup_offense_defense_success, axes = plt.subplots(1, 2)
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        sns.set(rc={"figure.figsize": (8, 4)})
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="offense.successRate",
                        hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[0], marker="o")
        axes[0].set(xticks=df_matchup_home_away_all_data_current_season['week'])
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="defense.successRate",
                        hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[1], marker="o")
        axes[1].set(xticks=df_matchup_home_away_all_data_current_season['week'])
        fig_matchup_offense_defense_success.tight_layout()
        list_figures.append(fig_matchup_offense_defense_success)

        fig_matchup_offense_defense_zscores, axes = plt.subplots(1, 2)
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        sns.set(rc={"figure.figsize": (8, 4)})
        sns.lineplot(data=df_cfb_summary_home_away_append, x="season", y="offense_zscore_final", hue="team",
                      palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[0], marker="o")
        sns.lineplot(data=df_cfb_summary_home_away_append, x="season", y="defense_zscore_final", hue="team",
                      palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[1], marker="o")
        fig_matchup_offense_defense_zscores.tight_layout()
        list_figures.append(fig_matchup_offense_defense_zscores)

        fig_matchup_special_teams_total_zscores, axes = plt.subplots(1, 2)
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        sns.set(rc={"figure.figsize": (8, 4)})
        sns.lineplot(data=df_cfb_summary_home_away_append, x="season", y="specialteams_zscore_final", hue="team",
                      palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[0], marker="o")
        sns.lineplot(data=df_cfb_summary_home_away_append, x="season", y="total_zscore", hue="team",
                     palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[1], marker="o")
        fig_matchup_special_teams_total_zscores.tight_layout()
        list_figures.append(fig_matchup_special_teams_total_zscores)

        fig_matchup_epa_offense_defense, axes = plt.subplots(1, 2)
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        sns.set(rc={"figure.figsize": (10, 4)})
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="offense.ppa",
                     hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[0], marker="o")
        axes[0].set(xticks=df_matchup_home_away_all_data_current_season['week'])
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="defense.ppa",
                     hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[1], marker="o")
        axes[1].set(xticks=df_matchup_home_away_all_data_current_season['week'])
        fig_matchup_epa_offense_defense.tight_layout()
        list_figures.append(fig_matchup_epa_offense_defense)


        fig_matchup_epa_offense_defense_per_season, axes = plt.subplots(1, 2)
        sns.set_style("whitegrid", {'grid.linestyle': '--'})
        sns.set(rc={"figure.figsize": (10, 4)})
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="epa_per_game_offense.overall",
                     hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[0],
                     marker="o")
        sns.lineplot(data=df_matchup_home_away_all_data_current_season, x="week", y="epa_per_game_defense.overall",
                     hue="team", palette={home_team: home_team_color, away_team: away_team_color}, ax=axes[1],
                     marker="o")
        fig_matchup_epa_offense_defense_per_season.tight_layout()
        list_figures.append(fig_matchup_epa_offense_defense_per_season)

        '''
        fig_matchup_all_teams_zscore = sns.displot(data=cfb_all_data_reporting_year, x ="offense_zscore_final", hue="team",
                                                   palette={home_team: home_team_color, away_team: away_team_color, 'team': 'black'})

        sns.set(rc={"figure.figsize": (8, 4)})
        list_figures.append(fig_matchup_all_teams_zscore)
        '''

        #Output DF's and Figures to Report
        filename_team_report = file_path_cfb_reports_reporting_year_week + str(matchup) + ".pdf"
        pp = PdfPages(filename_team_report)
        pp.savefig(fig_df_matchup_summary, bbox_inches='tight')
        for fig in list_figures:
            fig.savefig(pp, format='pdf')
        pp.savefig(fig_df_matchup_season_stats_offense, bbox_inches='tight')
        pp.savefig(fig_df_matchup_season_stats_defense_special_teams, bbox_inches='tight')
        pp.close()
        plt.close('all')
        print('Report Generated for ' + str(matchup))
