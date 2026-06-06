from utils.helpers import clamp, jitter

def music_vector(personality_vector, win_norm):
    music_vector = {
        "energy": 0.7 * personality_vector["aggression"] + 0.3 * personality_vector["control"],
        "danceability": 0.6 * personality_vector["teamwork"] + 0.4 * personality_vector["aggression"],
        "valence": 0.4 * personality_vector["stability"] + 0.6 * personality_vector["teamwork"],
        "instrumentalness": 0.4 * personality_vector["scaling"] + 0.6 * personality_vector["control"],
        "acousticness": 0.7 * personality_vector["stability"] + 0.3 * personality_vector["scaling"],
    }
    # winrate nudge
    music_vector["energy"] = clamp(music_vector["energy"] * 0.9 + 0.2 * win_norm, 0, 1)

    print(f"Music Vector before jitter: {music_vector}\n")
    
    for key in music_vector:
        music_vector[key] = clamp(jitter(music_vector[key], amount=0.05), 0, 1)

    print(f"Music Vector: {music_vector}\n")
    return music_vector
