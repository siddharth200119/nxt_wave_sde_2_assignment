from fastapi import FastAPI
from src.api import main_router as APIRouter
from src.sse import main_router as SSERouter
import os
from src.events import startup, shutdown
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi.exceptions import RequestValidationError
from src.models import APIOutput
from src.middlewares import middlewares_to_apply
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    # Formulate a clear, readable validation message and build JSON-safe error structures
    error_details = []
    sanitized_errors = []
    
    for err in exc.errors():
        loc_tuple = err.get("loc", [])
        loc = ".".join(str(x) for x in loc_tuple)
        msg = err.get("msg", "Invalid value")
        
        # Remove generic "Value error, " prefix from custom validator errors
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
            
        error_details.append(f"{loc}: {msg}")
        
        # Build serializable version of this error, scrubbing non-serializable python exception objects
        sanitized_err = {
            "type": err.get("type"),
            "loc": loc_tuple,
            "msg": msg,
            "input": err.get("input"),
        }
        
        if "ctx" in err:
            ctx = err["ctx"]
            sanitized_ctx = {}
            for k, v in ctx.items():
                if isinstance(v, Exception):
                    sanitized_ctx[k] = str(v)
                else:
                    sanitized_ctx[k] = v
            sanitized_err["ctx"] = sanitized_ctx
            
        sanitized_errors.append(sanitized_err)
    
    error_msg = "; ".join(error_details)
    return APIOutput.failure(
        message=f"Validation Error: {error_msg}",
        status_code=400,
        data={"detail": sanitized_errors}
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup(app)
    try:
        yield
    finally:
        await shutdown(app)

for middleware in reversed(middlewares_to_apply):
    app.add_middleware(middleware)

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
