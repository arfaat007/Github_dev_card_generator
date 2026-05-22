from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
import os
from pathlib import Path

from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.genai import types

from agent import github_card_agent
from mcp_server import (
    scrape_github,
    analyze_profile,
    generate_card_html,
    save_card
)
app = FastAPI(title="GitHub Dev Card API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize ADK services
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()

# Create runner
runner = Runner(
    app_name="github_card_generator",
    agent=github_card_agent,
    session_service=session_service,
    memory_service=memory_service
)

# Create cards directory
BASE_DIR = Path(__file__).resolve().parent
CARDS_DIR = BASE_DIR / "static" / "cards"
CARDS_DIR.mkdir(parents=True, exist_ok=True)

# Mount static folder
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
# UI mount – placed after API routes (see end of file)
# app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")  # moved later


# Request schema
class CardRequest(BaseModel):
    username: str


# @app.get("/")
# async def root():
#     return {"message": "GitHub Dev Card API Running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/generate")
async def generate_card(request: CardRequest):
    try:
        username = request.username.strip()

        # Step 1
        github_data = await scrape_github(username)

        if github_data.get("error"):
            raise HTTPException(
                status_code=404,
                detail=github_data["error"]
            )

        # Step 2
        analysis = await analyze_profile(github_data)

        # Step 3
        html = await generate_card_html(
            username,
            github_data,
            analysis
        )

        # Step 4
        # Save the card and return a relative URL (frontend will resolve on the same origin)
        card_url = f"/static/cards/{username}.html"

        # Verify
        card_path = CARDS_DIR / f"{username}.html"

        if not card_path.exists():
            raise HTTPException(
                status_code=500,
                detail="HTML file was not created."
            )

        return {
            "username": username,
            "card_url": card_url,
            "html": html
        }

    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/card/{username}")
async def get_card(username: str):
    card_path = CARDS_DIR / f"{username}.html"

    if not card_path.exists():
        raise HTTPException(status_code=404, detail="Card not found")

    return FileResponse(card_path)
# Serve UI at root after API routes
app.mount("/", StaticFiles(directory=str(BASE_DIR / "frontend"), html=True), name="frontend")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=port,
        reload=True
    )
