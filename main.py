import requests
import urllib.parse
from dotenv import load_dotenv
from flask import Flask, redirect, request, jsonify, session, render_template
from datetime import datetime
import os

# Load environment variables
load_dotenv()

# Validate required environment variables
REQUIRED_ENV_VARS = ["CLIENT_ID", "CLIENT_SECRET",
                     "REDIRECT_URI", "TOKEN_URL", "API_BASE_URL", "AUTH_URL"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing environment variable: {var}")

# Configuration
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
TOKEN_URL = os.getenv("TOKEN_URL")
API_BASE_URL = os.getenv("API_BASE_URL")
AUTH_URL = os.getenv("AUTH_URL")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(24))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"
    return redirect(auth_url)


@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})
    if 'code' not in request.args:
        return jsonify({"error": "Authorization code not provided"})

    req_body = {
        'code': request.args['code'],
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=req_body)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch token", "details": response.json()})

    token_info = response.json()
    session['access_token'] = token_info['access_token']
    session['refresh_token'] = token_info['refresh_token']
    session['expires_at'] = datetime.now().timestamp() + \
        token_info['expires_in']
    return redirect('/menu')


@app.route('/menu')
def menu():
    return render_template('menu.html')


@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')
    if float(datetime.now().timestamp()) > float(session['expires_at']):
        return redirect('/refresh-token')

    headers = {'Authorization': f"Bearer {session['access_token']}"}
    response = requests.get(f"{API_BASE_URL}me/playlists", headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch playlists", "details": response.json()})

    # Filtrar información relevante
    playlists = response.json().get('items', [])
    simplified_playlists = [
        {
            "name": playlist["name"],
            "image": playlist["images"][0]["url"] if playlist["images"] else None,
            "owner": playlist["owner"]["display_name"],
            "total_tracks": playlist["tracks"]["total"],
            "spotify_url": playlist["external_urls"]["spotify"]
        }
        for playlist in playlists if playlist
    ]
    print(simplified_playlists)

    # Renderizar la plantilla con datos
    return render_template('playlists.html', playlists=simplified_playlists)


@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')
    req_body = {
        'grant_type': 'refresh_token',
        'refresh_token': session['refresh_token'],
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(TOKEN_URL, data=req_body)
    if response.status_code != 200:
        return jsonify({"error": "Failed to refresh token", "details": response.json()})

    new_token_info = response.json()
    session['access_token'] = new_token_info['access_token']
    session['expires_at'] = datetime.now().timestamp() + \
        new_token_info['expires_in']
    return redirect('/playlists')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
