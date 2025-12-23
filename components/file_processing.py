import os
import aiofiles
from typing import Literal

# Import existing specific logic
from components.Agents.pdf_agent import extract_text_from_pdf
from components.Agents.ocr_agent import extract_text_from_image
from components.Agents.transcribe import transcribe_audio

SUPPORTED_EXTENSIONS = {
    "audio": [".mp3", ".wav", ".m4a", ".mp4", ".mpeg", ".mpga"],
    "image": [".png", ".jpg", ".jpeg", ".bmp", ".tiff"],
    "pdf": [".pdf"],
    "text": [".txt", ".md", ".py", ".json", ".csv"]
}

def identify_file_type(file_path: str) -> Literal["audio", "image", "pdf", "text", "unknown"]:
    if not file_path: return None
    _, ext = os.path.splitext(file_path.lower())
    for category, extensions in SUPPORTED_EXTENSIONS.items():
        if ext in extensions: return category
    return "unknown"

async def extract_file_content(file_path: str) -> str:
    """
    Unified function to turn ANY file into text.
    This runs the heavy lifting (OCR/Whisper) exactly once.
    """
    if not file_path or not os.path.exists(file_path):
        return ""

    file_type = identify_file_type(file_path)
    
    try:
        # 1. Text Files
        if file_type == "text":
            async with aiofiles.open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return await f.read()

        # 2. PDFs
        elif file_type == "pdf":
            return extract_text_from_pdf(file_path)

        # 3. Images (OCR)
        elif file_type == "image":
            return extract_text_from_image(file_path)

        # 4. Audio (Transcribe)
        elif file_type == "audio":
            # Call the transcribe agent directly to get the text
            result = transcribe_audio(file_path)
            # Handle the JSON return format
            if isinstance(result, dict):
                return result.get("transcript", str(result))
            return str(result)

        return f"[System: File type '{file_type}' detected. No automated text extraction available.]"

    except Exception as e:
        return f"[System Error processing file: {str(e)}]"

async def extract_content_preview(file_path: str) -> str:
    """Helper for the Router to get context."""
    content = await extract_file_content(file_path)
    return content[:2000] if content else ""