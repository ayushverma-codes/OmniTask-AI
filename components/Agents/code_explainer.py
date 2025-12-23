import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from components.LLM.llm_provider import load_llm
from constants import CODE_EXPLAIN_LLM

class CodeExplainerAgent:
    def __init__(self):
        # Load the LLM defined in constants (default: gemini)
        self.llm = load_llm(CODE_EXPLAIN_LLM, temperature=0.2)
        
        # Define the prompt structure
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "You are an expert Senior Software Engineer and Code Analyst. "
                "Your task is to analyze the provided code snippet and generate a report "
                "covering exactly these three areas:\n\n"
                "1. **Code Explanation**: Briefly explain what the code does logically.\n"
                "2. **Bug Detection**: Identify any potential bugs, edge cases, logical errors, or security risks. "
                "If the code looks clean, explicitly state that.\n"
                "3. **Complexity Analysis**: Determine the Time Complexity (Big O) and Space Complexity. "
                "Briefly explain why.\n\n"
                "Keep your response technical, concise, and structured."
            )),
            ("human", "Here is the code to analyze:\n\n{code_snippet}")
        ])
        
        # Create the chain
        self.chain = self.prompt | self.llm | StrOutputParser()

    def analyze_code(self, code_snippet: str) -> str:
        """
        Takes a code string as input and returns a structured textual analysis.
        """
        try:
            if not code_snippet.strip():
                return "Error: No code provided for analysis."

            response = self.chain.invoke({"code_snippet": code_snippet})
            return response
            
        except Exception as e:
            return f"Error during code analysis: {str(e)}"
