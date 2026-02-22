from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from routers import agent, auth

app = FastAPI()

# Con origen "*" no se puede usar allow_credentials=True (restricción CORS)
allow_any = CORS_ORIGINS == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=not allow_any,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth.router)
app.include_router(agent.router)


@app.get("/health")
def health():
    return {"status": "ok"}
