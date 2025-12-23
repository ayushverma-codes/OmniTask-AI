# D:\Projects\OmniTask_AI\main.py

import traceback
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from entity.config import init_storage
from components.file_handler import save_file
from pipeline.graph import init_db, save_message
from pipeline.manager import process_request

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_storage()
        init_db()
        print("✅ Storage and DB initialized.")
    except Exception as e:
        print(f"❌ Startup Error: {e}")
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/chat")
async def chat(
    thread_id: str = Form(...),
    text: str = Form(""),
    file: UploadFile | None = None
):
    try:
        # 1. Save File
        file_path = None
        if file:
            file_path = await save_file(file, thread_id)

        # 2. Save User Message
        save_message(thread_id=thread_id, text=text, file_path=file_path)

        # 3. Process Request (The Brain)
        response_text = await process_request(thread_id, text, file_path)

        # 4. Save Bot Response
        save_message(thread_id=thread_id, text=response_text, file_path=None)

        return {"message": response_text}

    except Exception as e:
        # Print full trace to console for debugging
        traceback.print_exc()
        
        # Return JSON error so UI doesn't crash
        return JSONResponse(
            status_code=500, 
            content={"message": f"I encountered an internal error: {str(e)}"}
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)