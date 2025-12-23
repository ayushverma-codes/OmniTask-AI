import os
import sys
import whisper
import argparse
import json
import warnings

# --- 1. SETUP PROJECT PATHS ---
# We explicitly add the project root to Python's path to find 'constants'
PROJECT_ROOT = r"D:\Projects\OmniTask_AI"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# --- 2. CONFIGURATION ---
# Path where the model 'base.pt' is located
# Whisper looks for {model_name}.pt inside this folder
MODEL_DIR = os.path.join(PROJECT_ROOT, "models", "audio_transcription")

# ⚠️ FFMPEG SETUP: Replace the path below with your actual FFmpeg bin folder
# If FFmpeg is already in your Windows System PATH, you can leave this empty string ""
FFMPEG_PATH = r"C:\Program Files\ffmpeg\bin" 

# Add FFmpeg to the environment path for this script execution
if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
    os.environ["PATH"] += os.pathsep + FFMPEG_PATH

# --- 3. IMPORTS FROM PROJECT ---
try:
    from constants import MAX_LENGTH
except ImportError:
    # Fallback if constants file is missing or has issues
    print("Warning: Could not import MAX_LENGTH from constants. Defaulting to 1000.")
    MAX_LENGTH = 1000

warnings.filterwarnings("ignore")

def transcribe_audio(audio_path, model_size="base"):
    """
    Transcribes audio using the local Whisper model.
    Returns: JSON-compatible dictionary { "file_name": str, "transcript": str }
    """
    # 1. Validate Audio File
    if not os.path.exists(audio_path):
        return {"error": f"File not found: {audio_path}"}

    # 2. Load Model
    # download_root tells Whisper where to look for 'base.pt' locally
    try:
        model = whisper.load_model(model_size, download_root=MODEL_DIR)
    except Exception as e:
        return {"error": f"Failed to load model from {MODEL_DIR}. Ensure 'base.pt' is there. Error: {str(e)}"}

    # 3. Transcribe
    try:
        result = model.transcribe(audio_path)
        full_text = result["text"].strip()
    except Exception as e:
        return {"error": f"Transcription failed during processing. Error: {str(e)}"}

    # 4. Truncate Text
    is_truncated = False
    if len(full_text) > MAX_LENGTH:
        transcribed_text = full_text[:MAX_LENGTH] + "... (truncated)"
        is_truncated = True
    else:
        transcribed_text = full_text

    # 5. Format Output
    response_data = {
        "file_name": os.path.basename(audio_path),
        "transcript": transcribed_text,
        "is_truncated": is_truncated
    }

    return response_data

