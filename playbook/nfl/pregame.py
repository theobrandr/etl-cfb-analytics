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



