import os
import uuid
import aiofiles
from fastapi import UploadFile
from constants import BASE_UPLOAD_DIR


async def save_file(file: UploadFile, thread_id: str) -> str:
    """
    Correct async saver for FastAPI UploadFile
    """
    thread_dir = os.path.join(BASE_UPLOAD_DIR, thread_id)
    os.makedirs(thread_dir, exist_ok=True)

    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(thread_dir, filename)

    async with aiofiles.open(file_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            await out_file.write(chunk)

    await file.close()
    return file_path
