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
    scope = 'user-read-private user-read-email user-read-recently-played user-top-read '
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
    return redirect('/playlists')


@app.route('/playlists')
def get_playlists():
    os.system('cls' if os.name == 'nt' else 'clear')

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
    # Renderizar la plantilla con datos
    return render_template('playlists.html', playlists=simplified_playlists)


@app.route('/recently-played')
def recently_played():
    os.system('cls' if os.name == 'nt' else 'clear')

    if 'access_token' not in session:
        return redirect('/login')

    if float(datetime.now().timestamp()) > float(session['expires_at']):
        return redirect('/refresh-token')

    headers = {'Authorization': f"Bearer {session['access_token']}"}

    response = requests.get(
        f"{API_BASE_URL}me/player/recently-played?limit=50", headers=headers)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch recently played tracks', 'details': response.json()})

    # Parse the response
    tracks = response.json().get('items', [])
    recently_played_tracks = [
        {
            'track_name': item['track']['name'],
            'artist_name': ', '.join(artist['name'] for artist in item['track']['artists']),
            'album_name': item['track']['album']['name'],
            'image_url': item['track']['album']['images'][0]['url'] if item['track']['album']['images'] else None,
            'played_at': item['played_at'],
            'spotify_url': item['track']['external_urls']['spotify']
        }
        for item in tracks
    ]

    return render_template('recently_played.html', tracks=recently_played_tracks)


@app.route('/top-artists')
def top_artists():
    os.system('cls' if os.name == 'nt' else 'clear')

    if 'access_token' not in session:
        return redirect('/login')

    # Check if the token is expired
    if float(datetime.now().timestamp()) > float(session['expires_at']):
        return redirect('/refresh-token')

    headers = {'Authorization': f"Bearer {session['access_token']}"}

    # Fetch top artists
    response = requests.get(
        f"{API_BASE_URL}me/top/artists?limit=50", headers=headers)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch top artists', 'details': response.json()})

    # Parse the response
    artists = response.json().get('items', [])
    top_artists = [
        {
            'artist_name': artist['name'],
            'genres': ', '.join(artist['genres']),
            'image_url': artist['images'][0]['url'] if artist['images'] else None,
            'spotify_url': artist['external_urls']['spotify']
        }
        for artist in artists
    ]

    return render_template('top_artists.html', artists=top_artists)


@app.route('/top-songs')
def top_songs():
    os.system('cls' if os.name == 'nt' else 'clear')

    if 'access_token' not in session:
        return redirect('/login')

    # Check if the token is expired
    if float(datetime.now().timestamp()) > float(session['expires_at']):
        return redirect('/refresh-token')

    headers = {'Authorization': f"Bearer {session['access_token']}"}

    # Fetch top tracks
    response = requests.get(
        f"{API_BASE_URL}me/top/tracks?limit=50&time_range=medium_term", headers=headers)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch top tracks', 'details': response.json()})

    # Parse the response
    tracks = response.json().get('items', [])
    top_tracks = [
        {
            'track_name': track['name'],
            'artist_name': ', '.join(artist['name'] for artist in track['artists']),
            'album_name': track['album']['name'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'duration': track['duration_ms'] // 1000,  # Convert ms to seconds
            'spotify_url': track['external_urls']['spotify']
        }
        for track in tracks
    ]

    return render_template('/top_songs.html', tracks=top_tracks)


@app.route('/available-genres')
def available_genres():
    if 'access_token' not in session:
        return redirect('/login')

    headers = {'Authorization': f"Bearer {session['access_token']}"}
    response = requests.get(
        f"{API_BASE_URL}recommendations/available-genre-seeds", headers=headers)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch available genres', 'details': response.json()})

    valid_genres = response.json().get('genres', [])
    print("Valid Genres: ", valid_genres)  # For debugging
    return jsonify(valid_genres)


@app.route('/recommendations')
def recommendations():
    #  os.system('cls' if os.name == 'nt' else 'clear')

    if 'access_token' not in session:
        return redirect('/login')

    # Check if the token is expired
    if float(datetime.now().timestamp()) > float(session['expires_at']):
        return redirect('/refresh-token')

    headers = {'Authorization': f"Bearer {session['access_token']}"}

    # Fetch the user's top tracks and artists
    top_tracks_response = requests.get(
        f"{API_BASE_URL}me/top/tracks?limit=1", headers=headers)
    top_tracks = top_tracks_response.json().get(
        'items', []) if top_tracks_response.status_code == 200 else []

    top_artists_response = requests.get(
        f"{API_BASE_URL}me/top/artists?limit=1", headers=headers)
    top_artists = top_artists_response.json().get(
        'items', []) if top_artists_response.status_code == 200 else []

    # Prepare seeds for recommendations
    seed_tracks = [track['id'] for track in top_tracks]
    seed_artists = [artist['id'] for artist in top_artists]

    # Extract genres from top artists
    genres = []
    for artist in top_artists:
        genres.extend(artist.get('genres', []))

    # Count genre frequencies and pick the top 3 genres
    from collections import Counter
    genre_counts = Counter(genres)
    seed_genres = [genre for genre, _ in genre_counts.most_common(3)]

    # Fetch valid genres
    valid_genres_response = requests.get(
        f"{API_BASE_URL}recommendations/available-genre-seeds", headers=headers)
    valid_genres = valid_genres_response.json().get('genres', [])

    # Filter valid genres
    seed_genres = [genre for genre in seed_genres if genre in valid_genres]
    if not seed_genres:
        seed_genres = ['pop', 'rock', 'hip-hop']  # Default fallback genres

    print("Seed Tracks: ", seed_tracks)
    print("Seed Artists: ", seed_artists)
    print("Seed Genres: ", seed_genres)

    # Build query parameters
    params = []
    if seed_artists:
        params.append(f"seed_artists={','.join(seed_artists)}")
    if seed_genres:
        params.append(f"seed_genres={','.join(seed_genres)}")
    if seed_tracks:
        params.append(f"seed_tracks={','.join(seed_tracks)}")
    params.append("limit=100")
    query = '&'.join(params)

    print("*************************\nAPI Query:\n*********************************",
          f"{API_BASE_URL}recommendations?{query}")

    # Fetch recommendations
    response = requests.get(
        f"{API_BASE_URL}recommendations?{query}", headers=headers)

    if response.status_code != 200:
        print("API Error: ", response.status_code, response.text)
        return jsonify({'error': 'Failed to fetch recommendations', 'details': response.text})

    print("*************************\n RESPONSE:\n*********************************",
          response)

    # Parse recommendations
    recommendations = response.json().get('tracks', [])
    recommended_tracks = [
        {
            'track_name': track['name'],
            'artist_name': ', '.join(artist['name'] for artist in track['artists']),
            'album_name': track['album']['name'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'spotify_url': track['external_urls']['spotify']
        }
        for track in recommendations
    ]

    print("*************************\n RECOMMENDATIONS:\n*********************************",
          recommended_tracks)

    return render_template('recommendations.html', tracks=recommended_tracks)


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
