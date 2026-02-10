import os
import uuid
import time
import chromadb
from chromadb.utils import embedding_functions
import yfinance as yf
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize ChromaDB
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(name="cognivest_docs")

# In-memory task status storage
task_status = {}

def update_task_status(task_id, status, message=None):
    task_status[task_id] = {"status": status, "message": message}

def get_task_status(task_id):
    return task_status.get(task_id, {"status": "UNKNOWN"})

def process_ticker_documents(ticker: str, task_id: str):
    """
    Background task to fetch news/documents for a ticker, embed them, and store in ChromaDB.
    """
    try:
        update_task_status(task_id, "PROCESSING", "Fetching documents...")
        
        # simulated delay
        # time.sleep(2) 

        # Fetch news using yfinance
        stock = yf.Ticker(ticker)
        news = stock.news
        
        documents = []
        metadatas = []
        ids = []

        if not news:
            update_task_status(task_id, "SUCCESS", "No news found, but processing complete.")
            return

        for item in news:
            title = item.get('title', '')
            link = item.get('link', '')
            publisher = item.get('publisher', '')
            # Some news items might not have 'relatedTickers' or it might be a list
            
            content = f"Title: {title}\nPublisher: {publisher}\nLink: {link}\n"
            
            documents.append(content)
            metadatas.append({"ticker": ticker, "source": publisher, "link": link})
            ids.append(str(uuid.uuid4()))

        if documents:
            update_task_status(task_id, "PROCESSING", "Embedding and storing documents...")
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
        update_task_status(task_id, "SUCCESS", "Documents processed successfully.")
        
    except Exception as e:
        print(f"Error processing documents for {ticker}: {e}")
        update_task_status(task_id, "FAILURE", str(e))

def query_rag(question: str, ticker: str):
    """
    Queries the RAG system for an answer based on the ticker.
    """
    try:
        # Retrieve relevant documents
        results = collection.query(
            query_texts=[question],
            n_results=3,
            where={"ticker": ticker} # Filter by ticker
        )
        
        context = ""
        if results['documents']:
            context = "\n\n".join(results['documents'][0])
            
        # Generate answer using OpenAI
        system_prompt = f"You are a helpful investment assistant. Use the following context to answer the user's question about {ticker}. If the answer is not in the context, say you don't know but offer general investment advice related to the question."
        
        user_prompt = f"Context:\n{context}\n\nQuestion: {question}"
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error querying RAG: {e}")
        return "I'm sorry, I encountered an error while trying to answer your question."
