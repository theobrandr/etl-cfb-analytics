# Accretion Data
College Football Data ETL's for advanced metrics and visualization with dash + plotly. 
The program will extract 5 years of college football/cfb data, transform the data, load the data into a local database. 
<br>
Once the ETL is done running, run accretiondata.py and navigate to http://127.0.0.1:8050


**Requirements**
<br>
  In order to use this python ETL you will need:
  - A valid API key from collegefootballdata.com 
  - Mutiple Python packages found in requirements.txt
  - A ".env" file in the same directory as the script

**Getting Started**
<br>
  If you don't already have the additional packages installed you will need to install them with pip
  - pip install -r requirements.txt

**Usage**
<br>
  - etl-cfbd.py (Data ETL to pull in College Football Data and Transform it for Reporting)
  - accretiondata.py (Dash App for Reporting)
    
<br>
**Program Arguments***
### Command Line Arguments for Blitz Analytics
<br>
  python etl-cfbd.py [-t] [-d] [-s]
  <br>
  --delete_tables	-d	Flag	Delete all DB tables if the database is consuming excessive space.
  <br>
  --skip_extract	-s	Flag	Skip the data extraction process if new data isn't required.
  <br>
  --skip_transform	-t	Flag	Skip the data transformation process if transforming data is not needed.
  <br>
  <br>

Examples:
  - Delete tables and re-populate the database:<br>
    -- python blitzanalytics.py -d -p
  - Pull data for previous years and generate a PDF report:<br>
    -- python blitzanalytics.py -p -r
  - Skip pulling data and transforming data and start the visualization:<br>
    -- python blitzanalytics.py -s -t


**.ENV file**
<br>
  An example .env file is found in this repository.
  - You will need to put your collegefootballdata.com api key in this file in order to pull from this data source.

**File Storage**
  In order to avoid re-pulling all previous years cfb data with every run of the script, a local sqlite database will be created in the directory the script is run from. 

**Accretion Data**
<img width="1316" alt="image" src="https://github.com/user-attachments/assets/8615809a-1454-49ed-950d-446e915e82d9">

**College Football Matchup Summary**
<img width="1469" alt="image" src="https://github.com/user-attachments/assets/c9dd95fd-70f0-4ac5-b60e-84638eba9539">

**College Football Matchup Detailed Analytics**
<br>
<img width="1422" alt="image" src="https://github.com/user-attachments/assets/8d4cae3b-d539-4632-bcf0-980183f5e0be">
<br>
<img width="1324" alt="image" src="https://github.com/user-attachments/assets/89d60b7e-b2f1-4da4-ba34-74f414f69248">
<br>
<img width="1440" alt="image" src="https://github.com/user-attachments/assets/63554f08-3a0f-4f35-baf0-a7f6bea28240">
<br>
<img width="736" alt="image" src="https://github.com/user-attachments/assets/0b5f5a60-b25d-4184-b7cc-bef50a21ab03">
<br>
<img width="726" alt="image" src="https://github.com/user-attachments/assets/e35f4a66-88d9-494e-a583-a10257cfe310">
<br>
<img width="1408" alt="image" src="https://github.com/user-attachments/assets/658d58e1-95b9-4877-8932-aa8d114027d1">




