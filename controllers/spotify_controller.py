import secrets

from fastapi import HTTPException, Request
from fastapi.responses import RedirectResponse

from services.spotify_auth import (
    create_playlist_for_user,
    exchange_code_for_token,
    get_authorize_url,
)

SESSION_TOKEN_KEY = "spotify_token"
SESSION_AUTH_KEY = "spotify_authenticated"
SESSION_OAUTH_STATE_KEY = "spotify_oauth_state"


def spotify_login(request: Request):
    state = secrets.token_urlsafe(16)
    request.session[SESSION_OAUTH_STATE_KEY] = state
    return RedirectResponse(get_authorize_url(state=state))


def spotify_callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        return RedirectResponse(url="/?spotify_auth=error")

    if not code:
        raise HTTPException(status_code=400, detail="Missing Spotify authorization code.")

    expected_state = request.session.pop(SESSION_OAUTH_STATE_KEY, None)
    if not expected_state or state != expected_state:
        return RedirectResponse(url="/?spotify_auth=error")

    try:
        token_info = exchange_code_for_token(code)
    except Exception:
        return RedirectResponse(url="/?spotify_auth=error")

    request.session[SESSION_TOKEN_KEY] = token_info
    request.session[SESSION_AUTH_KEY] = True
    return RedirectResponse(url="/?spotify_auth=success")


def spotify_status(request: Request):
    return {"authenticated": bool(request.session.get(SESSION_AUTH_KEY))}


def spotify_create_playlist(request: Request, payload: dict):
    if not request.session.get(SESSION_AUTH_KEY):
        raise HTTPException(status_code=401, detail="Connect Spotify to unlock the full playlist.")

    token_info = request.session.get(SESSION_TOKEN_KEY)
    if not token_info:
        raise HTTPException(status_code=401, detail="Spotify session expired. Please log in again.")

    track_ids = payload.get("track_ids") or []
    riot_id = payload.get("riot_id") or "your profile"
    cluster = payload.get("cluster") or "league"

    if not track_ids:
        raise HTTPException(status_code=400, detail="No tracks provided.")

    try:
        playlist = create_playlist_for_user(
            token_info,
            track_ids,
            f"League Vibes — {riot_id}",
            f"Generated from {riot_id}'s ranked match history. Genre match: {cluster}.",
        )
    except Exception as error:
        raise HTTPException(status_code=502, detail=f"Could not create Spotify playlist: {error}")

    return playlist
