from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

app = FastAPI(title="AdShield AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP: ouvert à tout ; à restreindre en production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)