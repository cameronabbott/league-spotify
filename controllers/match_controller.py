from fastapi import HTTPException

from utils.config import REGION_TO_ROUTING

UNEXPECTED_API_ERROR = "Unexpected error found. Please try again later."


def split_riot_id(riot_id):
    if "#" not in riot_id:
        raise HTTPException(
            status_code=400,
            detail="Use a Riot ID in the format GameName#TAG.",
        )

    game_name, tag_line = riot_id.split("#", 1)
    game_name = game_name.strip()
    tag_line = tag_line.strip()

    if not game_name or not tag_line:
        raise HTTPException(
            status_code=400,
            detail="Use a Riot ID in the format GameName#TAG.",
        )

    return game_name, tag_line


def format_track(scored_track):
    track, score = scored_track
    name, artists, spotify_id = track
    return {
        "name": name,
        "artists": artists,
        "spotify_id": spotify_id,
        "spotify_url": f"https://open.spotify.com/track/{spotify_id}",
        "score": round(score, 4),
    }


def recommend_tracks_for_player(riot_id, region, limit=10):
    region = region.upper().strip()

    if region not in REGION_TO_ROUTING:
        raise HTTPException(status_code=400, detail="That region is not supported.")

    game_name, tag_line = split_riot_id(riot_id)

    from services.feature_engine import (
        build_average_vector,
        build_personality_vector,
        NotEnoughValidMatches,
        obtain_normalised_vector,
    )
    from services.music_mapper import music_vector, music_vector_to_cluster
    from services.ranker import score_tracks
    from services.reccobeats_client import ReccoBeatsClient
    from services.riot_service import get_matches, get_puuid, RiotApiError
    from services.spotify_client import SpotifyClient
    from services.track_processor import refine_tracks

    try:
        puuid = get_puuid(game_name, tag_line)
    except RiotApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)

    if not puuid:
        raise HTTPException(status_code=404, detail="Could not find that Riot account.")

    try:
        matches = get_matches(puuid, region, count=10)
    except RiotApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)

    if not matches:
        raise HTTPException(
            status_code=404,
            detail="No recent ranked solo/duo matches found for that account.",
        )

    try:
        average_vector = build_average_vector(
            puuid,
            matches,
            region,
            min_valid_matches=5,
        )
    except RiotApiError as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail)
    except NotEnoughValidMatches as error:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Not enough valid ranked matches. Found {error.valid_matches} "
                f"valid matches out of {error.checked_matches}; need at least "
                f"{error.required_matches}."
            ),
        )

    if not average_vector:
        raise HTTPException(
            status_code=422,
            detail="Could not build a profile from the recent matches.",
        )

    normalised_vector = obtain_normalised_vector(average_vector)
    personality_vector = build_personality_vector(
        normalised_vector,
        average_vector["role"],
        average_vector["archetype"],
    )
    target_music_vector = music_vector(personality_vector, average_vector["win"])
    cluster = music_vector_to_cluster(target_music_vector)

    spotify_client = SpotifyClient()
    spotify_tracks = spotify_client.search(cluster, limit=10, max_pages=4)

    if not spotify_tracks:
        raise HTTPException(
            status_code=502,
            detail=UNEXPECTED_API_ERROR,
        )

    refined_tracks = refine_tracks(spotify_tracks, cluster)
    track_ids = [track[2] for track in refined_tracks]
    music_vectors = ReccoBeatsClient().get_audio_features(track_ids)

    if not music_vectors:
        raise HTTPException(
            status_code=502,
            detail=UNEXPECTED_API_ERROR,
        )

    scored_tracks = score_tracks(refined_tracks, music_vectors, target_music_vector)
    recommendations = [format_track(track) for track in scored_tracks[:limit]]

    return {
        "riot_id": f"{game_name}#{tag_line}",
        "region": region,
        "cluster": cluster,
        "music_vector": [round(value, 4) for value in target_music_vector],
        "recommendations": recommendations,
    }
