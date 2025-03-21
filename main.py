from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from domain.recommendation import recommendation_router


app = FastAPI()

origins = [
    "http://localhost:5173",
    # "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(recommendation_router.router)
