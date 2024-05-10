# Blitzanalytics
Your Playbook to Success through College Football Data ETL's and Reporting.
The program will extract 5 years of college football/cfb data, transform the data, load the data into a local database, and automatically generate reports.  

**Program Status**
<br>
- [100%] College Football Data 
- [100%] College Football Matchup Reporting
- [0%] College Football Team Reporting

**Requirements**
<br>
  In order to use this python ETL you will need:
  - A valid API key from collegefootballdata.com 
  - Mutiple Python packages (pandas, requests, openpyxl and python-dotenv)
  - A ".env" file in the same directory as the script

**Getting Started**
<br>
  If you don't already have the additional packages installed you will need to install them with pip
  - pip install -r requirements.txt

**Usage**
<br>
  blitanalytics.py

**Program Arguments***
  python blitzanalytics.py [-p] [-r REPORT_WEEK] [-y REPORT_YEAR] [-t] [-d] [-s]
  -p, --previous_years: Pull data for the last 5 years. By default, only the current year's data will be pulled.
  -r REPORT_WEEK, --report_week REPORT_WEEK: Specify a week for reporting. The default week is the current week.
  -y REPORT_YEAR, --report_year REPORT_YEAR: Specify a year for reporting. The default year is the current year.
  -t, --season_type: Specify 'regular' for Regular Season or 'postseason' for PostSeason.
  -d, --delete_tables: Delete all DB tables if the database is consuming excessive space. Run the program with the -p flag afterward to re-populate the DB.
  -s, --skip_extract: Skip the data extraction process if new data isn't required.

  Examples:
  python blitzanalytics.py -p
  python blitzanalytics.py -y 2023 -w 3 -t regular


**.ENV file**
<br>
  An example .env file is found in this repository.
  - You will need to put your collegefootballdata.com api key in this file in order to pull from this data source.

**File Storage**
  In order to avoid re-pulling all previous years cfb data with every run of the script, a local sqlite database will be created in the directory the script is run from. 

**College Football**
<br>
  Current Reporting:
  - Weekly Matchup Reporting
    
  - Game Matchups by Season and Week
  - Team Record by Season
  - Team Seasons Offensive/Defensive/Special Teams Stats
  - Team Season Rankings
  - Team Info
  - EPA per Game
  - Odds/Spread per Game


