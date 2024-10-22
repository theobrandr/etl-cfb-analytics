import os
import dotenv
from datetime import date
from datetime import datetime
import sqlite3
import requests
import json

#Load Enviroment Variables
dotenv.load_dotenv()

#Datetimestamp to insert into DB
global timestamp
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def check_sqllite_db_status():
    # Testing Connection to sqlite CFB.DB
    connection = sqlite3.connect("databases/nfl_espn.db")
    cursor = connection.cursor()
    sql_version_query = 'select sqlite_version();'
    cursor.execute(sql_version_query)
    result_sql_version_query = cursor.fetchall()
    print('SQLite Version is {}'.format(result_sql_version_query))
    cursor.close()
    connection.close()

