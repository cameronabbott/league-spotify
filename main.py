from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel, Field

from controllers.match_controller import recommend_tracks_for_player

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


class RecommendationRequest(BaseModel):
    riot_id: str = Field(..., min_length=3)
    region: str = Field(..., min_length=2)


@app.get("/")
def home():
    return HTMLResponse((FRONTEND_DIR / "index.html").read_text())

from fastapi.responses import RedirectResponse

@app.get("/{full_path:path}")
def catch_all(full_path: str):
    # don't interfere with API routes
    if full_path.startswith("api"):
        return {"detail": "Not found"}

    return RedirectResponse(url="/")

@app.post("/api/recommendations")
def get_recommendations(request: RecommendationRequest):
    return recommend_tracks_for_player(request.riot_id, request.region, limit=10)
