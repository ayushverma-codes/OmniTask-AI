from youtube_transcript_api import YouTubeTranscriptApi
import re

def fetch_youtube_transcript(url: str):
    try:
        # 1. Regex to find Video ID (works for youtube.com and youtu.be)
        video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
        if not video_id_match:
            return "Error: Could not parse Video ID from URL."
        
        video_id = video_id_match.group(1)

        # 2. Fetch Transcript
        # FIX: Instantiate the class first, then call .fetch()
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        
        # 3. Join text
        # FIX: The result is an object, access text via attribute (.text), not key (['text'])
        full_text = " ".join([entry.text for entry in transcript])
        
        return {
            "video_id": video_id,
            "transcript_length": len(full_text),
            "transcript": full_text
        }
        
    except Exception as e:
        return {"error": "Transcript unavailable or disabled.", "details": str(e)}

