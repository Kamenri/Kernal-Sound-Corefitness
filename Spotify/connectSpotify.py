import json
import random
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth


class SpotifyGenerator:
    def __init__(self):
        """
        Create a connection to spotify server and create the list of genres
        """
        CLIENT_ID = 'c5e8920929564a4189b2a238ec4df8c9'
        CLIENT_SECRET = 'e29ae4fb338e4ceb99f324ba4d2841da'

        scope = 'playlist-modify-private,playlist-modify-public'
        token = util.prompt_for_user_token(client_id= CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri='http://127.0.0.1:9090',scope=scope)

        self.sp = spotipy.Spotify(auth = token)

        # create a dictionary of categories and its ids
        results = self.sp.categories(country='US',limit = 50)
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
            playlists_result = self.sp.category_playlists(category_id)
            
            # create a list of playlist ids
            p_id_list = []
            for playlist in playlists_result['playlists']['items']:
                p_id_list.append(playlist['id'])
            
            # we can decide which playlist to chose 
            # this will pick the first no_playlist or less depending on size of list
            for i in range(0, min(no_playlist , len(p_id_list))):
                # request songs in playlist
                songs_result = self.sp.playlist(p_id_list[i])

                # add the songs to list if it does not exist in the list
                for song in songs_result['tracks']['items']:
                    if (song['track'] != None ):
                        if (song['track']['id'] not in songs_list):
                            songs_list.append(song['track']['id'])
        
        # return the list
        return songs_list
    

    # feature would be a dictionary of string for the name of feature and a list of 
    # 2 integers first being the goal and second being the tolerence

    def check_filters(self, song, features):
        # go through each features and check if song fits within it
        for feature in features.keys():
            # get feature being measured
            value = song[feature]
            
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
            songs_result = self.sp.audio_features(songs_list[i : i + 100])
            
            # iterate through the list of song features dictionary
            for song in songs_result:
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
        results = self.sp.user_playlist_create('0qzh263pzjkbr9gc4q6zdpkn2',name)
        playlist_url = results['external_urls']['spotify']
        playlist_id = results['id']

        # add songs
        self.sp.user_playlist_add_tracks('0qzh263pzjkbr9gc4q6zdpkn2',playlist_id,songs)
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

            goal_length -= int(song_dictionary[id_chosen])

            if(len(list_of_id) == 0 and goal_length > 0):
                reach_goal = False
                break
        
        # create the playlist
        url = self.create_playlist(songs_chosen, name)
        return reach_goal, url

# test
name = 'Cool'
length = 15
features = {'tempo' : [100, 10], 'energy' : [.65, 10]}
genres = ['Indie', 'Chill', 'Mood']
no_playlist = 10

sg = SpotifyGenerator()
reached_tm, url = sg.generate_playlist(name, length, features, genres, no_playlist)
print(url)