from redis_client import redis_client
from fastapi import FastAPI
from pydantic import BaseModel
from state import agent



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


# Test endpoint
@app.get("/")
def home():
    return {
        "message": "AI Business Analytics API is running"
    }


# Main analytics endpoint
@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):

    question = request.question

    cache_key = f"cache:{question}"

    # Check Redis
    cached_answer = redis_client.get(cache_key)

    if cached_answer:
        return {
            "answer": cached_answer,
            "source": "redis"
        }

    # Run LangGraph
    result = agent.invoke({
        "question": question
    })

    answer = result["final_answer"]

    # Store answer in Redis for 1 hour
    redis_client.set(
        cache_key,
        answer,
        ex=3600
    )

    return {
        "answer": answer,
        "source": "agent"
    }
