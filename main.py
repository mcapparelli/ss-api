from fastapi import FastAPI
from source.user.application.router import router as user_router
from source.transfer.application.router import router as transfer_router

app = FastAPI(
    title="Simple Swap API",
    version="1.0.0"
)

app.include_router(user_router)
app.include_router(transfer_router)

@app.get("/health")
async def health_check():
    return { "status": "healthy" }