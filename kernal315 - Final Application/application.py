from flask import Flask, render_template, request, redirect, session
import hashlib
import psycopg2
import os
import spotify
import spotify_settings
import fitbit
import wger as wg

# connect to the database:
# note: to connect thru terminal: heroku pg:psql -a APPNAME
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
sg = spotify.SpotifyGenerator()
fd = fitbit.FitbitData()
app = Flask(__name__)
usersetting = spotify_settings.default
app.secret_key = 'dljsaklqk24e21cjn!Ew@@dsa5'

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    session['spotify_generated'] = False
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        session["username"] = request.form.get('username')
        PASSWORD = request.form.get('password')
        PASSWORD_HASH = hashlib.sha256(PASSWORD.encode('utf-8')).hexdigest()

        # check that user is in the database:
        cur.execute('SELECT * FROM USERDATA WHERE USERNAME = %s AND PASSWORD_HASH = %s', (session["username"], PASSWORD_HASH,))
        row = cur.fetchone()
        if row is None:
            return render_template('errorpage.html', message='Error: Wrong username or password. Please try again.')
        else:
            # update access token and refresh token
            f_refresh_token = row[3]
            fitbit_refresh_token = fd.refresh(f_refresh_token)
            if (fitbit_refresh_token == 'error'):
                auth_url = fd.authorize()
                return redirect(auth_url)
            if(len(f_refresh_token) > 0):
                cur.execute('UPDATE USERDATA SET FITBIT_REFRESH = %s WHERE USERNAME = %s AND PASSWORD_HASH = %s',(fitbit_refresh_token, session['username'], PASSWORD_HASH))
                conn.commit()
            session['list_activities'] = fd.get_past_activities()
            session['converted_act'] = fd.createJSON(session['list_activities'])
            print(session['converted_act'])
            session['tabon'] = "defaultOpen"
            return render_template('main.html', username=session["username"], fitbit_data = session['converted_act'],wger_data = {},spotifyURL=None, tabon=session['tabon'])

@app.route('/signup', methods=['POST'])
def signup():
    return render_template('signup.html')

@app.route('/signin_page', methods=['POST'])
def signin_page():
    return render_template('signin.html')

@app.route('/signup_process', methods=['POST'])
def signup_process():
    session['spotify_generated'] = False
    session["username"] = request.form.get('username')
    PASSWORD = request.form.get('password')
    PASSWORD_VERIFY = request.form.get('password_verify')

    PASSWORD_HASH = hashlib.sha256(PASSWORD.encode('utf-8')).hexdigest()

    if PASSWORD != PASSWORD_VERIFY:
        return 'ERROR: passwords are not matching!'

    # add userdata to database
    cur.execute('INSERT INTO USERDATA (USERNAME, PASSWORD_HASH, SPOTIFY_REFRESH, FITBIT_REFRESH) VALUES (%s, %s, %s, %s)', (session['username'], PASSWORD_HASH, "na", "na",))
    conn.commit()

    auth_url = sg.authorize()
    return redirect(auth_url)

# the main page
@app.route('/')
def index():
    return render_template('index.html')

# generating a playlist through spotify api:
@app.route('/make_playlist', methods=['POST'])
def make_playlist():
    # session['wger'] = {}
    # get the data from the dropdown menus:
    workout_type = request.form.get('workout_type')
    workout_length = request.form.get('workout_length')
    workout_intensity = request.form.get('workout_intensity')
    run_time = request.form.get('RunTime') 
    if (request.form.get('not_explict')):
        not_explicit = True
    else:
        not_explicit = False
    if(request.form.get("protanopia")):
        session["color"] = "protanopia"
    elif(request.form.get("deuteranopia")):
        session["color"] = "deuteranopia"
    else:
        session["color"] = "none"
    print(session["color"],'---------------------------------------------------')
    music_type = []
    for genre in spotify_settings.genres:
        if request.form.get(genre):
            music_type.append(genre)
    wger_settings = []
    if run_time is None:
        run_time = ''

    if(run_time != ''): #if text box is not empty
        session['tabon'] = "defaultOpen3"
        CalculatedAvgRate = fd.get_rate(session['list_activities']) #new lines   m/s
        workout_type = 'Running'
        if(CalculatedAvgRate <= 1.341116667):
            CalculatedTime = ((float(run_time) * 1609.34) / float(1.341116667)) / 60 #new line 1 mi = 1609.34 meters => divide by 60 to convert to minutes
            wger_settings, usersetting = spotify_settings.choose_workout(workout_type, workout_intensity, CalculatedTime, music_type,not_explicit)
        elif(CalculatedAvgRate > 1.341116667 ):
            CalculatedTime = ((float(run_time) * 1609.34) / float(CalculatedAvgRate)) / 60 #new line 1 mi = 1609.34 meters => divide by 60 to convert to minutes
            wger_settings, usersetting = spotify_settings.choose_workout(workout_type, workout_intensity, CalculatedTime, music_type,not_explicit)
    elif(run_time == ''):
        # pick the workout for the user:
        session['tabon'] = "defaultOpen2"
        wger_settings, usersetting = spotify_settings.choose_workout(workout_type, workout_intensity, workout_length, music_type,not_explicit)

    session['wger'] = wg.get_exercise(wger_settings,3)
    print(session['wger'])

    # get refresh token
    cur.execute('SELECT * FROM USERDATA WHERE USERNAME = %s', (session['username'],))
    row = cur.fetchone()

    refresh_token = str(row[2])

    refresh_token = sg.refresh(refresh_token)
    if (refresh_token == 'error'):
        session['spotify_generated'] = True
        session['spotify_settings'] = usersetting
        auth_url = sg.authorize()
        return redirect(auth_url)

    # update to a new refresh token if necesarry
    if(len(refresh_token) > 0):
        cur.execute('UPDATE USERDATA SET SPOTIFY_REFRESH = %s WHERE USERNAME = %s',(refresh_token, session['username']))
        conn.commit()

    reached_tm, url = sg.generate_playlist(usersetting['name'],
                usersetting['length'], usersetting['features'],
                usersetting['genres'], usersetting['no_playlist'],
                usersetting['not_explicit'])

    # authorize spotify and generate the playlist:
    return render_template('main.html', username= session['username'], fitbit_data = session['converted_act'], spotifyURL= url, wger_data = session['wger'],tabon=session['tabon'], colorblind = session["color"])


@app.route("/callback/spotify")
def callback_spotify():
    auth_token = str(request.args['code'])
    refresh_token = sg.get_refresh_token(auth_token)
    cur.execute('UPDATE USERDATA SET SPOTIFY_REFRESH = %s WHERE USERNAME = %s',(refresh_token, session['username']))
    conn.commit()

    if(session['spotify_generated']):
        session['spotify_generated'] = False
        usersetting = session['spotify_settings']
        reached_tm, url = sg.generate_playlist(usersetting['name'],
                usersetting['length'], usersetting['features'],
                usersetting['genres'], usersetting['no_playlist'],
                usersetting['not_explicit'])
        return render_template('main.html', username= session['username'], fitbit_data = session['converted_act'], spotifyURL= url, wger_data = session['wger'],tabon=session['tabon'], colorblind = session["color"])

    auth_url = fd.authorize()
    return redirect(auth_url)


@app.route("/callback/fitbit")
def callback_fitbit():
    auth_token = str(request.args['code'])
    fitbit_refresh_token = fd.get_refresh_token(auth_token)

    cur.execute('UPDATE USERDATA SET FITBIT_REFRESH = %s WHERE USERNAME = %s',(fitbit_refresh_token, session['username'],))
    conn.commit()

    session['tabon'] = "defaultOpen"
    session['list_activities'] = fd.get_past_activities()
    session['converted_act'] = fd.createJSON(session['list_activities'])
    return render_template('main.html', username=session["username"], fitbit_data = session['converted_act'],wger_data = {},spotifyURL=None,tabon=session['tabon'])
