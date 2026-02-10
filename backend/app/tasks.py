import os
import requests
import uuid
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from app import rag_pipeline, database
from app.database import Task
from sqlalchemy.orm import Session
import datetime
from bs4 import BeautifulSoup
import re
import time

# Alpha Vantage Setup
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# SEC Setup
# SEC requires a user agent in the format: "AppName/Version (Email)" or similar.
SEC_USER_AGENT = os.getenv("SEC_API_USER_AGENT", "CognivestAI/1.0 (cognivest_dev@example.com)")

def update_task_db(db: Session, task_id: str, status: str, message: str = None):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.status = status
        if message:
            task.message = message
        db.commit()

def clean_html_content(html_content):
    """
    Cleans HTML content to extract text.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style", "head", "title", "meta", "[document]"]):
        script.extract()
        
    text = soup.get_text(separator=' ')
    
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def chunk_text(text, chunk_size=2000, overlap=200):
    """
    Splits text into chunks with overlap.
    """
    chunks = []
    start = 0
    text_len = len(text)
    
    if text_len <= chunk_size:
        return [text]
    
    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk = text[start:end]
        chunks.append(chunk)
        
        if end == text_len:
            break
            
        start += (chunk_size - overlap)
        
    return chunks

def fetch_sec_filings(ticker: str):
    """
    Fetches recent 10-K/10-Q filings from SEC EDGAR, downloads full text, and chunks it.
    """
    try:
        headers = {'User-Agent': SEC_USER_AGENT}
        print(f"Using SEC User-Agent: {SEC_USER_AGENT}")
        
        tickers_url = "https://www.sec.gov/files/company_tickers.json"
        
        resp = requests.get(tickers_url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch SEC tickers: {resp.status_code}")
            return []
            
        data = resp.json()
        cik = None
        ticker_upper = ticker.upper()
        for key, val in data.items():
            if val['ticker'] == ticker_upper:
                cik = val['cik_str']
                break
                
        if not cik:
            print(f"CIK not found for {ticker}")
            return []
            
        # Pad CIK to 10 digits
        cik_str = str(cik).zfill(10)
        print(f"Found CIK: {cik_str}")
        
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"
        resp = requests.get(submissions_url, headers=headers)
        if resp.status_code != 200:
             print(f"Failed to fetch submissions for CIK {cik_str}: {resp.status_code}")
             return []
             
        filings = resp.json().get('filings', {}).get('recent', {})
        
        documents = []
        # Get last 1 relevant filing to avoid hitting limits or processing too much
        count = 0
        limit = 1 
        
        if not filings.get('form'):
             print("No filings found.")
             return []

        for i, form in enumerate(filings.get('form', [])):
            if form in ['10-K', '10-Q']:
                acc_num = filings['accessionNumber'][i]
                primary_doc = filings['primaryDocument'][i]
                report_date = filings['reportDate'][i]
                
                # Construct link
                doc_link = f"https://www.sec.gov/Archives/edgar/data/{int(cik_str)}/{acc_num.replace('-', '')}/{primary_doc}"
                print(f"Fetching filing content from: {doc_link}")
                
                # Fetch full text
                # Rate limiting: sleep briefly to be nice to SEC
                time.sleep(0.2)
                
                try:
                    doc_resp = requests.get(doc_link, headers=headers, timeout=30)
                    if doc_resp.status_code == 200:
                        print("Download successful. Cleaning HTML...")
                        raw_text = clean_html_content(doc_resp.content)
                        print(f"Total text length: {len(raw_text)}")
                        
                        chunks = chunk_text(raw_text)
                        print(f"Parsed {len(chunks)} chunks from {form}")
                        
                        for idx, chunk in enumerate(chunks):
                            documents.append({
                                "content": f"SEC Filing {form} ({report_date}) - Part {idx+1}/{len(chunks)}:\n{chunk}",
                                "source": "SEC",
                                "link": doc_link,
                                "metadata_suffix": f" - Part {idx+1}"
                            })
                    else:
                        print(f"Failed to download filing text: {doc_resp.status_code}")
                        # Fallback
                        content = f"SEC Filing {form} - Date: {report_date}\nLink: {doc_link}\n(Content download failed)"
                        documents.append({"content": content, "source": "SEC", "link": doc_link})
                except Exception as doc_e:
                    print(f"Exception downloading doc: {doc_e}")
                    content = f"SEC Filing {form} - Date: {report_date}\nLink: {doc_link}\n(Download error: {doc_e})"
                    documents.append({"content": content, "source": "SEC", "link": doc_link})
                
                count += 1
                if count >= limit:
                    break
        return documents

    except Exception as e:
        print(f"Error fetching SEC filings: {e}")
        import traceback
        traceback.print_exc()
        return []

def fetch_alpha_vantage_news(ticker: str):
    """
    Fetches news sentiment using Alpha Vantage.
    """
    if not ALPHA_VANTAGE_API_KEY:
        return []
    
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        feed = data.get('feed', [])
        
        docs = []
        for item in feed[:5]: # Top 5 news
            content = f"Title: {item.get('title')}\nSummary: {item.get('summary')}\nSentiment: {item.get('overall_sentiment_score')}"
            docs.append({"content": content, "source": item.get('source'), "link": item.get('url')})
        return docs
    except Exception as e:
        print(f"Error fetching Alpha Vantage news: {e}")
        return []

def process_ticker_documents(ticker: str, task_id: str):
    """
    Background task orchestrated.
    """
    # Create DB session
    db = database.SessionLocal()
    
    # Create Task record if not exists
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        task = Task(id=task_id, status="PROCESSING", message="Starting...")
        db.add(task)
        db.commit()
    
    try:
        update_task_db(db, task_id, "PROCESSING", "Fetching SEC 10-K Filings...")
        sec_docs = fetch_sec_filings(ticker)
        
        update_task_db(db, task_id, "PROCESSING", "Fetching News...")
        av_docs = fetch_alpha_vantage_news(ticker)
        
        # Fallback/Additional news from yfinance
        stock = yf.Ticker(ticker)
        yf_news = stock.news
        yf_docs = []
        try:
             # yf.news might be empty or different structure depending on version
             if yf_news:
                for item in yf_news:
                     yf_docs.append({
                         "content": f"Title: {item.get('title')}\nPublisher: {item.get('publisher')}\n",
                         "source": item.get('publisher'),
                         "link": item.get('link')
                     })
        except Exception as yfe:
            print(f"YF News error: {yfe}")

        all_docs = sec_docs + av_docs + yf_docs
        
        if not all_docs:
            update_task_db(db, task_id, "SUCCESS", "No documents found.")
            db.close()
            return

        update_task_db(db, task_id, "PROCESSING", f"Embedding {len(all_docs)} documents with Gemini...")
        print(f"Total documents to embed: {len(all_docs)}")
        
        documents_text = [d['content'] for d in all_docs]
        metadatas = [{"ticker": ticker, "source": d.get('source') or "Unknown", "link": d.get('link') or "Unknown"} for d in all_docs]
        ids = [str(uuid.uuid4()) for _ in all_docs]
        
        embeddings = []
        
        # Process in batches to handle API limits / network stability
        batch_size = 5
        total_batches = (len(documents_text) + batch_size - 1) // batch_size
        
        for i in range(0, len(documents_text), batch_size):
            batch_texts = documents_text[i:i+batch_size]
            print(f"Embedding batch {i//batch_size + 1}/{total_batches}")
            
            for text in batch_texts:
                # Truncate text if it's too long for embedding model? 
                # gemini-embedding-001 has 2048 token input limit? 
                # Our chunk size is 2000 chars ~ 500-800 tokens. Should be safe.
                emb = rag_pipeline.get_gemini_embedding(text)
                if emb and len(emb) > 0:
                    embeddings.append(emb)
                else:
                    embeddings.append(None)
            
            # Brief pause between batches
            time.sleep(0.5)
        
        # Filter valid
        valid_indices = [i for i, e in enumerate(embeddings) if e is not None]
        
        if valid_indices:
            print(f"Persisting {len(valid_indices)} vectors to ChromaDB...")
            rag_pipeline.collection.add(
                documents=[documents_text[i] for i in valid_indices],
                embeddings=[embeddings[i] for i in valid_indices],
                metadatas=[metadatas[i] for i in valid_indices],
                ids=[ids[i] for i in valid_indices]
            )

        update_task_db(db, task_id, "SUCCESS", f"Processed {len(valid_indices)} chunks successfully.")
        
    except Exception as e:
        print(f"Task failed: {e}")
        import traceback
        traceback.print_exc()
        update_task_db(db, task_id, "FAILURE", str(e))
    finally:
        db.close()
