from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
import uuid
from app import database, tasks, rag_pipeline
import requests

app = FastAPI(title="Cognivest API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TickerRequest(BaseModel):
    ticker: str

class QueryRequest(BaseModel):
    question: str
    ticker: str

@app.get("/")
def read_root():
    return {"message": "Welcome to Cognivest API (Gemini Edition)"}

@app.post("/process-document")
async def process_document(request: TickerRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    task_id = str(uuid.uuid4())
    
    # Create initial task record
    new_task = database.Task(id=task_id, status="PENDING", message="Task initiated")
    db.add(new_task)
    db.commit()
    
    # Add background task
    background_tasks.add_task(tasks.process_ticker_documents, request.ticker, task_id)
    
    return {"message": "Processing started", "task_id": task_id}

@app.get("/task-status/{task_id}")
async def get_status(task_id: str, db: Session = Depends(get_db)):
    task = db.query(database.Task).filter(database.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": task.status, "message": task.message}

@app.get("/api/stock-data/{ticker}")
def get_stock_data(ticker: str):
    """
    Fetches daily time series data for a given stock ticker from Alpha Vantage.
    """
    API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
    OUTPUT_SIZE = "compact" # "full" - full data (20 years) | "compact" - latest 100
    url = (
        f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY"
        f"&symbol={ticker}&apikey={API_KEY}&outputsize={OUTPUT_SIZE}"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if "Time Series (Daily)" not in data:
            return {"error": "Could not retrieve time series data. The API limit might be reached or the ticker is invalid."}

        time_series = data["Time Series (Daily)"]

        # Format the data for ApexCharts: [{ x: date, y: price }]
        chart_data = [
            {"x": date, "y": float(values["4. close"])}
            for date, values in time_series.items()
        ]
        # Sort by date ascending
        chart_data.sort(key=lambda item: item['x'])

        return {"ticker": ticker, "data": chart_data}

    except requests.exceptions.RequestException as e:
        return {"error": f"Error fetching stock data: {e}"}
    

@app.post("/api/query")
async def query_rag(request: QueryRequest):
    context = rag_pipeline.query_vectors(request.question, request.ticker)
    
    answer = rag_pipeline.generate_answer(context, request.question)
    
    return {"answer": answer}
