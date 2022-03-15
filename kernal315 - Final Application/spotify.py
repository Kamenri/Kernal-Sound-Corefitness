import base64
import json
import random
import requests
import spotify_settings
from requests.auth import HTTPBasicAuth
from urllib.parse import quote


""" Spotify Scipt that connects users to api and can generate a spotify playlist"""

#  Client Keys
client_id = 'c5e8920929564a4189b2a238ec4df8c9'
client_secret = 'e29ae4fb338e4ceb99f324ba4d2841da'


# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Server-side Parameters
CLIENT_SIDE_URL = "https://kernal315.herokuapp.com"
SCOPE = "playlist-modify-public playlist-modify-private"
REDIRECT_URI = "{}/callback/spotify".format(CLIENT_SIDE_URL)
# REDIRECT_URI = "{}signin".format(CLIENT_SIDE_URL)
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


class SpotifyGenerator:
    def __init__(self):
        pass
        
    
    def authorize(self):
        """ return url for request authorization
        """
        param = {
            'client_id': client_id,
            'response_type': 'code',
            'redirect_uri' : REDIRECT_URI,
            'scope' : SCOPE
        }
        url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in param.items()])
        auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
        return auth_url


    def get_refresh_token(self, auth_token):
        """ get refresh and access token to use

            Parameters:
                - auth_token - authorization token needed to get a refresh and access token        
        """

        # Requests refresh and access tokens
        code_payload = {
            "grant_type": "authorization_code",
            "code": auth_token,
            "redirect_uri": REDIRECT_URI,
            'client_id': client_id,
            'client_secret': client_secret
        }
        post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
        
        # Tokens are Returned to Application
        response_data = json.loads(post_request.text)
        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        token_type = response_data["token_type"]
        expires_in = response_data["expires_in"]

        # Use the access token to access Spotify API
        self.authorization_header = {"Authorization": "Bearer {}".format(access_token)}
        self.authorization_header_2 = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type":"application/json"
        }
        self.authorization_header_3 = {
            "Authorization": "Bearer {}".format(access_token),
            "Accept":"application/json"
        }
        # Get profile data
        user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
        profile_response = requests.get(user_profile_api_endpoint, headers=self.authorization_header)
        profile_data = json.loads(profile_response.text)
        self.user_id = profile_data['id']
        return refresh_token

    
    def refresh(self, r_token):
        # get a new access token
        endpoint = 'https://accounts.spotify.com/api/token'
        request_body = {
            'grant_type' : 'refresh_token',
            'refresh_token' : r_token
        }
        response = requests.post(url = endpoint, data = request_body, auth=HTTPBasicAuth(client_id,client_secret))

        # retrieve and use the new access tokens
        refresh_token = ''
        response_data = json.loads(response.text)
        if 'error' in response_data.keys():
            return 'error'
        access_token = response_data["access_token"]
        if 'refresh_token' in response_data.keys():
            refresh_token = response_data["refresh_token"]

        # Use the access token to access Spotify API
        self.authorization_header = {"Authorization": "Bearer {}".format(access_token)}
        self.authorization_header_2 = {
            "Authorization": "Bearer {}".format(access_token),
            "Content-Type":"application/json"
        }
        self.authorization_header_3 = {
            "Authorization": "Bearer {}".format(access_token),
            "Accept":"application/json"
        }
        # Get profile data
        user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
        profile_response = requests.get(user_profile_api_endpoint, headers=self.authorization_header)
        profile_data = json.loads(profile_response.text)
        self.user_id = profile_data['id']

        return refresh_token


    def get_songs(self,genres, no_playlist, not_explicit):
        """ given a list of genres/ categories it will get the first no_playlist
            and retrieve all songs for it. this will return a list of song ids.

            Parameters:
                - genres - list of genres identified in spotify_settings.py
                - no_playlist - number of playlist to call from
                - not_explicit - Bool value to determine if the songs produced should be explicit or not
        """

        # declare variables
        songs_list = []
        num = 0
        # go through the genres
        for category in genres:
            # get ids of category
            
            category_id = spotify_settings.genres_ids[category]
            print(category, category_id)
            # request the playlists of the category
            playlists_result = self.category_playlists(category_id)
            print(len(playlists_result['playlists']['items']),'------------------playlist_results_length-----------------')
            # create a list of playlist ids
            p_id_list = []
            for playlist in playlists_result['playlists']['items']:
                p_id_list.append(playlist['id'])

            # we can decide which playlist to chose
            # this will pick the first no_playlist or less depending on size of list
            for i in range(0, min(no_playlist , len(p_id_list))):
                # request songs in playlist
                songs_result = self.playlist(p_id_list[i])
                # add the songs to list if it does not exist in the list
                # print(songs_result)
                print(len(songs_result['tracks']['items']),'------------------song_len_playlist--------------------')
                for song in songs_result['tracks']['items']:
                    if (song['track'] != None ):
                        if (song['track']['id'] not in songs_list):
                            # checks if explicit and is in us
                            num += 1
                            # if((not song['track']['explicit'] or not not_explicit) and ('US' in song['track']['available_markets'])):
                            if(not song['track']['explicit'] or not not_explicit):
                                songs_list.append(song['track']['id'])

        # return the list
        print(num,'---------------num----------------')
        return songs_list


    def check_filters(self, song, features):
        """ function will return a bool value depending if the song fits the specified feature

            Parameters:
                - song - attributes of a song stored in a dictionary
                - features - attributes in a dictionary to compare the song against
        """
        
        # go through each features and check if song fits within it
        for feature in features.keys():
            if(not isinstance(song,dict)):
                return False
            # get feature being measured
            value = float(song[feature])

            # returns false if it does not meet the criterea
            goal = features[feature][0]
            tolerance = features[feature][1]
            if ((goal - tolerance > value or value > goal + tolerance)):
                return False
        # if all features are right then return True
        return True


    def filter_songs_list(self, songs_list, features):
        """ function will return a new list of song that fits the features criteria

            Parameters:
                - song - list of song id's from a prespecified genre
                - features - attributes in a dictionary to compare the song against
        """
        new_songs_dict = {}
        # go through the playlist one hundred at a time
        for i in range(0, len(songs_list), 100):
            # get attributes
            songs_result = self.audio_features(songs_list[i : i + 100])

            # iterate through the list of song features dictionary
            for song in songs_result['audio_features']:
                # get feature being measured

                # add song id if it is within the tolerence
                if (self.check_filters(song, features)):
                    new_songs_dict[song['id']] = song['duration_ms']

        return new_songs_dict


    def create_playlist(self,songs, name):
        """ creates a playlist of songs, notice that only 100 songs can be added
            returns the link to playlist

            Parameters:
                - songs - list of song id's or uri
                - name - name to  be given to the playlist
        """
        # if there are too many songs cut it short
        if (len(songs) > 50):
            songs = songs[0:49]

        # make playlist
        results = self.user_playlist_create(name)
        playlist_url = results['external_urls']['spotify']
        playlist_id = results['id']

        # add songs
        self.user_playlist_add_tracks(playlist_id,songs)
        return playlist_url


    def generate_playlist(self, name, length_min, features, genres, no_playlist, not_explicit):
        """ function to be called by the main code, creates a playlist based on the specified
            attributes and features, returns the playlist ur

            Parameters:
                - name - name to give the playlist
                - length_min - time in minutes to try to reach, altough it would not be guaranteed if the features are too specific
                - features - attributes in a dictionary to compare the song against
                - genres - list of genres identified in spotify_settings.py
                - no_playlist - number of playlist to call from
                - not_explicit - Bool value to determine if the songs produced should be explicit or not
        """
        list_of_songs = self.get_songs(genres, no_playlist, not_explicit)
        print(len(list_of_songs))
        song_dictionary = self.filter_songs_list(list_of_songs,features)

        # choose the songs for the playlist that adds up to aroung the wanted length
        goal_length = 60000 * length_min
        list_of_id = list(song_dictionary.keys())
        songs_chosen = []
        reach_goal = True
        spotify_cap = 49
        num = 0
        while(goal_length > 0 and reach_goal and spotify_cap > num):
            if(len(list_of_id) == 0):
                reach_goal = False
                print('out')
            else:
                # get random id and remove from list
                id_chosen = random.choice(list_of_id)
                list_of_id.remove(id_chosen)

                songs_chosen.append(id_chosen)
                print('song added')
                goal_length -= int(song_dictionary[id_chosen])
            num += 1

        # create the playlist
        url = self.create_playlist(songs_chosen, name)
        url = url[0:25] + 'embed' + url[24:]
        return reach_goal, url

    
    def categories(self, country, limit):
        """ request categories in spotify

            Parameters:
                - country - takes an ISO 3166-1alpha-2 country code
                    categories relavant to a particular country
                - limit - how much playlist to get, up to 50 or less depending
                    on if we there are less playlist
        """
        endpoint = 'https://api.spotify.com/v1/browse/categories'
        param = {
            'country' : country,
            'limit' : limit
        }
        response = requests.get(endpoint, headers=self.authorization_header, params=param)
        return json.loads(response.text)


    def category_playlists(self, category_id):
        """ request the playlists of a category, returns dictionary

            Parameters: 
                - category_id - category id
        """
        endpoint = 'https://api.spotify.com/v1/browse/categories/{}/playlists'.format(category_id)
        response = requests.get(endpoint, headers=self.authorization_header)
        return json.loads(response.text)


    def playlist(self, playlist_id):
        """ request the songs of a playlist, returns dictionary

            Parameters: 
                - playlist_id - playlist id
        """
        endpoint = 'https://api.spotify.com/v1/playlists/{}'.format(playlist_id)
        param = {
            'country' : 'US',
        }
        response = requests.get(endpoint, headers=self.authorization_header, params=param)
        return json.loads(response.text)


    def audio_features(self, song_list):
        """ request the features of song, returns dictionary

            Parameters: 
                - song_list - list of song ids
        """
        s_list = ','.join(song_list)
        endpoint = 'https://api.spotify.com/v1/audio-features'
        param = {
            'ids' : s_list,
        }
        response = requests.get(endpoint, headers=self.authorization_header, params=param)
        return json.loads(response.text)


    def user_playlist_create(self, name):
        """ create a playlist in spotify, returns dictionary of the url for the playist

            Parameters: 
                - name - name of the playlist
        """
        endpoint = 'https://api.spotify.com/v1/users/{}/playlists'.format(self.user_id)
        request_body = json.dumps({
          "name": name
        })
        response = requests.post(url = endpoint, data = request_body, headers=self.authorization_header_2)
        return json.loads(response.text)


    def user_playlist_add_tracks(self, playlist_id, songs):
        """ add songs to playlist in spotify, returns dictionary if sucessful or not

            Parameters: 
                - playlist_id - id of the playlist
                - songs - list of the songs
        """
        if (len(songs)>0):
            songs = self.ids_to_uris(songs=songs)
            s_list = ','.join(songs)
            request_body = {
            "uris": s_list
            }
        else: 
            request_body = {}
        endpoint = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id)
        print(request_body)
        response = requests.post(url = endpoint, params= request_body, headers=self.authorization_header_3)
        return json.loads(response.text)
    
    def ids_to_uris(self, songs):
        """ converts the song ids to uri

            Parameters:
                - songs - list of songs
        """
        s_list = ','.join(songs)
        endpoint = 'https://api.spotify.com/v1/tracks'
        param = {
            'ids' : s_list,
        }
        response = requests.get(endpoint, headers=self.authorization_header, params=param)
        ret_list = []
        for song in json.loads(response.text)['tracks']:
            ret_list.append(song['uri'])
        return ret_list
