def app(environ, start_response):
    import json
    start_response("200 OK", [("Content-Type", "application/json")])
    return [json.dumps({"hello": "world", "path": environ.get("PATH_INFO", "?")}).encode()]
