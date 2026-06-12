from utils.helpers import clamp, jitter

# changed to tempo and removed instrumentalness since it was too dependent on genre, often was 0
# tempo is normalsied from 0 to 1
def music_vector(personality_vector, win_norm):
    music_vector = {
        "energy": 0.7 * personality_vector["aggression"] + 0.3 * personality_vector["control"],
        "danceability": 0.6 * personality_vector["teamwork"] + 0.4 * personality_vector["aggression"],
        "valence": 0.4 * personality_vector["stability"] + 0.6 * personality_vector["teamwork"],
        "tempo": 0.4 * personality_vector["scaling"] + 0.6 * personality_vector["control"]
    }
    # winrate nudge
    music_vector["energy"] = clamp(music_vector["energy"] * 0.9 + 0.2 * win_norm, 0, 1)

    print(f"Music Vector before jitter: {music_vector}\n")
    
    for key in music_vector:
        music_vector[key] = clamp(jitter(music_vector[key], amount=0.05), 0, 1)

    print(f"Music Vector: {music_vector}\n")
    return music_vector


def genre_calculator(arr_music_vectors):
    average_music_vector = [sum(values)/len(values) for values in zip(*arr_music_vectors)]
    minimum_music_vector = [min(values) for values in zip(*arr_music_vectors)]
    maximum_music_vector = [max(values) for values in zip(*arr_music_vectors)]
    median_music_vector = [sorted(values)[len(values) // 2] for values in zip(*arr_music_vectors)]
    # print(f"Average Music Vector: {average_music_vector}\n")
    # print(f"Minimum Music Vector: {minimum_music_vector}\n")
    # print(f"Maximum Music Vector: {maximum_music_vector}\n")
    # print(f"Median Music Vector: {median_music_vector}\n")
    # return average
    return average_music_vector