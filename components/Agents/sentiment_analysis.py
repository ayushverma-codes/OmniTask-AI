# D:\Projects\OmniTask_AI\components\Agents\sentiment_analysis.py
import sys
import os
from typing import Literal

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from langchain_core.prompts import ChatPromptTemplate
# --- FIX: Import directly from standard pydantic ---
from pydantic import BaseModel, Field
from components.LLM.llm_provider import load_llm
from constants import SENTIMENT_LLM

# 1. Define the Structure (Label + Confidence + Justification)
class SentimentOutput(BaseModel):
    label: Literal["Positive", "Negative", "Neutral"] = Field(
        description="The sentiment label of the text."
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0."
    )
    justification: str = Field(
        description="A concise, one-line justification for the classification."
    )

def analyze_sentiment(text: str) -> dict:
    """
    Analyzes the sentiment of the provided text using the LLM defined in constants.
    """
    try:
        # 2. Load the specific LLM for this task
        llm = load_llm(SENTIMENT_LLM, temperature=0.0)

        # 3. Bind the structure to the LLM
        structured_llm = llm.with_structured_output(SentimentOutput)

        # 4. Create the prompt
        system_prompt = (
            "You are a sentiment analysis expert. "
            "Analyze the user's text and extract the sentiment label, "
            "a confidence score (0.0-1.0), and a one-line justification. "
            "Be precise and concise."
        )
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input_text}"),
        ])

        # 5. Build the chain
        chain = prompt | structured_llm

        # 6. Execute
        result = chain.invoke({"input_text": text})

        # --- FIX: Use model_dump() for Pydantic v2 ---
        return result.model_dump()

    except Exception as e:
        # Fallback error handling
        return {
            "label": "Error",
            "confidence": 0.0,
            "justification": f"Analysis failed: {str(e)}"
        }
