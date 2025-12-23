import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_groq import ChatGroq

def load_llm(llm_name: str, temperature: float = 0.0):
    """
    Load and return a LangChain LLM instance (Gemini or Groq)
    based on the provided llm_name.
    """
    # Load .env from project root (adjust depth if your structure changes)
    # Assuming this file is in components/LLM/
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../../"))
    env_path = os.path.join(root_dir, ".env")
    
    if not load_dotenv(env_path):
        print(f"Warning: .env file not found at {env_path}")

    llm_name = llm_name.lower().strip()

    if "gemini" in llm_name:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")

        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", # Updated to current stable version
            temperature=temperature,
            max_retries=2,
            google_api_key=api_key,
        )

    elif "groq" in llm_name:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
            
        # return ChatGroq(
        #     model="llama-3.3-70b-versatile", 
        #     temperature=temperature,
        #     max_retries=2,
        #     api_key=api_key
        # )

    else:
        raise ValueError(f"Unsupported LLM name: {llm_name}. Please check constants/__init__.py")