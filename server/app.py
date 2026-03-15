"""FastAPI application for Daily Stack V4."""

from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from server import db

app = FastAPI(title="Daily Stack", version="4.0.0")

STATIC_DIR = Path(__file__).resolve().parent.parent


# --- Request models ---


class HabitRequest(BaseModel):
    date: str
    habit_id: str
    done: bool


class TextRequest(BaseModel):
    date: str
    text: str


class JournalRequest(BaseModel):
    date: str
    period: Literal["morning", "evening"]
    text: str


# --- API endpoints ---


@app.post("/api/habits")
def post_habit(req: HabitRequest):
    db.upsert_habit(req.date, req.habit_id, req.done)
    return {"ok": True}


@app.get("/api/habits/{date}")
def get_habits(date: str):
    return db.get_habits(date)


@app.post("/api/focus")
def post_focus(req: TextRequest):
    db.upsert_focus(req.date, req.text)
    return {"ok": True}


@app.get("/api/focus/{date}")
def get_focus(date: str):
    return db.get_focus(date)


@app.post("/api/reflection")
def post_reflection(req: TextRequest):
    db.upsert_reflection(req.date, req.text)
    return {"ok": True}


@app.get("/api/reflection/{date}")
def get_reflection(date: str):
    return db.get_reflection(date)


@app.post("/api/journal")
def post_journal(req: JournalRequest):
    db.upsert_journal(req.date, req.period, req.text)
    return {"ok": True}


@app.get("/api/journal/{date}")
def get_journal(date: str):
    return db.get_journal(date)


@app.get("/api/export")
def export_all():
    return db.export_all()


# --- Static file serving ---


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


# Mount static files for everything else (icons, manifest, sw.js, etc.)
app.mount("/", StaticFiles(directory=str(STATIC_DIR)), name="static")
