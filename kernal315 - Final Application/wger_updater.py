import json
import os
import psycopg2
import random
import requests

from apscheduler.schedulers.blocking import BlockingScheduler
from html.parser import HTMLParser
from io import StringIO

""" A script to update our database of workouts that can 
    run automatically in Heroku as a seperate worker thread.

    This python script only needs to be started once in 
    Heroku though changes in the script may require a restart.
    
    To start, in command line type:
        
        heroku ps:scale wger_updater=1
    
    To end, in command line type:

        heroku ps:scale wger_updater=0

"""

# initialize variables
sched = BlockingScheduler()
bodyparts = {
    'chest': [4, 3],
    'shoulders' : [2],
    'back' : [12, 9],
    'arms' : [1, 5, 11, 13],
    'core' : [14, 6],
    'butt' : [8],
    'legs' : [10],
    'calf' : [7, 15]
}

# class to get rid of any html and just return the text component
class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        # initialize variables
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()


    def handle_data(self, d):
        self.text.write(d)
    
    
    def get_data(self):
        return self.text.getvalue()


def strip_tags(html):
    """ Take the given text and return text without html

        Parameters:
            - html - the text that needs to be cleaned
    """
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def get_exercise(body_parts):
    """ Function to get exercise information from the WGER API
        and returns a list of exercises of specified body part.

        Parameter:
            - body_parts - identifies what muscle group to search for
    
    """
    # form the url
    endpoint = 'https://wger.de/api/v2/exercise/?'
    for num in bodyparts[body_parts]:
        endpoint += 'muscles={}&'.format(num)
    endpoint += 'language=2&format=json'
    
    # retrive and format data
    response = requests.get(endpoint)
    x = json.loads(response.text)
    exercise_list = x['results']
    return_list = []

    #process data
    for exercise in range (0, len(exercise_list)):
        e_chosen = exercise_list[exercise]
        return_dict = {
            'name' : e_chosen['name'],
            'description' : strip_tags(e_chosen['description']),
            'muscle' : e_chosen['muscles']
        }
        return_list.append(return_dict)
    return return_list

def update_method():
    """ Function to update the database by getting the information
        and then adding it to our database. 
    """
    # Choose a random muscle group to update if necessary
    part_chosen = random.choice(list(bodyparts.keys()))
    exercise_list = get_exercise(part_chosen)

    # format data
    rows = []
    for i in exercise_list:
        row = []
        row.append(i['name'])
        row.append(i['description'])
        for part in bodyparts:
            if ( len(list(set(bodyparts[part]) & set(i['muscle']))) > 0 ):
                row.append(1)
            else:
                row.append(0)
        rows.append(row)
    
    # connect to database
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # add to database if new
    for exercise in rows:
        # print('Check if', exercise[0],'is in the database')
        cur.execute('SELECT NAME FROM WORKOUT WHERE NAME = %s ', (exercise[0],))
        row = cur.fetchone()
        if row is None:
            cur.execute('INSERT INTO WORKOUT (NAME, INFO, CHEST, SHOULDERS, BACK, ARMS, CORE, BUTT, LEGS, CALF) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 
            (exercise[0], exercise[1], exercise[2], exercise[3], exercise[4], exercise[5], exercise[6], exercise[7], exercise[8], exercise[9],))
            conn.commit()


# function for debugging purposes 
# @sched.scheduled_job('interval', minutes=1)
# def timed_job():
#     print("Background tasks are active")


@sched.scheduled_job('cron', day_of_week='mon-fri', hour=18)
def scheduled_job():
    """ Perform the database update at 6 P.M. Monday through 
        Friday as Heroku has recommended 
    """
    update_method()


# initialize schedule
sched.start()