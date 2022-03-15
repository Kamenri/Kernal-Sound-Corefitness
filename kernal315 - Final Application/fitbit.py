import datetime
import json
import pandas as pd 
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import quote

#  Client Keys
client_id = '22C23V'
client_secret = '0414261220b0d7884e24b300127a489a'

# Fitbit URIS
FITBIT_AUTH_URI = 'https://www.fitbit.com/oauth2/authorize'
FITBIT_TOKEN_URI = 'https://api.fitbit.com/oauth2/token'

# Server-side Parameters
CLIENT_SIDE_URL = "https://kernal315.herokuapp.com"
SCOPE = 'activity'
REDIRECT_URI = "{}/callback/fitbit".format(CLIENT_SIDE_URL)

class FitbitData:
    def __init__(self):
        pass


    def authorize(self):
        # return url for request authorization
        param = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri' : REDIRECT_URI,
            'scope' : SCOPE
        }

        url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in param.items()])
        auth_url = "{}/?{}".format(FITBIT_AUTH_URI, url_args)
        return auth_url

    
    def get_refresh_token(self, auth_token):
        # Auth Step 4: Requests refresh and access tokens
        code_payload = {
            "grant_type": "authorization_code",
            "code": auth_token,
            "redirect_uri": REDIRECT_URI,
            'client_id': client_id
        }

        # base 64 encode
        # client_info = client_id + ':' + client_secret
        # b64val = base64.b64encode(client_info)
        # header = {'Authorization': 'Basic {}'.format(b64val)}

        post_request = requests.post(FITBIT_TOKEN_URI, data=code_payload, auth = HTTPBasicAuth(client_id, client_secret))

        # Auth Step 5: Tokens are Returned to Application
        response_data = json.loads(post_request.text)
        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        token_type = response_data["token_type"]
        expires_in = response_data["expires_in"]
        self.user_id = response_data["user_id"]

        # Auth Step 6: Use the access token to access Spotify API
        self.authorization_header = {"Authorization": "Bearer {}".format(access_token)}
        return refresh_token
    
    def refresh(self, r_token):
        # get a new access token
        endpoint = 'https://api.fitbit.com/oauth2/token'
        request_body = {
            'grant_type' : 'refresh_token',
            'refresh_token' : r_token
        }
        response = requests.post(url = endpoint, data = request_body, auth=HTTPBasicAuth(client_id,client_secret))

        # retrieve and use the new access tokens
        refresh_token = ''
        response_data = json.loads(response.text)
        print(response_data)
        if 'errors' in response_data.keys():
            return 'error'
        access_token = response_data["access_token"]
        self.user_id = response_data["user_id"]
        if 'refresh_token' in response_data.keys():
            refresh_token = response_data["refresh_token"]

        # Auth Step 6: Use the access token to access Spotify API
        self.authorization_header = {"Authorization": "Bearer {}".format(access_token)}

        return refresh_token

    
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
            data_dict = self.activities(date = currDate)
            
            # iterate through the given data
            for dict_keys in data_dict:
                # get the activites data points from the dictionary data structure
                if (dict_keys == 'activities'):
                    # iterate through the list of exercises done on the specific date if there is any
                    for activity_dict in data_dict[dict_keys]:
                        # add to list
                        past_activities.append(activity_dict)
                               

        return past_activities

    def get_rate(self, listActivities):
        """
        This returns the average rate of the user's speed based on the data of the last 7 days 
        """
        # create a date range that goes form 7 days ago to today
        endTime = pd.datetime.today().date() #- datetime.timedelta(days = 1)
        startTime = endTime - datetime.timedelta(days = 7)
        allDates = pd.date_range(start=startTime, end = endTime)

        past_distance = [] #km
        past_duration = [] #ms 
        overall_rate = [] #m / s
        count1 = 0
        count2 = 0
        count3 = 0
        count4 = 0
        Average_rate = 0
        # iterate through all of the dates
                    # retrive the data from fitbit api
        data_dict = listActivities         
        # iterate through the given data
        for dict_keys in data_dict:
            # Appends the distance/duration values onto their respective list
            if('distance' in dict_keys.keys()):
                past_distance.append(dict_keys['distance'])
            if('duration' in dict_keys.keys()):
                past_duration.append(dict_keys['duration'])
        #conversion
        for pd1 in past_distance: #conversion from KM to M
            #count = 0
            if (count1 < len(past_distance)):
                past_distance[count1] = past_distance[count1] / 1000.0
            count1 = count1 + 1
        for pd2 in past_duration: #conversion from ms to s
            if (count2 < len(past_duration)):
                past_duration[count2] = past_duration[count2] * 1000.0
            count2 = count2 + 1  
        for pd3 in past_distance: #conversion to m/s
            if (count3 < len(past_distance)):
                avgrate = past_distance[count3] / past_duration[count3]
                overall_rate.append(avgrate)
            count3 = count3 + 1
        Overall_Sum = 0;  
        for sumOR in overall_rate: #mean of the overall rate
            Overall_Sum = Overall_Sum + sumOR
            count4 = count4 + 1
            if(count4 == len(overall_rate)):
                Average_rate = Overall_Sum / len(overall_rate)
        return Average_rate


    def activities(self, date):
        endpoint = 'https://api.fitbit.com/1/user/{}/activities/date/{}.json'.format(self.user_id, date)
        response = requests.get(endpoint, headers=self.authorization_header)
        return json.loads(response.text)


    def createJSON(self,list_act):
        ret_json = {}
        keys = ['name','startDate','startTime', 'duration', 'calories', 'distance']
        num = 0
        for activity in list_act:
            act_dict = {}
            act_dict['name'] = activity['name']
            
            duration =round( ((activity['duration']/1000) /60),2)
            act_dict['Date'] = activity['startDate']
            act_dict['Time Started'] = activity['startTime']
            act_dict['Duration'] = '{} minutes'.format(duration)
            act_dict['Calories Spent'] = '{} cal'.format(activity['calories'])
            if 'distance' in activity.keys() and activity['activityParentName'] != 'Interval Workout':
                act_dict['Distance'] = '{} km'.format(activity['distance'])
            ret_json[num] = act_dict
            num += 1
        # return json.dumps(ret_json)
        return ret_json
