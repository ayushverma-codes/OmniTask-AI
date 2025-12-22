import os
from constants import BASE_UPLOAD_DIR

def init_storage():
    os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)
