default = {'name' : 'DefaultSettings', 'length' : 15, 'features' : {'tempo' : [130, 10], 'energy' : [.65, 10]}, 'genres' : ['Indie', 'Chill', 'Mood'], 'no_playlist' : 5 }

genres = ['Top Lists', 'Hip Hop', 'Pop', 'Country', 'Workout', 'Rock', 
          'Latin', 'Shows with music', 'Mood', 'R&B', 'Happy Holidays', 
          'Gaming', 'RADAR', 'Focus', 'Dance/Electronic', 'Black History Is Now', 
          'Chill', 'At Home', 'Indie', 'Christian', 'Decades', 'Alternative', 'Student', 
          'Wellness', 'In the car', 'Pride', 'Party', 'Sleep', 'Classical', 'Jazz', 'Folk & Acoustic', 
          'Soul', 'Spotify Singles', 'Cooking & Dining', 'Sports', 'Romance', 'K-Pop', 'Punk', 'Regional Mexican', 
          'Pop culture', 'Arab', 'Desi', 'Anime', 'Tastemakers', 'Afro', 'Comedy', 'Metal', 'Caribbean', 'Blues', 'Funk', 
          'Commute', 'Kids & Family', 'Diwali', 'Instrumental']

#["Top Lists", "Hip Hop", "Pop", "Country", "Workout", "Rock", "Latin", "Shows with music", "Mood", "R&B", "Happy Holidays", "Gaming", "RADAR", "Focus", "Dance/Electronic", "Black History Is Now", "Chill", "At Home", "Indie", "Christian", "Decades", "Alternative", "Student", "Wellness", "In the car", "Pride", "Party", "Sleep", "Classical", "Jazz", "Folk & Acoustic", "Soul", "Spotify Singles", "Cooking & Dining", "Sports", "Romance", "K-Pop", "Punk", "Regional Mexican", "Pop culture", "Arab", "Desi", "Anime", "Tastemakers", "Afro", "Comedy", "Metal", "Caribbean", "Blues", "Funk", "Commute", "Kids & Family", "Diwali", "Instrumental"]

# some constants:
no_playlist_vals = {'Easy' : 5, 'Medium' : 6, 'Hard' : 7} # based on workout_intensity
tempo_vals = { 'Running' : {'Easy' : 100, 'Medium' : 130, 'Hard' : 160},
               'Cycling' : {'Easy' : 120, 'Medium' : 130, 'Hard' : 140},
               'Rowing' : {'Easy' : 110, 'Medium' : 120, 'Hard' : 130},
               'Bench' : {'Easy' : 120, 'Medium' : 130, 'Hard' : 140},
               'Dumbbells' : {'Easy' : 100, 'Medium' : 110, 'Hard' : 120},
               'ArmWokout' : {'Easy' : 100, 'Medium' : 130, 'Hard' : 160},
               'ChestWorkout' : {'Easy' : 100, 'Medium' : 130, 'Hard' : 160},
               'LegWorkout' : {'Easy' : 100, 'Medium' : 130, 'Hard' : 160},
               'GluteWorkout' : {'Easy' : 100, 'Medium' : 130, 'Hard' : 160}
             } # based on workout_intensity

wger_settings = {
    'Running' : ['LEGS','BUTT','CORE'],
    'Cycling' : ['LEGS','BUTT'],
    'Rowing' : ['BACK', 'ARMS'],
    'Bench' : ['CHEST', 'SHOULDERS'],
    'Dumbbells' : ['CHEST','BACK'],
    'ArmWokout' : ['ARMS'],
    'ChestWorkout' : ['CHEST','SHOULDERS','ARMS'],
    'LegWorkout' : ['LEGS','BUTT', 'CALF'],
    'GluteWorkout' : ['BUTT','CORE']
}

def choose_workout(workout_type, workout_intensity, workout_length, music_type,not_explicit):
    workout_settings = {'name' : 'GeneratedSetting',
                        'length' : int(workout_length),
                        'features' : {'tempo' : [tempo_vals[workout_type][workout_intensity], 10], 'energy' : [.65, 10]},
                        'genres' : music_type,
                        'no_playlist' : no_playlist_vals[workout_intensity],
                        'not_explicit' : not_explicit
                        } 
    return wger_settings[workout_type], workout_settings

genres_ids = {
    "Top Lists" : "toplists",
    "Hip Hop" : "hiphop",
    "Pop" : "pop",
    "Country" : "country",
    "Workout" : "workout",
    "Rock" : "rock",
    "Latin" : "latin",
    "Shows with music" : "shows_with_music",
    "Mood" : "mood",
    "R&B" : "rnb",
    "Happy Holidays" : "holidays",
    "Gaming" : "gaming",
    "RADAR" : "radar",
    "Focus" : "focus",
    "Dance/Electronic" : "edm_dance",
    "Black History Is Now" : "blackhistorymonth",
    "Chill" : "chill",
    "At Home" : "at_home",
    "Indie" : "indie_alt",
    "Christian" : "inspirational",
    "Decades" : "decades",
    "Alternative" : "alternative",
    "Student" : "student",
    "Wellness" : "wellness",
    "In the car" : "in_the_car",
    "Pride" : "pride",
    "Party" : "party",
    "Sleep" : "sleep",
    "Classical" : "classical",
    "Jazz" : "jazz",
    "Folk & Acoustic" : "roots",
    "Soul" : "soul",
    "Spotify Singles" : "sessions",
    "Cooking & Dining" : "dinner",
    "Sports" : "sports",
    "Romance" : "romance",
    "K-Pop" : "kpop",
    "Punk" : "punk",
    "Regional Mexican" : "regional_mexican",
    "Pop culture" : "popculture",
    "Arab" : "arab",
    "Desi" : "desi",
    "Anime" : "anime",
    "Tastemakers" : "thirdparty",
    "Afro" : "afro",
    "Comedy" : "comedy",
    "Metal" : "metal",
    "Caribbean" : "caribbean",
    "Blues" : "blues",
    "Funk" : "funk",
    "Commute" : "travel",
    "Kids & Family" : "family",
    "Diwali" : "diwali",
    "Instrumental" : "instrumental"
}