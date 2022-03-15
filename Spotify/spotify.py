import json
import random
import requests
from urllib.parse import quote



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
CLIENT_SIDE_URL = "https://soundcore.herokuapp.com"
SCOPE = "playlist-modify-public playlist-modify-private"
REDIRECT_URI = "{}/callback/spotify".format(CLIENT_SIDE_URL)
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


class SpotifyGenerator:
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
        auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
        return auth_url


    def refresh(self, auth_token):
        # Auth Step 4: Requests refresh and access tokens
        code_payload = {
            "grant_type": "authorization_code",
            "code": auth_token,
            "redirect_uri": REDIRECT_URI,
            'client_id': client_id,
            'client_secret': client_secret
        }
        post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)
        
        # Auth Step 5: Tokens are Returned to Application
        response_data = json.loads(post_request.text)
        access_token = response_data["access_token"]
        refresh_token = response_data["refresh_token"]
        token_type = response_data["token_type"]
        expires_in = response_data["expires_in"]

        # Auth Step 6: Use the access token to access Spotify API
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

        # create a dictionary of categories and its ids
        results = self.categories(country='US', limit=50)
        self.categories_dict = {}
        for i in results['categories']['items']:
            self.categories_dict[i['name']] = i['id']


    def get_categories(self):
        """
        get categories name in the dictionary
        """
        categories = []
        for name in self.categories_dict.keys():
            categories.append(name)
        return categories

    
    def get_songs(self,genres, no_playlist):
        """
        given a list of genres/ categories it will get the first no_playlist
        and retrieve all songs for it. this will return a list of song ids.
        """
        # declare variables
        songs_list = []

        # go through the genres
        for category in genres:
            # get ids of category
            category_id = self.categories_dict[category]

            # request the playlists of the category
            playlists_result = self.category_playlists(category_id)

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
                
                for song in songs_result['tracks']['items']:
                    if (song['track'] != None ):
                        if (song['track']['id'] not in songs_list):
                            songs_list.append(song['track']['id'])

        # return the list
        return songs_list


    def check_filters(self, song, features):
        # go through each features and check if song fits within it

        for feature in features.keys():
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
        """
        creates a playlist of songs, notice that only 100 songs can be added
        returns the link to playlist
        """
        # if there are too many songs cut it short
        if (len(songs) > 100):
            songs = songs[0:99]

        # make playlist
        results = self.user_playlist_create(name)
        playlist_url = results['external_urls']['spotify']
        playlist_id = results['id']

        # add songs
        self.user_playlist_add_tracks(playlist_id,songs)
        return playlist_url


    def generate_playlist(self, name, length_min, features, genres, no_playlist):
        list_of_songs = self.get_songs(genres, no_playlist)
        song_dictionary = self.filter_songs_list(list_of_songs,features)

        # choose the songs for the playlist that adds up to aroung the wanted length
        goal_length = 60000 * length_min
        list_of_id = list(song_dictionary.keys())
        songs_chosen = []
        reach_goal = True

        while(goal_length > 0):
            # get random id and remove from list
            id_chosen = random.choice(list_of_id)
            list_of_id.remove(id_chosen)

            songs_chosen.append(id_chosen)
            print('song added')
            goal_length -= int(song_dictionary[id_chosen])

            if(len(list_of_id) == 0 and goal_length > 0):
                reach_goal = False
                print('out')
                break

        # create the playlist
        url = self.create_playlist(songs_chosen, name)
        return reach_goal, url

    
    def categories(self, country, limit):
        endpoint = 'https://api.spotify.com/v1/browse/categories'
        param = {
            'country' : country,
            'limit' : limit
        }
        response = requests.get(endpoint, headers=self.authorization_header, params=param)
        return json.loads(response.text)


    def category_playlists(self, category_id):
        endpoint = 'https://api.spotify.com/v1/browse/categories/{}/playlists'.format(category_id)
        response = requests.get(endpoint, headers=self.authorization_header)
        return json.loads(response.text)


    def playlist(self, playlist_id):
        endpoint = 'https://api.spotify.com/v1/playlists/{}'.format(playlist_id)
        param = {
            'country' : 'US',
        }
        response = requests.get(endpoint, headers=self.authorization_header, params=param)
        return json.loads(response.text)


    def audio_features(self, song_list):
        s_list = ','.join(song_list)
        endpoint = 'https://api.spotify.com/v1/audio-features'
        param = {
            'ids' : s_list,
        }
        response = requests.get(endpoint, headers=self.authorization_header, params=param)
        return json.loads(response.text)


    def user_playlist_create(self, name):
        endpoint = 'https://api.spotify.com/v1/users/{}/playlists'.format(self.user_id)
        request_body = json.dumps({
          "name": name
        })
        response = requests.post(url = endpoint, data = request_body, headers=self.authorization_header_2)
        return json.loads(response.text)


    def user_playlist_add_tracks(self, playlist_id, songs):
        songs = self.ids_to_uris(songs=songs)
        s_list = ','.join(songs)
        endpoint = 'https://api.spotify.com/v1/playlists/{}/tracks'.format(playlist_id)
        request_body = {
          "uris": s_list
        }
        print(request_body)
        response = requests.post(url = endpoint, params= request_body, headers=self.authorization_header_3)
        return json.loads(response.text)
    
    def ids_to_uris(self, songs):
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
