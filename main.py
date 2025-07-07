from fastapi import FastAPI
from source.user.application.router import router as user_router

app = FastAPI(
    title="Simple Swap API",
    version="1.0.0"
)

app.include_router(user_router)

@app.get("/health")
async def health_check():
    return { "status": "healthy" }