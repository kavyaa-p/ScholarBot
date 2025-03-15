# ScholarBot

A Retrieval-Augmented Generation (RAG) based AI system that processes PDFs, extracts relevant
content, and answers questions using FastAPI, LangChain, ChromaDB, OpenAI APIs, and React.

## Features

- Upload PDF files and extract their text
- Chunk text intelligently for efficient retrieval
- Store embeddings in a ChromaDB vector database
- Use OpenAI embeddings and GPT models for responses
- Query documents with natural language and get structured answers
- React frontend for an intuitive user experience

## Tech Stack

### Backend

- Python, FastAPI
- OpenAI API

### Frontend

- React (Vite)

## Installation & Setup

### 1. Clone Repository

```sh
git clone https://github.com/your-username/ScholarBot.git
cd ScholarBot
```

### 2. Backend Setup (FastAPI)

#### 2.1. Create Virtual Environment

```sh
cd backend
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate      # On Windows
```

#### 2.2. Install Dependencies

```sh
pip install -r requirements.txt
```

#### 2.3. Start FastAPI Server

```sh
uvicorn main:backend_app --reload
# or
python3 -m uvicorn main:backend_app # if the previous command does not work
```

Backend running at: http://127.0.0.1:8000

### 3. Frontend Setup (React)

#### 3.1. Install Dependencies

```sh
cd frontend
npm install
```

#### 3.2. Start React Server

```sh
npm run dev
```

Frontend running at: http://localhost:5173

## API Endpoints

| Method | Endpoint  | Description               |
|--------|-----------|---------------------------|
| `POST` | `/upload` | Upload a PDF file         |
| `POST` | `/query`  | Query extracted documents |
| `POST` | `/docs`   | OpenAPI Docs (Swagger UI) |

## Usage Guide

1. Upload a PDF file using the upload button
2. Ask questions about the content
3. Get answers based on document context