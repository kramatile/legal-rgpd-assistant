from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .model_loader import GraphRag
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL_NAME = os.getenv("OPENROUTER_MODEL_NAME")

if not all([
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD,
    OPENROUTER_API_KEY,
    OPENROUTER_MODEL_NAME
]):
    raise RuntimeError("Missing required environment variables")

graph_rag = GraphRag(
    OPENROUTER_MODEL_NAME,
    OPENROUTER_API_KEY,
    NEO4J_URI,
    NEO4J_USERNAME,
    NEO4J_PASSWORD
)

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def answer(payload: QueryRequest):
    try:
        return {"answer": graph_rag.invoke(payload.query)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
