import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.schemas.query import QueryRequest, QueryResponse, FeedbackRequest, FeedbackResponse
from app.services.graph.workflow import app_graph
from app.services.retrieval.retriever import PineconeRetriever
from app.core.config import settings, logger
import time

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent assistant for citrus disease and government schemes using LangGraph, Groq, and Pinecone.",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    formatted_process_time = "{0:.2f}".format(process_time)
    logger.info(f"path={request.url.path} method={request.method} status_code={response.status_code} duration={formatted_process_time}ms")
    return response

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "An internal server error occurred. Please check logs for details."},
    )

@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

@app.post("/query", response_model=QueryResponse, tags=["Agent"])
async def query_agent(request: QueryRequest):
    try:
        logger.info(f"Processing query for session: {request.session_id or 'default'}")
        initial_state = {"question": request.question}
        config = {"configurable": {"thread_id": request.session_id or "default-session"}}
        
        final_state = app_graph.invoke(initial_state, config=config)
        
        return QueryResponse(
            success=True,
            intent=final_state.get("intent", "unknown"),
            answer=final_state.get("answer", "No answer generated."),
            sources=final_state.get("sources", [])
        )
    except Exception as e:
        logger.error(f"Query Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process query")

@app.post("/feedback", response_model=FeedbackResponse, tags=["Feedback"])
async def post_feedback(request: FeedbackRequest):
    try:
        retriever = PineconeRetriever()
        
        if not request.is_satisfied:
            if request.correct_info:
                logger.info(f"Learning from user correction: {request.session_id}")
                retriever.add_learned_knowledge(
                    request.correct_info, 
                    f"User Correction (Session: {request.session_id})", 
                    "hybrid"
                )
                return FeedbackResponse(success=True, message="Thank you for the correction! I have learned this for future queries.")
            else:
                logger.info(f"Triggering automated learning for: {request.question}")
                from langchain_community.tools.tavily_search import TavilySearchResults
                search = TavilySearchResults(max_results=1)
                search_results = search.invoke(request.question)
                
                if search_results:
                    learned_content = search_results[0].get("content", "")
                    url = search_results[0].get("url", "")
                    retriever.add_learned_knowledge(learned_content, url, "hybrid")
                    return FeedbackResponse(success=True, message="I've learned more about this topic to improve!")
        
        return FeedbackResponse(success=True, message="Thanks for your feedback!")
    except Exception as e:
        logger.error(f"Feedback Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to record feedback")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
