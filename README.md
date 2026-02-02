# Agentic Agriculture RAG Chatbot 🌾

An intelligent, production-ready system designed to help farmers manage citrus diseases and navigate government agricultural schemes. Built with **FastAPI**, **LangGraph**, **Pinecone**, and **Groq**.

## 🚀 Key Features

- **Agentic RAG**: Uses LangGraph to intelligently route queries and manage multi-step reasoning.
- **Production Ready**: Includes structured logging, centralized configuration (Pydantic Settings), global error handling, and Docker support.
- **Continuous Learning**: Automatically learns from web searches (Tavily) and user feedback.
- **MCP Capable**: Core logic is decoupled from the API, making it easy to expose as Model Context Protocol (MCP) tools.

---

## 🏗️ Tech Stack

- **Backend**: FastAPI (Python 3.11)
- **Frontend**: Vite + React + TypeScript
- **Orchestration**: LangGraph
- **Vector DB**: Pinecone
- **LLM**: Groq (Llama 3.3 70B & 3.1 8B)
- **Deployment**: Docker & Docker Compose

---

## ⚙️ Production Setup

### 1. Environment Configuration

Create a `.env` file in the root directory:

```env
# API Keys
GROQ_API_KEY=your_groq_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=your_index_name
TAVILY_API_KEY=your_tavily_key

# Optional Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_key

# Settings
LOG_LEVEL=INFO
```

### 2. Run with Docker (Recommended)

```bash
docker-compose up --build
```

The backend will be at `http://localhost:8000` and the frontend at `http://localhost:3000`.

### 3. Local Development

```bash
# Backend
pip install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:.
python app/main.py

# Frontend
cd frontend
npm install
npm run dev
```

---

## 🛠️ MCP Server Integration

This project is designed to be used as an MCP server base. The following functions in `app/services` can be wrapped as tools:

- `query_agent`: Main entry point for agricultural advice.
- `add_learned_knowledge`: Specific tool for updating the knowledge base.

To use this with an MCP host (like Claude Desktop):

1. Ensure your environment variables are set in the host config.
2. Direct the host to the `app/main.py` or a dedicated MCP entry point.

---

## 📐 Project Structure

- `app/core/`: Centralized config and logging.
- `app/api/`: API route definitions.
- `app/services/`: Core business logic (Graph, Retrieval, LLM).
- `app/schemas/`: Pydantic models for request/response.
- `scripts/`: Ingestion and testing utilities.
- `frontend/`: React application.

---

## 🧪 Testing

Run the validation suite:

```bash
export PYTHONPATH=$PYTHONPATH:.
python scripts/test_cases.py
```

---

## 🔒 Security & Best Practices

- **Secrets**: Never commit `.env` files. A `.gitignore` is provided.
- **Validation**: Environment variables are validated at startup using Pydantic.
- **Logging**: Structured logs for better observability in production.
- **Error Handling**: Global exception handlers prevent leaking stack traces.
