import uvicorn
import os
import sys

# Ensure UTF-8 output on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure current dir is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import HOST, PORT

if __name__ == "__main__":
    print("=" * 65)
    print("Cognify - Intelligent Adaptive Learning Platform")
    print(f"Server running at: http://{HOST}:{PORT}")
    print("=" * 65)
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
