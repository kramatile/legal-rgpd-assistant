from fastapi import FastAPI
from .config import add_cors
from .routes import router

app = FastAPI(
    title="Sentiment Analysis API",
    version="1.0.0"
)

add_cors(app)
app.include_router(router)