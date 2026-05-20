from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.heatmap import router as heatmap_router

app = FastAPI(title="Correlation Heatmap Tool")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(heatmap_router)


@app.get("/")
async def root():
    return {"message": "Correlation Heatmap API"}
