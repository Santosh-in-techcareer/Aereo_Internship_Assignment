from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import Base, engine
from . import models
from .routes.files import router as files_router
from .routes.chat import router as chat_router


from sqlalchemy import text

Base.metadata.create_all(bind=engine)

# Auto-migrate schema updates for existing tables
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE features ADD COLUMN IF NOT EXISTS perimeter FLOAT;"))
    conn.commit()


app = FastAPI(
    title="Geospatial File Measurement & AI Assistant API",
    description="Backend service for uploading KML and Shapefile files, calculating spatial measurements, and chatting with AI.",
    version="1.0.0",
)


app.include_router(files_router)
app.include_router(chat_router)


app.mount(
    "/frontend",
    StaticFiles(
        directory="frontend",
        html=True
    ),
    name="frontend"
)


@app.get("/")
def root():
    return {
        "message": "Geospatial File Measurement API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }