from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sys
import os

# ---------------------------------------------------------
# Path Setup & Imports
# ---------------------------------------------------------
# Ensure we can import from parent directories
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from components.LLM.llm_provider import load_llm
    from constants import SUMMARISE_LLM
except ImportError as e:
    raise ImportError(f"Could not import project dependencies: {e}")

# ---------------------------------------------------------
# Summarization Function
# ---------------------------------------------------------
def generate_summary(text: str) -> str:
    """
    Generates a structured summary using the configured LLM.
    
    Returns:
        String containing:
        - 1-line summary
        - 3 bullet points
        - 5-sentence summary
    """
    if not text:
        return "Error: No text provided for summarization."

    # 1. Load the LLM defined in constants
    # We load it inside the function to ensure it picks up any config changes 
    # and keeps the function self-contained.
    try:
        llm = load_llm(SUMMARISE_LLM, temperature=0.3)
    except Exception as e:
        return f"Error loading LLM: {str(e)}"

    # 2. Define the strict output format template
    template = """
    You are an expert summarization assistant. 
    Analyze the following text and provide a summary strictly adhering to this format:

    1. **1-line summary**: A single, high-level sentence capturing the main essence.
    2. **Key Highlights**: Exactly 3 bullet points covering the most critical details.
    3. **Detailed Summary**: Exactly 5 sentences providing a comprehensive overview.

    Text to analyze:
    {text}

    Output:
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["text"]
    )

    # 3. Create and execute the chain
    chain = prompt | llm | StrOutputParser()
    
    try:
        return chain.invoke({"text": text})
    except Exception as e:
        return f"Error processing summary: {str(e)}"
