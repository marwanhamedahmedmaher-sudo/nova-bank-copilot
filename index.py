"""Entry point for the hosted copy on Vercel, which looks for a FastAPI `app` in index.py. Steps in docs/hosting.md."""
from app.main import app  # noqa: F401
