from app.core.config import settings, logger
from typing import List, Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from app.services.llm.classifier import get_intent_classifier
from app.services.retrieval.retriever import PineconeRetriever
from pydantic import BaseModel, Field
from langchain_community.tools.tavily_search import TavilySearchResults

# Grader Schema
class ContextGrader(BaseModel):
    """Binary score for context sufficiency."""
    is_sufficient: bool = Field(description="True if context is enough to answer the question, False otherwise.")
    reason: str = Field(description="Brief reason for the sufficiency score.")

# Define the state representation
class GraphState(TypedDict):
    question: str
    intent: str
    context: str
    history: List[Any]
    answer: str
    sources: List[Dict[str, Any]]
    search_triggered: bool
    is_satisfied: bool

# Nodes
def classify_intent_node(state: GraphState):
    logger.info("Classifying user intent")
    question = state["question"]
    classifier = get_intent_classifier()
    
    try:
        result = classifier.invoke({"query": question})
        intent = result.intent
    except Exception as e:
        logger.error(f"Classification error: {e}")
        intent = "hybrid" # Fallback to hybrid for safety
        
    return {"intent": intent}

def retrieve_node(state: GraphState):
    intent = state["intent"]
    
    if intent == "out_of_scope":
        return {"context": "NOT_APPLICABLE", "sources": [], "search_triggered": False}
        
    logger.info(f"Retrieving from Pinecone for {intent.upper()}")
    question = state["question"]
    retriever = PineconeRetriever()
    
    context = ""
    sources = []
    
    if intent == "hybrid":
        disease_results = retriever.retrieve(question, container_tag="disease", top_k=2)
        scheme_results = retriever.retrieve(question, container_tag="scheme", top_k=2)
        results = disease_results + scheme_results
    else:
        results = retriever.retrieve(question, container_tag=intent, top_k=3)
        
    for res in results:
        content = res.get("content", "")
        metadata = res.get("metadata") or {}
        doc = metadata.get("document_name", "Unknown")
        pg = metadata.get("page_number", "N/A")
        
        context += f"\n--- SOURCE: {doc} (Page {pg}) ---\n{content}\n"
        sources.append({"document": doc, "page": pg})
        
    # Intelligent LLM Grader to avoid over-searching
    search_triggered = False
    if results and len(context) > 100:
        logger.info("Grading context sufficiency")
        try:
            grader_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0).with_structured_output(ContextGrader)
            grade_prompt = f"""You are a quality grader. Given a user question and the retrieved context, decide if the context matches the question well enough to provide a helpful answer WITHOUT searching the web.
            
            Question: {question}
            Context: {context[:2000]}
            
            Is the context sufficient?"""
            
            grade = grader_llm.invoke(grade_prompt)
            if not grade.is_sufficient:
                logger.info(f"Context insufficient: {grade.reason}. Triggering search")
                search_triggered = True
        except Exception as e:
            logger.warning(f"Grader error: {e}. Falling back to no search")
            search_triggered = False # Safe fallback: don't search if grader fails
    else:
        logger.info("No info in Pinecone. Triggering search")
        search_triggered = True
        
    return {"context": context, "sources": sources, "search_triggered": search_triggered}

def web_search_node(state: GraphState):
    logger.info("Web searching for new knowledge")
    question = state["question"]
    intent = state["intent"]
    
    try:
        search = TavilySearchResults(max_results=2)
        search_results = search.invoke(question)
        logger.info(f"Search found {len(search_results)} results")
    except Exception as e:
        logger.error(f"Search error: {e}")
        return {"context": state["context"] + "\n[Web search failed]", "sources": state["sources"]}
    
    new_context = state["context"] + "\n\n--- ADDITIONAL WEB KNOWLEDGE ---\n"
    new_sources = state["sources"]
    
    learned_content = ""
    for res in search_results:
        content = res.get("content", "")
        url = res.get("url", "Link")
        new_context += f"- {content} (Source: {url})\n"
        new_sources.append({"document": f"Web: {url}", "page": "N/A"})
        learned_content += f"{content} "

    # Self-Learning: Store this back to Pinecone!
    if learned_content.strip() and search_results:
        try:
            retriever = PineconeRetriever()
            retriever.add_learned_knowledge(learned_content, search_results[0].get("url", "Link"), intent)
        except Exception as e:
            logger.error(f"Learning error: {e}")
    
    return {"context": new_context, "sources": new_sources}

def generate_answer_node(state: GraphState):
    logger.info("Generating final answer")
    question = state["question"]
    context = state["context"]
    intent = state["intent"]
    history = state.get("history", [])
    search_triggered = state.get("search_triggered", False)
    
    llm = ChatGroq(model=settings.GROQ_MODEL, temperature=0.2)
    
    if intent == "out_of_scope":
        prompt = """You are a warm and helpful agricultural expert. The user has asked something outside your core expertise.
        
        Response Rules:
        1. Acknowledge the question kindly.
        2. Gently steer them back to agricultural topics (citrus diseases or government schemes) where you can provide real value.
        3. Do not be a rigid robot; sound like a friendly neighbor who also happens to be a scientist.
        """
    else:
        history_str = ""
        if history:
            history_str = "\n--- RECENT CONVERSATION ---\n"
            for msg in history[-2:]: 
                role = "Farmer" if isinstance(msg, HumanMessage) else "Advisor"
                history_str += f"{role}: {msg.content[:300]}\n"

        if len(context) > 4000:
            context = context[:4000] + "\n... [Context trimmed for focus] ..."

        learning_note = "I've included some fresh insights from my research to ensure you have the most complete answer." if search_triggered else ""

        prompt = f"""You are the Elite Agri-Cult Consultant. Your signature answers are the gold standard for agricultural advice.
        
        KNOWLEDGE BASE CONTEXT: {context}
        {history_str}
        QUESTION: {question}
        
        SIGNATURE ANSWER FORMAT (MANDATORY):
        1. **EXPERT ANALYSIS**: Start with a warm professional greeting. Summarize the core answer clearly. If the data is complex or in a table, DE-CLUTTER it and present only the most important facts in simple bullet points.
        2. **ACTION PLAN**: Provide exactly 3 high-impact steps the farmer should take immediately.
        3. **PRO-CONSULTANT TIP**: Provide one piece of unique, high-value advice based on the context.
        4. **FINAL WORD**: A warm, professional closing.
        
        STRICT STYLE RULES:
        - NEVER mention "PDF", "Source", "Database", or "Knowledge Base".
        - Use ONLY the headers above. No extra text or footers.
        - Bold the headers (**EXPERT ANALYSIS**, etc.).
        - Fix all raw data: Convert any messy text or table data into clear, human-readable sentences.
        """
    
    messages = [SystemMessage(content=prompt), HumanMessage(content=question)]
    
    try:
        response = llm.invoke(messages)
        answer = response.content
    except Exception as e:
        logger.error(f"Generation error: {e}")
        llm_fallback = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)
        response = llm_fallback.invoke(messages)
        answer = response.content
    
    # Update history
    new_history = history + [HumanMessage(content=question), response]
    
    return {"answer": answer, "history": new_history}

# Routing logic
def decide_to_search(state: GraphState):
    if state["search_triggered"]:
        return "search"
    return "generate"

# Build the graph
workflow = StateGraph(GraphState)

workflow.add_node("classify", classify_intent_node)
workflow.add_node("retrieve", retrieve_node)
workflow.add_node("search", web_search_node)
workflow.add_node("generate", generate_answer_node)

workflow.set_entry_point("classify")
workflow.add_edge("classify", "retrieve")

workflow.add_conditional_edges(
    "retrieve",
    decide_to_search,
    {
        "search": "search",
        "generate": "generate"
    }
)

workflow.add_edge("search", "generate")
workflow.add_edge("generate", END)

# Persistent Memory
from langgraph.checkpoint.memory import MemorySaver
memory = MemorySaver()

# Compile
app_graph = workflow.compile(checkpointer=memory)

if __name__ == "__main__":
    # Test
    initial_state = {"question": "How to treat citrus canker?"}
    for output in app_graph.stream(initial_state):
        print(output)
