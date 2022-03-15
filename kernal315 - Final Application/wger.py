import os
import psycopg2
import random

""" WGER Exercise Recommender Script 
    ** Note actual API calls are in wger_updater.py
"""

# initialize varible
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

def get_exercise(body_parts, amount):
    """ Gets a requested amount of exercise randomly picked
        based on the muscle group from our database

        Parameters:
            - body_parts - muscle group wanted
            - ammount - requested amount of exercise, Max 20 or
                it may be even less depending on our database.
    """
    # connect to database
    DATABASE_URL = os.environ['DATABASE_URL']
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    cur = conn.cursor()

    # variables decleration and initialization
    amount = (20 if amount> 20 else amount)
    exercise_list = []
    name = []

    # data processing
    for part in body_parts:
        cur.execute('SELECT NAME, INFO FROM WORKOUT WHERE {} = 1'.format(part))
        rows = cur.fetchall()
        for row in rows:
            if row[0] not in name:
                name.append(row[0])
                exercise = {
                    'name' : row[0],
                    'info' : repr(row[1]).replace('\\\\r\\\\n',' ')
                }
                # debug print
                # print(row[1])
                # print(repr(row[1]))
                exercise_list.append(exercise)

    # randomly pick exercises
    return_json = {}
    e_list = len(exercise_list)
    for i in range(0,min(e_list,amount)):
        e_chosen = random.choice(exercise_list)
        exercise_list.remove(e_chosen)
        return_json[i] = e_chosen
        # debug print
        # print(e_chosen['info'],'|||')
        # print(repr(e_chosen['info']))
    
    return return_json
