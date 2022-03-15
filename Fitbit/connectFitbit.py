import matplotlib.pyplot as plt
import fitbit
import pandas as pd 
import datetime
import gather_keys_oauth2 as Oauth2

# YOU NEED TO PUT IN THE CLIENT_ID AND CLIENT_SECRET
class FitbitData:
    def __init__(self, CLIENT_ID, CLIENT_SECRET):
        """
        Create a fitbit object that can access the Fitbit Api and retrieve data
        given the CLIENT_ID and CLIENT_SECRET
        """
        # declare variables
        self.CLIENT_ID = CLIENT_ID
        self.CLIENT_SECRET = CLIENT_SECRET

        # Authorize Client side to access data
        self.server = Oauth2.OAuth2Server(CLIENT_ID, CLIENT_SECRET)
        self.server.browser_authorize()
        ACCESS_TOKEN = str(self.server.fitbit.client.session.token['access_token'])
        REFRESH_TOKEN = str(self.server.fitbit.client.session.token['refresh_token'])
        
        # create access to fitbit
        self.client_fitbit = fitbit.Fitbit(CLIENT_ID, CLIENT_SECRET, oauth2 = True, access_token = ACCESS_TOKEN, refresh_token = REFRESH_TOKEN)

    def get_past_activities(self):
        """
        This returns a list of activites the user has done in the last 7 days 
        that includes the current day
        Note most common attributes are calories, duration, name, startDate, startTime
        """
        # create a date range that goes form 7 days ago to today
        endTime = pd.datetime.today().date() #- datetime.timedelta(days = 1)
        startTime = endTime - datetime.timedelta(days = 7)
        allDates = pd.date_range(start=startTime, end = endTime)

        past_activities = []

        # iterate through all of the dates
        for currDate in allDates:

            # format the date
            currDate = currDate.date().strftime("%Y-%m-%d")
            # retrive the data from fitbit api
            data_dict = self.client_fitbit.activities(date = currDate)
            
            # iterate through the given data
            for dict_keys in data_dict:
                # get the activites data points from the dictionary data structure
                if (dict_keys == 'activities'):
                    # iterate through the list of exercises done on the specific date if there is any
                    for activity_dict in data_dict[dict_keys]:
                        # add to list
                        past_activities.append(activity_dict)
        
        return past_activities

# Quick test
user1 = FitbitData('22C23V', '0414261220b0d7884e24b300127a489a')
print(user1.get_past_activities())