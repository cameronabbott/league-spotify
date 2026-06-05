from utils.helpers import clamp, jitter

def map_to_spotify(personality_vector, win_norm):
    spotify_vector = {
        "energy": 0.7 * personality_vector["aggression"] + 0.3 * personality_vector["control"],
        "danceability": 0.6 * personality_vector["teamwork"] + 0.4 * personality_vector["aggression"],
        "valence": 0.4 * personality_vector["stability"] + 0.6 * personality_vector["teamwork"],
        "instrumentalness": 0.4 * personality_vector["scaling"] + 0.6 * personality_vector["control"],
        "acousticness": 0.7 * personality_vector["stability"] + 0.3 * personality_vector["scaling"],
    }
    # winrate nudge
    spotify_vector["energy"] = clamp(spotify_vector["energy"] * 0.9 + 0.2 * win_norm, 0, 1)

    print(f"Spotify Vector before jitter: {spotify_vector}\n")
    
    for key in spotify_vector:
        spotify_vector[key] = clamp(jitter(spotify_vector[key], amount=0.05), 0, 1)

    print(f"Spotify Vector: {spotify_vector}\n")
    return spotify_vector
