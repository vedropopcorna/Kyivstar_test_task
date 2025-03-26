from fastapi import FastAPI
from app.api.endpoints import router as api_router
import os
from huggingface_hub import login
from dotenv import load_dotenv
load_dotenv()


huggingface_token = os.getenv("HUGGINGFACE_API_KEY")
if not huggingface_token:
    raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

login(token=huggingface_token)
app = FastAPI()
app.include_router(api_router)

def get_app():
    return app