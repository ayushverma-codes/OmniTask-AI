from dataclasses import dataclass
from typing import Optional

@dataclass
class ChatMessage:
    role: str
    content: str
    file_path: Optional[str] = None
