from redis_client import redis_client
from fastapi import FastAPI
from pydantic import BaseModel
from state import agent
import json


# Create FastAPI application
app = FastAPI(
    title="AI Business Analytics API",
    description="Business Analytics and Decision Support Agent",
    version="1.0"
)


# Request model
class QuestionRequest(BaseModel):
    question: str


# Response model
class AnswerResponse(BaseModel):
    answer: str
    chart_type: str = ""
    chart_title: str = ""
    chart_data: list = []

# Test endpoint
@app.get("/")
def home():
    return {
        "message": "AI Business Analytics API is running"
    }


# Main analytics endpoint
@app.post("/ask")
def ask_question(request: QuestionRequest):

    question = request.question
    cache_key = f"cache:{question}"

    cached_data = redis_client.get(cache_key)

    if cached_data:
        return json.loads(cached_data)

    result = agent.invoke({
        "question": question
    })

    response_data = {
        "answer": result["final_answer"],
        "chart_type": result.get("chart_type", ""),
        "chart_title": result.get("chart_title", ""),
        "chart_data": result.get("chart_data", [])
    }

    redis_client.set(
        cache_key,
        json.dumps(response_data),
        ex=3600
    )

    return response_data