from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.core.database import Base, engine
from app.models import entities

app = FastAPI(title="Word Dictation Learning API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)

@app.on_event("startup")
def create_tables_for_dev():
    Base.metadata.create_all(bind=engine)
