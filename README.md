# etl-cfb-analytics
An ETL for College Football data and Analytics

The ETL will extract 5 years of college football data from collegefootball.com, transform data, load it to a CSV, and automatically generate reports for the curent year by week and by matchup.  

**Requirements**
<br>In order to use this python ETL you will need:
- A valid API key from collegefootballdata.com 
- Mutiple Python packages (pandas, requests, openpyxl and python-dotenv)
- A ".env" file in the same directory as the script

**Getting Started**
<br>If you don't already have the additional packages installed you will need to install them with pip
pip install -r requirements.txt

**.ENV file**
<br>An example .env file is found in this repository.

- You will need to put your collegefootballdata.com api key in this file.

- During the first run of the ETL, 5 years of cfb data will be pulled. After the intial run, this variable will be set to false. 
If you would like to re-pull that data, change this back to env_previous_years_api_pull_status='False'
If you don't want to pull 4 years of previous data, set env_previous_years_api_pull_status='True'

**File Storage**
- In order to avoid re-pulling all previous years cfb data with every run of the script, a folder titled 'api_files' will be created in the directory the script is run from. All of the collegefootball.com api pulls are stored in this folder as json files. The ETL will update the current year files with each run. 

**ETL Usage**
- python etl_cfb_analytics.py

**Data and Analystics Pulled**
- Game Matchups by Season and Week
- Team Record by Season
- Team Seasons Offensive/Defensive/Special Teams Stats
- Team Season Rankings
- Team Info
- EPA per Game
- Odds/Spread per Game

**Reporting Currently Automatically Generated**
- Points Scored by team for the last 5 years
- Result of the spread by team for the last 5 years
