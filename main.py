from fastapi import FastAPI, UploadFile, Form
from contextlib import asynccontextmanager
import uvicorn

from entity.config import init_storage
from components.file_handler import save_file
from pipeline.graph import init_db, save_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_storage()
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/chat")
async def chat(
    thread_id: str = Form(...),
    text: str = Form(""),
    file: UploadFile | None = None
):
    file_path = None

    if file:
        file_path = await save_file(file, thread_id)

    save_message(
        thread_id=thread_id,
        text=text,
        file_path=file_path
    )

    if file_path:
        return {
            "message": (
                "I have received your file and saved it to local storage. "
                "What should I do?"
            )
        }

    return {"message": "I received your message. What should I do?"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
