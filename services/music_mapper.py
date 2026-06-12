from utils.helpers import clamp, jitter, cosine_similarity, euclidean_distance
from utils.config import MUSIC_CLUSTER_VECTORS


# changed to tempo and removed instrumentalness since it was too dependent on genre, often was 0
# tempo is normalsied from 0 to 1
# changed to see if better cluster serparation
def music_vector(personality_vector, win_norm):
    # energy, danceability, valence, tempo
    # more scaling + control = high, tempo = game urgency
    music_vector = [personality_vector["aggression"],
                    personality_vector["teamwork"],
                    personality_vector["stability"],
                    (1 - personality_vector["scaling"]) * 0.6 + 0.4 * (1 - personality_vector["control"])]
    # winrate nudge
    music_vector[0] = clamp(music_vector[0] * 0.9 + 0.2 * win_norm, 0, 1)

    print(f"Music Vector before jitter: {music_vector}\n")
    
    for i in range(len(music_vector)):
        music_vector[i] = clamp(jitter(music_vector[i], amount=0.05), 0, 1)

    print(f"Music Vector: {music_vector}\n")
    return music_vector


def music_vector_calculator(arr_music_vectors):
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

# if we only do cosine_similarity, [0.2, 0.2, 0.2, 0.2] is the same as [0.8, 0.8, 0.8, 0.8]
# need to add something to consider magnitude
# not sure if this right way to do it though
# if we have low values for a music vector feel like it should map to genre with generally lower values 
# euclidean distance to deal with this
def music_vector_to_cluster(music_vector):
    best_score = -1
    best_cluster = None
    for cluster_name, cluster_vector in MUSIC_CLUSTER_VECTORS.items():
        cosine = cosine_similarity(music_vector, cluster_vector)
        euclidean_norm = euclidean_distance(music_vector, cluster_vector) / 2  # normalise to [0, 1]
        score = cosine - 0.3 * euclidean_norm
        if score > best_score:
            best_score = score
            best_cluster = cluster_name
    print(f"Best Cluster: {best_cluster} with score {best_score}\n")
    return best_cluster

