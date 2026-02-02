from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from app.core.config import settings, logger

class IntentResponse(BaseModel):
    """Result of intent classification."""
    intent: Literal["disease", "scheme", "hybrid", "out_of_scope"] = Field(
        description="The classified intent of the user query."
    )
    explanation: str = Field(description="Brief explanation of the classification decision.")

def get_intent_classifier():
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=settings.GROQ_API_KEY,
        temperature=0
    )
    
    # Structured output ensures we get one of the four labels
    structured_llm = llm.with_structured_output(IntentResponse)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert agricultural intent classifier for a farmer chatbot. 
        Your job is to classify farmer queries into one of four categories:
        1. 'disease': Query is about crop pests, diseases, symptoms, or plant health.
        2. 'scheme': Query is about government subsidies, financial help, or agricultural programs.
        3. 'hybrid': Query combines both.
        4. 'out_of_scope': Query is NOT about agriculture at all (e.g. general knowledge, sports, unrelated small talk).
        
        RULES:
        - ANY question related to farming, crops (even non-citrus), or agriculture should be mapped to 1, 2, or 3.
        - Handle spelling mistakes gracefully.
        - Use 'out_of_scope' ONLY for totally non-agricultural queries."""),
        ("human", "{query}")
    ])
    
    return prompt | structured_llm

if __name__ == "__main__":
    classifier = get_intent_classifier()
    test_query = "What schemes can help me manage Citrus Canker?"
    result = classifier.invoke({"query": test_query})
    logger.info(f"Query: {test_query}")
    logger.info(f"Intent: {result.intent}")
    logger.info(f"Explanation: {result.explanation}")
