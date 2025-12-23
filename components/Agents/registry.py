import asyncio
from components.Agents.summarization_agent import generate_summary
from components.Agents.sentiment_analysis import analyze_sentiment
from components.Agents.code_explainer import CodeExplainerAgent
from components.Agents.ocr_agent import extract_text_from_image
from components.Agents.transcribe import transcribe_audio
from components.Agents.pdf_agent import process_pdf
from components.Agents.yt_fetcher import fetch_youtube_transcript

# --- WRAPPERS ---

def run_summarize(payload):
    # 1. Use Cached Content (Fastest)
    content = payload.get('cached_content')
    
    # 2. If no cache, try text input
    if not content or len(content) < 5:
        content = payload.get('text', "")
    
    # 3. Last resort fallback
    if not content:
        return "Error: No content found to summarize."

    return generate_summary(content)

def run_transcribe(payload):
    # If we already have it in cache (which we should), just return it!
    if payload.get('cached_content'):
        return payload['cached_content']
        
    # Fallback to tool
    result = transcribe_audio(payload['file_path'])
    # CLEAN OUTPUT FIX
    if isinstance(result, dict):
        return result.get("transcript", str(result))
    return str(result)

def run_sentiment(payload): 
    text = payload.get('cached_content') or payload.get('text')
    return str(analyze_sentiment(text))

def run_code(payload): 
    text = payload.get('cached_content') or payload.get('text')
    return CodeExplainerAgent().analyze_code(text)

def run_ocr(payload):
    # If already extracted, return it
    if payload.get('cached_content'): return payload['cached_content']
    return extract_text_from_image(payload['file_path'])

def run_pdf(payload): 
    if payload.get('cached_content'): return payload['cached_content']
    return str(process_pdf(payload['file_path']))

def run_yt(payload): 
    return str(fetch_youtube_transcript(payload['text']))

AGENT_MAP = {
    "summarize": run_summarize,
    "sentiment": run_sentiment,
    "code_explain": run_code,
    "ocr": run_ocr,
    "transcribe": run_transcribe,
    "pdf_extract": run_pdf,
    "youtube_transcript": run_yt
}

async def execute_agent(agent_name: str, text: str, file_path: str, cached_content: str = None):
    handler = AGENT_MAP.get(agent_name)
    if not handler: return f"Error: Agent '{agent_name}' not found."
    
    payload = {
        "text": text, 
        "file_path": file_path, 
        "cached_content": cached_content
    }
    
    try:
        result = await asyncio.to_thread(handler, payload)
        return result
    except Exception as e:
        return f"Error executing {agent_name}: {str(e)}"