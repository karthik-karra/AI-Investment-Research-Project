from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from app.services import stock_service, rag_service
import uuid

router = APIRouter()

class TickerRequest(BaseModel):
    ticker: str

class QueryRequest(BaseModel):
    question: str
    ticker: str

@router.post("/process-document")
async def process_document(request: TickerRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    # Initialize task status
    rag_service.update_task_status(task_id, "PENDING", "Task initiated")
    
    # Add to background tasks
    background_tasks.add_task(rag_service.process_ticker_documents, request.ticker, task_id)
    
    return {"message": "Processing started", "task_id": task_id}

@router.get("/task-status/{task_id}")
async def get_status(task_id: str):
    status = rag_service.get_task_status(task_id)
    return status

@router.get("/api/stock-data/{ticker}")
async def get_stock_data(ticker: str):
    data = stock_service.get_stock_data(ticker)
    if not data:
        return {"error": "No data found for ticker", "data": []}
    return {"data": data}

@router.post("/api/query")
async def query_rag(request: QueryRequest):
    answer = rag_service.query_rag(request.question, request.ticker)
    return {"answer": answer}
