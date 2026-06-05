from utils.config import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET
import requests

# flesh this out later, refresh the token etc, use better authentication
# i need seed tracks or generes... i need to map personality vector to those as well
# spotify recommendations is deprecated... need to find alternative
class SpotifyClient:
    def __init__(self):
        self.client_id = SPOTIFY_CLIENT_ID
        self.client_secret = SPOTIFY_CLIENT_SECRET
        self.access_token = self.get_new_token()
        self.token_expiry = None  

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

    def get_recommendations(self, spotify_vector, seed_genres=None, seed_tracks=None):
        headers = {
            "Authorization": f"Bearer {self.get_token()}"
        }
        url = "https://api.spotify.com/v1/recommendations"
        params = {
            "target_energy": spotify_vector["energy"],
            "target_danceability": spotify_vector["danceability"],
            "target_valence": spotify_vector["valence"],
            "target_instrumentalness": spotify_vector["instrumentalness"],
            "target_acousticness": spotify_vector["acousticness"],
            "seed_genres": "k-pop"
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching Spotify recommendations: {response.status_code} - {response.text}")
            return None
        return response.json()