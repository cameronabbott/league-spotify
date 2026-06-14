from utils.helpers import euclidean_distance
def score_tracks(tracks, music_vectors, target_music_vector):
    scored_tracks = []
    for track, music_vector in zip(tracks, music_vectors):
        score = euclidean_distance(music_vector, target_music_vector)
        scored_tracks.append((track, score))
    scored_tracks.sort(key=lambda x: x[1])  # Sort by score (lower is better)
    return scored_tracks
    