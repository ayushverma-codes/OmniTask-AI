import re
from typing import Dict, Any
from components.file_processing import identify_file_type

# --- HEURISTIC MAPPING ---
KEYWORD_INTENTS = {
    "summarize": ["summarize", "summary", "shorten", "brief", "tl;dr", "digest"],
    "sentiment": ["sentiment", "emotion", "feeling", "tone", "positive", "negative"],
    "code_explain": ["explain code", "analyze code", "review code", "debug", "complexity", "big o"],
    "ocr": ["extract text", "read text", "ocr", "grab text", "text from image"],
    "transcribe": ["transcribe", "transcription", "speech to text", "audio to text"],
}

def analyze_keywords(text: str) -> str | None:
    """Scans text for specific keywords to determine intent deterministically."""
    if not text: return None
    
    # 1. SPECIAL CHECK: YouTube URL
    yt_pattern = r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
    if re.search(yt_pattern, text):
        return "youtube_transcript"

    # 2. Standard Keyword Check
    text_lower = text.lower()
    for intent, keywords in KEYWORD_INTENTS.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                return intent
    return None

def route_request(user_text: str, file_path: str | None) -> Dict[str, Any]:
    user_text = user_text.strip() if user_text else ""
    file_type = identify_file_type(file_path) if file_path else None

    # CASE 1: File + Text
    if file_path and user_text:
        detected_intent = analyze_keywords(user_text)
        
        if detected_intent:
            if detected_intent == "youtube_transcript":
                 return {"action": "execute", "agent": "youtube_transcript"}

            if _validate_compatibility(detected_intent, file_type):
                return {"action": "execute", "agent": detected_intent}
            else:
                return {
                    "action": "ask_user", 
                    "message": f"You asked to **{detected_intent}**, but the file is a **{file_type}**. Please check your input."
                }
        return {"action": "analyze_intent"}

    # CASE 2: File Only
    if file_path and not user_text:
        return _generate_clarification_response(file_type)

    # CASE 3: Text Only
    if user_text and not file_path:
        detected_intent = analyze_keywords(user_text)
        
        if detected_intent == "youtube_transcript":
             return {"action": "execute", "agent": detected_intent}
             
        if detected_intent in ["code_explain", "sentiment"]:
             return {"action": "execute", "agent": detected_intent}
        
        return {"action": "analyze_intent"}

    return {"action": "ask_user", "message": "I didn't receive any input."}

def _validate_compatibility(intent: str, file_type: str) -> bool:
    compatibility = {
        "transcribe": ["audio"],
        "ocr": ["image", "pdf"],
        # Updated: Allow summarize for audio (Executor will handle transcription)
        "summarize": ["text", "pdf", "audio"], 
        "code_explain": ["text"], 
        "sentiment": ["text"],
        "youtube_transcript": ["text", "unknown"]
    }
    return file_type in compatibility.get(intent, []) or file_type == "text"

def _generate_clarification_response(file_type: str) -> dict:
    options = {
        "audio": "1. Transcribe\n2. Summarize (after transcription)",
        "image": "1. Extract Text (OCR)",
        "pdf": "1. Summarize\n2. Extract Text",
        "text": "1. Summarize\n2. Analyze Sentiment\n3. Explain Code"
    }
    msg = f"I received a **{file_type}** file. What should I do?\n\n{options.get(file_type, 'Please clarify.')}"
    return {"action": "ask_user", "message": msg}