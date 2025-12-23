from typing import Literal, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from components.LLM.llm_provider import load_llm

# Using 'gemini' as default since it's in your constants
ROUTER_LLM_NAME = "gemini" 

class RouterOutput(BaseModel):
    intent: Literal["summarize", "sentiment", "code_explain", "ocr", "transcribe", "ambiguous"]
    confidence: float
    clarification_question: Optional[str] = Field(description="Only if ambiguous")

def get_intent_from_llm(user_text: str, file_context: str = "") -> dict:
    """
    Uses LLM to classify intent when heuristics fail.
    """
    try:
        llm = load_llm(ROUTER_LLM_NAME, temperature=0.0)
        structured_llm = llm.with_structured_output(RouterOutput)

        system_prompt = (
            "You are an Intent Classifier for an AI Agent system. "
            "Analyze the user input and file context. "
            "Classify the goal into one of the known tools. "
            "If the request is vague (e.g., 'process this' or 'help'), mark as 'ambiguous' "
            "and generate a polite clarification question."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Context from File: {file_context}\n\nUser Instruction: {user_text}")
        ])

        chain = prompt | structured_llm
        result = chain.invoke({"user_text": user_text, "file_context": file_context})
        
        return result.model_dump()

    except Exception as e:
        return {
            "intent": "ambiguous", 
            "clarification_question": f"System Error during routing: {str(e)}"
        }