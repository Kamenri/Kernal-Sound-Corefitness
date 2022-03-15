from flask import Flask, request, redirect, g, render_template
import spotify

app = Flask(__name__)


sg = spotify.SpotifyGenerator()
# A welcome message to test our server
@app.route('/')
def index():
    # return "<h1>Welcome to our server !!</h1>"
    return render_template('main.html', username= 'Marmar')


# generating a playlist through spotify api:
@app.route('/make_playlist', methods=['POST'])
def make_playlist():
    auth_url = sg.authorize()
    return redirect(auth_url)


@app.route("/callback/spotify")
def callback():
    auth_token = str(request.args['code'])
    sg.refresh(auth_token)

    name = 'Cool'
    length = 10
    features = {'tempo' : [100, 10], 'energy' : [.65, 10]}
    genres = ['Indie', 'Chill', 'Mood']
    no_playlist = 5

    reached_tm, url = sg.generate_playlist(name, length, features, genres, no_playlist)
    # url = len(sg.get_categories())
    return render_template('main.html', username= url)
