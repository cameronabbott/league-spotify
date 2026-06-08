import requests

class ReccoBeatsClient:
    def get_audio_features(self, ids):
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
        return response.json()