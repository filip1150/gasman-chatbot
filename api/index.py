import sys
import os
import json
import traceback

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)
sys.path.insert(0, os.path.join(_root, "backend"))  # so "from database import" works

_error_msg = None

try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_root, ".env"))
    from backend.database import init_db, SessionLocal
    from backend.knowledge_base import sync_from_pinecone
    init_db()
    # Repopulate SQLite from Pinecone on every cold start (ephemeral /tmp)
    _db = SessionLocal()
    try:
        sync_from_pinecone(_db)
    finally:
        _db.close()
    from backend.main import app as _fastapi_app
    from a2wsgi import ASGIMiddleware
    _wsgi_app = ASGIMiddleware(_fastapi_app)
    _error_msg = None
except Exception:
    _error_msg = traceback.format_exc()
    _wsgi_app = None


def app(environ, start_response):
    if _wsgi_app is not None:
        return _wsgi_app(environ, start_response)
    start_response("500 Internal Server Error", [("Content-Type", "application/json")])
    return [json.dumps({"error": _error_msg}).encode()]
