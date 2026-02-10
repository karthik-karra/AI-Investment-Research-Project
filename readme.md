# Cognivest - AI Investment Research

Cognivest is an AI-powered investment research tool designed to help users analyze financial documents and track stock performance. It combines a robust backend with a modern frontend to provide real-time stock data visualization and a Q&A interface powered by Google's Gemini LLM.

## Features

-   **Stock Data Visualization**: View daily time-series data for stock tickers using interactive charts.
-   **AI-Powered Q&A**: Upload and process financial documents (or retrieve them via API) and ask questions about specific stocks using a RAG (Retrieval-Augmented Generation) pipeline.
-   **Document Processing**: Automatically fetches and indexes documents for efficient retrieval.
-   **Task Management**: Tracks the status of background document processing tasks.

## Tech Stack

### Backend
-   **Framework**: FastAPI
-   **Language**: Python 3.8+
-   **Database**: PostgreSQL (via Docker), ChromaDB (Vector Database)
-   **AI/LLM**: Google Gemini (`google-genai`)
-   **Data Sources**: Alpha Vantage, Yahoo Finance (`yfinance`)
-   **ORM**: SQLAlchemy

### Frontend
-   **Framework**: Vue.js 3
-   **UI Library**: PrimeVue
-   **Charts**: ApexCharts (via `vue3-apexcharts`)
-   **HTTP Client**: Axios

### DevOps
-   **Containerization**: Docker & Docker Compose (for PostgreSQL)

## Prerequisites

Ensure you have the following installed:
-   [Node.js](https://nodejs.org/) & npm
-   [Python 3.8+](https://www.python.org/)
-   [Docker Desktop](https://www.docker.com/products/docker-desktop/)

## Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/karthik-karra/AI-Investment-Research-Project
cd "AI Investment Research Project"
```

### 2. Database Setup
Start the PostgreSQL database using Docker Compose:
```bash
docker-compose up -d
```
This will start a PostgreSQL instance on port `5432`.

### 3. Backend Setup

Navigate to the backend directory:
```bash
cd backend
```

Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

**Environment Variables**:
Create a `.env` file in the `backend` directory with the following keys:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/cognivest
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
GEMINI_API_KEY=your_google_gemini_key
```

Run the backend server:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.

### 4. Frontend Setup

Navigate to the frontend directory:
```bash
cd ../frontend
```

Install dependencies:
```bash
npm install
```

Run the development server:
```bash
npm run serve
```
The application will be accessible at `http://localhost:8080`.

## API Documentation

Once the backend is running, you can access the interactive API documentation at:
-   **Swagger UI**: `http://localhost:8000/docs`
-   **ReDoc**: `http://localhost:8000/redoc`

## Project Structure

-   `backend/`: Contains the FastAPI application, database models, and RAG pipeline.
-   `frontend/`: Contains the Vue.js application.
-   `docker-compose.yml`: Configuration for the PostgreSQL database service.
-   `run_backend.bat` / `run_frontend.bat`: Helper scripts for Windows.

## Contributing

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.
