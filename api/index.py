import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from backend.database import init_db
from backend.main import app as fastapi_app
from a2wsgi import ASGIMiddleware

# Initialize DB on cold start (lifespan events don't fire in serverless)
init_db()

# Convert ASGI (FastAPI) → WSGI for Vercel's Python runtime
app = ASGIMiddleware(fastapi_app)
