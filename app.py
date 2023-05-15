#!/usr/bin/python3

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, url_for, session, request, redirect
import json
import time
import pandas as pd

# App config
app = Flask(__name__)

app.secret_key = 'f0a7d5f87cc24ac9aa7647553b7c32b8'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

@app.route('/authorize')
def authorize():
    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session["token_info"] = token_info
    return redirect("/getTracks")

@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')

@app.route('/getTracks')
def get_all_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    # while True:
    #     offset = iter * 50
    #     iter += 1
    curGroup = sp.current_user_saved_tracks(limit=50)['items']
    return curGroup
        # for idx, item in enumerate(curGroup):
        #     track = item['track']
        #     val = track['name'] + " - " + track['artists'][0]['name']
        #     results += [val]
        # if (len(curGroup) < 50):
        #     break
    
    df = pd.DataFrame(results, columns=["song names"]) 
    df.to_csv('songs.csv', index=False)
    return "done"

@app.route('/getRecentTracks')
def get_recent_tracks():
    session['token_info'], authorized = get_token()
    session.modified = True
    if not authorized:
        return redirect('/')
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = []
    iter = 0
    # while True:
    #     offset = iter * 50
    #     iter += 1
    curGroup = sp.current_user_recently_played(limit=50)['items']
    for idx, item in enumerate(curGroup):
        track = item['track']
        val = track['name'] + " - " + track['artists'][0]['name']
        results += [val]
    # if (len(curGroup) < 50):
    #     break

    df = pd.DataFrame(results, columns=["song names"]) 
    df.to_csv('songs.csv', index=False)
    return results

# Checks to see if token is valid and gets a new token if not
def get_token():
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))

    token_valid = True
    return token_info, token_valid


def create_spotify_oauth():
    return SpotifyOAuth(
            client_id="b834e40874cd4cbaa48507238730ce31",
            client_secret="f0a7d5f87cc24ac9aa7647553b7c32b8",
            redirect_uri=url_for('authorize', _external=True),
            scope="user-library-read user-read-recently-played")

if __name__ == "__main__":
    app.run(port="8080")