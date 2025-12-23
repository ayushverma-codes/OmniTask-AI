import operator
from typing import Annotated, TypedDict, Union, List, Dict

class AgentState(TypedDict):
    # Chat History
    messages: Annotated[List[Dict[str, str]], operator.add]
    
    # The path to the file on disk
    current_file_path: Union[str, None]
    
    # --- NEW: The actual text content extracted from the file ---
    # This prevents re-transcribing audio or re-OCRing images on every turn.
    extracted_content: Union[str, None]
    
    # Internal Flow Control
    next_step: Union[str, None]
    tool_output: Union[str, None]