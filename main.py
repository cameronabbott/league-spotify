import os
import secrets

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field
from starlette.middleware.sessions import SessionMiddleware

from controllers.match_controller import recommend_tracks_for_player
from controllers.spotify_controller import (
    spotify_callback,
    spotify_create_playlist,
    spotify_login,
    spotify_status,
)

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

SESSION_SECRET = os.getenv("SESSION_SECRET") or secrets.token_hex(32)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class RecommendationRequest(BaseModel):
    riot_id: str = Field(..., min_length=3)
    region: str = Field(..., min_length=2)


class CreatePlaylistRequest(BaseModel):
    track_ids: list[str] = Field(..., min_length=1)
    riot_id: str = Field(..., min_length=3)
    cluster: str = Field(..., min_length=2)


@app.get("/")
def home():
    return HTMLResponse((FRONTEND_DIR / "index.html").read_text())


@app.post("/api/recommendations")
def get_recommendations(request: RecommendationRequest):
    return recommend_tracks_for_player(request.riot_id, request.region, limit=15)


@app.get("/api/spotify/login")
def login_with_spotify(request: Request):
    return spotify_login(request)


@app.get("/api/spotify/callback")
def spotify_oauth_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    return spotify_callback(request, code=code, state=state, error=error)


@app.get("/api/spotify/status")
def get_spotify_status(request: Request):
    return spotify_status(request)


@app.post("/api/spotify/create-playlist")
def create_spotify_playlist(request: Request, payload: CreatePlaylistRequest):
    return spotify_create_playlist(request, payload.model_dump())


@app.get("/{full_path:path}")
def catch_all(full_path: str):
    if full_path.startswith("api"):
        return {"detail": "Not found"}

    return RedirectResponse(url="/")
