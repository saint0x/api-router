from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time
import psutil
import asyncio
from datetime import datetime

app = FastAPI()

# Middleware for timing requests
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    route_match_start = time.time()
    response = await call_next(request)
    route_match_time = time.time() - route_match_start
    total_time = time.time() - start_time
    
    # Add timing headers
    response.headers["X-Route-Match-Time"] = str(route_match_time)
    response.headers["X-Total-Time"] = str(total_time)
    return response

@app.get("/ping")
async def ping():
    return {"status": "ok"}

@app.get("/api/v1/data")
async def get_data():
    return {
        "data": {
            "id": 1,
            "name": "test",
            "timestamp": datetime.now().isoformat()
        }
    }

@app.post("/api/v1/process")
async def process_data(request: Request):
    data = await request.json()
    # Simulate processing
    await asyncio.sleep(0.001)
    return {
        "processed": True,
        "input": data,
        "timestamp": datetime.now().isoformat()
    }
