from fastapi import FastAPI
from src.api import main_router as APIRouter
from src.sse import main_router as SSERouter
import os
from src.events import startup, shutdown
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()



@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup(app)
    try:
        yield
    finally:
        await shutdown(app)


from src.middlewares import middlewares_to_apply

# Add middlewares in reverse order they were discovered
# FastAPI executes the LAST added middleware FIRST for incoming requests.
for middleware in reversed(middlewares_to_apply):
    app.add_middleware(middleware)

# Add CORS middleware LAST so it executes FIRST to catch preflight
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(APIRouter)
app.include_router(SSERouter)

if __name__ == "__main__":
    import uvicorn

    DEFAULT_PORT = "3030"
    try:
        port = int(os.environ.get("PORT", DEFAULT_PORT))
    except Exception:
        port = int(DEFAULT_PORT)

    uvicorn.run(
        "main:app",
        port=port,
        host=os.environ.get("HOST", "127.0.0.1"),
        reload=os.environ.get("ENV", "DEV") == "DEV",
    )
