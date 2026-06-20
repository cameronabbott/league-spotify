import os
import secrets

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET

SPOTIFY_REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8000/api/spotify/callback"
)
SPOTIFY_SCOPES = (
    "playlist-modify-public "
    "playlist-modify-private "
    "user-read-private "
    "user-read-email"
)


def build_oauth_manager():
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SPOTIFY_SCOPES,
        show_dialog=True,
        open_browser=False,
        cache_path=None,
    )


def get_authorize_url(state=None):
    oauth = build_oauth_manager()
    return oauth.get_authorize_url(state=state or secrets.token_urlsafe(16))


def exchange_code_for_token(code):
    oauth = build_oauth_manager()
    return oauth.get_access_token(code, as_dict=True)


def spotify_client_from_token(token_info):
    return spotipy.Spotify(auth=token_info["access_token"])


def create_playlist_for_user(token_info, track_ids, playlist_name, description):
    print("SCOPES:", token_info.get("scope"))
    if not track_ids:
        return None

    sp = spotify_client_from_token(token_info)
    user = sp.current_user()
    print("USER OBJECT:", sp.current_user())
    print("ME OBJECT:", sp.me())
    playlist = sp.current_user_playlist_create(
        name=playlist_name,
        public=True,
        collaborative=False,
        description=description
    )

    uris = [f"spotify:track:{track_id}" for track_id in track_ids]
    for offset in range(0, len(uris), 100):
        sp.playlist_add_items(playlist["id"], uris[offset : offset + 100])

    return {
        "playlist_id": playlist["id"],
        "playlist_url": playlist["external_urls"]["spotify"],
        "playlist_name": playlist["name"],
    }
