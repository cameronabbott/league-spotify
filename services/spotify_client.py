from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from utils.config import MUSIC_CLUSTER_TO_SPOTIFY_SERACH

# flesh this out later, refresh the token etc, use better authentication
# i need seed tracks or generes... i need to map personality vector to those as well
# spotify recommendations is deprecated... need to find alternative
class SpotifyClient:
    def __init__(self):
        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET
        # self.access_token = None
        self.access_token = self.get_new_token()
        self.token_expiry = None  
        # self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        #     client_id=SPOTIFY_CLIENT_ID,
        #     client_secret=SPOTIFY_CLIENT_SECRET,
        #     redirect_uri="http://127.0.0.1:8888/callback",
        #     scope="playlist-read-private playlist-read-collaborative",
        #     open_browser=False
        # ))

        # print("Open this link in browser:")
        # print(self.sp.auth_manager.get_authorize_url())

        # input("Press Enter after login...")

        # self.sp.current_user()  # ensures auth is complete

        # print("Authenticated!")
    def get_new_token(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code != 200:
            print(f"Error fetching Spotify token: {response.status_code} - {response.text}")
            return None
        self.token_expiry = response.json().get("expires_in")
        return response.json().get("access_token")

    def get_token(self):
        # Implement token refresh logic if needed
        return self.access_token

    def authenticate(self):
        # Implement Spotify authentication flow to get access token
        pass

    
    # must be owned by the authenticated user or collaborative playlist
    def get_playlist_items(self, playlist_id, limit=40):
        tracks = self.sp.playlist_items(playlist_id, limit=limit)["items"]

        return [(track["item"]["name"], track["item"]["artists"][0]["name"], track["item"]["id"]) for track in tracks]
    
    def get_playlist(self, playlist_id):
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"

        headers = {
            "Authorization": f"Bearer {self.get_token()}"
        }

        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching Spotify playlist tracks: {response.status_code} - {response.text}")
            return None
        return response.json()

    # Example: q=remaster%2520track%3ADoxy%2520artist%3AMiles%2520Davis
    # yeah using the genre is terrible
    # seraching just for kpop is better than using q
    def search(self, genre):
        search_query = MUSIC_CLUSTER_TO_SPOTIFY_SERACH.get(genre)
        if search_query is None:
            print(f"Error: No Spotify search query found for genre '{genre}'")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.get_token()}"
        }
        url = "https://api.spotify.com/v1/search"
        params = {
            "q": search_query,
            "type": "track",
            "limit": 2
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error searching Spotify: {response.status_code} - {response.text}")
            return None
        return response.json()