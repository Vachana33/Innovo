from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth
from app.routers.files import router as files_router
from app.routers import funding_programs
from app.routers import templates

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", # local frontend
        "http://localhost:5174", # local frontend
    
        "https://innovo-5kis.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(files_router)
app.include_router(funding_programs.router)
app.include_router(templates.router)

@app.get("/health")
def health():
    return {"status": "ok"}
