from fastapi import FastAPI
from routes.match_routes import router as matches_router

app = FastAPI()

@app.get("/")
def home():
    return {"message": "running"}

app.include_router(matches_router)