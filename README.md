# Spotify API Flask App

A Flask-based application to interact with the Spotify API. This app allows users to view their top tracks, recently played songs, playlists, and more.

---

## Features

- **Login with Spotify**: Authenticate using your Spotify account.
- **Top Songs**: View your top 50 songs with details like track name, artist, album, and duration.
- **Recently Played**: Check your 50 most recently played tracks.
- **Play Count Tracking**: (Optional) Tracks the number of times you’ve listened to each song.
- **Top Artists**: Explore your top 50 artists along with their genres and Spotify links.

---

## Setup and Installation

### Prerequisites

1. Python 3.9 or higher.
2. A Spotify Developer account with a registered app. ([Create one here](https://developer.spotify.com/dashboard/))
3. `pip` for installing dependencies.

---

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/spotify-api-flask.git
   cd spotify-api-flask
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Spotify app credentials:
   ```plaintext
   CLIENT_ID=your_spotify_client_id
   CLIENT_SECRET=your_spotify_client_secret
   REDIRECT_URI=http://localhost:3000/callback
   TOKEN_URL=https://accounts.spotify.com/api/token
   API_BASE_URL=https://api.spotify.com/v1/
   AUTH_URL=https://accounts.spotify.com/authorize
   SECRET_KEY=your_secret_key
   ```

4. Initialize the database (if tracking play counts):
   ```bash
   python -c "import main; main.init_db()"
   ```

---

### Running the App

1. Start the Flask server:
   ```bash
   python main.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:3000
   ```

---

## Endpoints

### Public Endpoints

| Endpoint             | Description                                     |
|----------------------|-------------------------------------------------|
| `/login`             | Redirects to Spotify login.                    |
| `/top-songs`         | Displays your top 50 tracks.                   |
| `/recently-played`   | Shows your most recently played tracks.         |
| `/top-artists`       | Lists your top artists with genres.            |
| `/playlists`         | Fetches and displays your Spotify playlists.   |

---

## Contribution

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Spotify API**: For providing a robust interface to access Spotify user data.
- **Flask**: A lightweight WSGI framework for Python.
- **SQLite**: A database solution for tracking play counts.

---

## Contact

For questions or feedback, contact:
- **Your Name**: your.email@example.com
- [GitHub Profile](https://github.com/yourusername)
