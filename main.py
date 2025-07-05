from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Simple Swap API",
    version="1.0.0"
)

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Importar y registrar routers
# from source.user.application.use_cases.create_user.controller import router as user_router
# app.include_router(user_router)

@app.get("/health")
async def health_check():
    return { "status": "healthy" }