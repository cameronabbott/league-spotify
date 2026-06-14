from utils.config import BAD_KEYWORDS
import re

def valid_track(track, genre):
    # track format (name, [artists], id)
    # temporary solution for kpop
    if genre == "kpop":
        genre = "k-pop"
    name, artists, id = track
    name_lower = name.lower()
    artists_lower = [artist.lower() for artist in artists]

    for keyword in BAD_KEYWORDS + [genre]:
        if keyword in name_lower or any(keyword in artist for artist in artists_lower):
            print("Discarding track due to bad keyword:", track)
            return False
    return True

def normalise_title(title):
    title = re.sub(r"\(.*?\)", "", title)
    title = re.sub(r"\[.*?\]", "", title)

    title = re.sub(r"\s*[-–—~]\s*", " - ", title)
    
    title = title.split(" - ")[0]

    return title.strip().lower()

def refine_tracks(tracks, genre):
    # removes duplicates + tracks with genre in artist or song name
    # track format (name, [artists], id)
    refined_tracks = {}
    for track in tracks:
        print("Processing track:", track)
        if valid_track(track, genre):
            normalised_title = normalise_title(track[0])
            if normalised_title in refined_tracks:
                if len(track[0]) < len(refined_tracks[normalised_title][0]):
                    refined_tracks[normalised_title] = track
            else:
                refined_tracks[normalised_title] = track

    return list(refined_tracks.values())
