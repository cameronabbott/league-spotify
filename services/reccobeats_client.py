import requests
import utils.helpers as helpers

class ReccoBeatsClient:
    def get_audio_features(self, ids):
        if len(ids) > 40:
            print("Error: Maximum of 40 track IDs allowed for audio features request.")
            return None
        
        url = f"https://api.reccobeats.com/v1/audio-features"
        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "ids": ids
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching ReccoBeats audio features: {response.status_code} - {response.text}")
            return None
        
        # energy, danceability, valence, tempo
        music_vectors = []
        for track in response.json().get("content", []):
            music_vectors.append([track['energy'], track['danceability'], track['valence'], track['tempo']])
            music_vectors[-1][3] = helpers.normalise(music_vectors[-1][3], 60, 170)  # normalise tempo to 0 - 1
            # print(f"Track ID: {track['id']}, Energy: {track['energy']}, Danceability: {track['danceability']}, Valence: {track['valence']}, Tempo: {track['tempo']}"  )
        return music_vectors
        