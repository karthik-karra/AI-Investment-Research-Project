import os
from google import genai
from google.genai import types
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found in environment variables.")

client = genai.Client(api_key=GEMINI_API_KEY)

current_dir = os.path.dirname(os.path.abspath(__file__))
persist_directory = os.path.join(current_dir, "..", "chroma_db")

chroma_client = chromadb.PersistentClient(path=persist_directory)
collection = chroma_client.get_or_create_collection(name="cognivest_docs")

def get_gemini_embedding(text):
    """
    Generates embedding using Gemini optimized for document retrieval.
    """
    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                title="Embedding of stock document"
            )
        )
        return result.embeddings[0].values
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

def generate_answer(context, question):
    """
    Generates an answer using Gemini based on the provided context.
    """
    try:
        print(f"\n--- Generating Answer ---")
        print(f"Question: {question}")
        
        prompt = f"""
        You are a helpful investment assistant for Cognivest.
        Use the following context to answer the user's question.
        If the answer is not in the context, say you don't know.
        
        Context:
        {context}
        
        Question:
        {question}
        """
        
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=prompt
        )
        
        print(f"Generated Answer: {response.text}")
        print("-------------------------")
        return response.text
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "I'm sorry, I encountered an error while processing your request."

def query_vectors(question: str, ticker: str, n_results: int = 5):
    """
    Queries ChromaDB for relevant documents.
    """
    try:
        print(f"\n--- Querying Vectors ---")
        print(f"Query: {question} (Ticker: {ticker})")
        
        # We need to embed the query first
        query_embedding = client.models.embed_content(
            model="gemini-embedding-001",
            contents=question,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )
        
        results = collection.query(
            query_embeddings=[query_embedding.embeddings[0].values],
            n_results=n_results,
            where={"ticker": ticker}
        )
        
        context = ""
        if results['documents']:
            print(f"Found {len(results['documents'][0])} relevant documents.")
            
            context_parts = []
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i] if results['metadatas'] else {}
                source = meta.get('source', 'Unknown')
                link = meta.get('link', 'No link')
                
                print(f"[Doc {i+1}] Source: {source} | Link: {link}")
                print(f"Preview: {doc[:200]}...")
                context_parts.append(doc)
                
            context = "\n\n".join(context_parts)
        else:
            print("No relevant documents found.")
            
        return context
    except Exception as e:
        print(f"Error querying vectors: {e}")
        return ""
