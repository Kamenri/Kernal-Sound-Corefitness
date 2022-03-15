from flask import Flask, render_template, request
import hashlib
import psycopg2
import os
import spotify

# connect to the database:
# note: to connect thru terminal: heroku pg:psql -a APPNAME
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

app = Flask(__name__)

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        USERNAME = request.form.get('username')
        PASSWORD = request.form.get('password')
        PASSWORD_HASH = hashlib.sha256(PASSWORD.encode('utf-8')).hexdigest()

        # check that user is in the database:
        cur.execute('SELECT * FROM USERDATA WHERE USERNAME = %s AND PASSWORD_HASH = %s', (USERNAME, PASSWORD_HASH,))
        row = cur.fetchone()
        if row is None:
            return render_template('errorpage.html', message='Error: Wrong username or password. Please try again.')
        else:
            # TODO: replace this
            return render_template('main.html', username=row[0])

@app.route('/signup', methods=['POST'])
def signup():
    return render_template('signup.html')

@app.route('/signup_process', methods=['POST'])
def signup_process():
    USERNAME = request.form.get('username')
    PASSWORD = request.form.get('password')
    PASSWORD_VERIFY = request.form.get('password_verify')
    FITBIT_CLIENT_ID = request.form.get('fitbit_client_id')
    FITBIT_CLIENT_SECRET = request.form.get('fitbit_client_secret')
    PASSWORD_HASH = hashlib.sha256(PASSWORD.encode('utf-8')).hexdigest()

    if PASSWORD != PASSWORD_VERIFY:
        return 'ERROR: passwords are not matching!'

    # insert user data to the database:
    cur.execute('INSERT INTO USERDATA (USERNAME, PASSWORD_HASH, FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET) VALUES (%s, %s, %s, %s)', (USERNAME, PASSWORD_HASH, FITBIT_CLIENT_ID, FITBIT_CLIENT_SECRET,))
    conn.commit()
    return 'sign up successful!'

# the main page
@app.route('/')
def index():
    return render_template('index.html')

# generating a playlist through spotify api:
@app.route('/make_playlist', methods=['POST'])
def make_playlist():
    name = 'Cool'
    length = 15
    features = {'tempo' : [100, 10], 'energy' : [.65, 10]}
    genres = ['Indie', 'Chill', 'Mood']
    no_playlist = 5

    sg = spotify.SpotifyGenerator()
    print('made the spotify generator')
    # reached_tm, url = sg.generate_playlist(name, length, features, genres, no_playlist)
    url='temp'
    return render_template('main.html', username=url)
