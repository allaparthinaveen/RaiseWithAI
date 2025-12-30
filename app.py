# app.py - Complete Python script for Web Search Microservice using Tavily
# This implements a decoupled microservice pattern with FastAPI.
# API key is loaded from environment variables (.env file or system env).
# Run with: uvicorn app:app --reload
# Test with curl/Postman: e.g., curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d '{"query": "latest AI advancements 2025"}'

import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, List, Optional
from tavily import TavilyClient

# Load environment variables from .env file
load_dotenv()

# Configurable API key from environment
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY not set in environment variables")

# Initialize Tavily client (global for the service)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

# FastAPI app instance
app = FastAPI(
    title="Web Search Microservice",
    description="A decoupled microservice for AI-optimized web searches using Tavily. Ideal for integration into agentic workflows like Trend Researcher.",
    version="1.0.0"
)

# Pydantic models for request/response validation
class SearchRequest(BaseModel):
    query: str
    search_depth: Optional[str] = "advanced"  # "basic" or "advanced"
    max_results: Optional[int] = 8
    include_answer: Optional[bool] = True
    include_raw_content: Optional[bool] = False
    include_images: Optional[bool] = False
    include_domains: Optional[List[str]] = None
    exclude_domains: Optional[List[str]] = None

class SearchResult(BaseModel):
    title: str
    url: str
    content: str
    score: float
    published_date: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    answer: Optional[str] = None
    results: List[SearchResult]

# Health check endpoint (GET for simple testing)
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Web Search Microservice is running"}

# Main search endpoint (POST for flexibility with body params)
@app.post("/search", response_model=SearchResponse)
async def perform_search(request: SearchRequest = Body(...)):
    try:
        # Prepare Tavily search parameters
        search_params = {
            "search_depth": request.search_depth,
            "max_results": request.max_results,
            "include_answer": request.include_answer,
            "include_raw_content": request.include_raw_content,
            "include_images": request.include_images,
        }
        if request.include_domains:
            search_params["include_domains"] = request.include_domains
        if request.exclude_domains:
            search_params["exclude_domains"] = request.exclude_domains

        # Execute Tavily search
        response = tavily.search(
            query=request.query,
            **search_params
        )

        # Parse and structure the results
        structured_results = [
            SearchResult(
                title=r["title"],
                url=r["url"],
                content=r["content"],
                score=r["score"],
                published_date=r.get("published_date")
            )
            for r in response.get("results", [])
        ]

        return SearchResponse(
            query=request.query,
            answer=response.get("answer"),
            results=structured_results
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tavily search error: {str(e)}")

# Optional: Fallback or test endpoint if needed (e.g., for quick query without full params)
@app.get("/quick-search")
async def quick_search(query: str):
    try:
        response = tavily.search(query=query)
        return {
            "query": query,
            "answer": response.get("answer"),
            "results": response.get("results")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick search error: {str(e)}")

# Run the app if executed directly (for development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
