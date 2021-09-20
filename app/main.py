from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.custom_classes.finbert import model_loader
from app.routes import test
from db.database import SessionLocal
# import aioredis
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from fastapi_cache.decorator import cache

app = FastAPI()

# API Doc
# app = FastAPI(
#     title="Wiki-Movie",
#     description="Wikipedia Persing Tools",
#     version="1.0.0",
# )


# Error
@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    # print(f"OMG! An HTTP error!: {repr(exc)}")
    # Add error logger here loguru
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error"},
    )


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()

# API routes
app.include_router(
    router=test.router,
    tags=["financial-sentiment"]
)

db = SessionLocal()
pipe_line_fixed, pipe_line_all = None, None

#
@app.on_event("startup")
async def startup_event():
    # redis =  aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    # FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    global pipe_line_fixed, pipe_line_all
    pipe_line_fixed, pipe_line_all = model_loader()
    import nltk
    nltk.download('punkt')


# if __name__ == '__main__':
#     uvicorn.run(app='app:app', reload=True, port="7003", host="0.0.0.0")
