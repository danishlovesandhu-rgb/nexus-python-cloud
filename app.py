import os
import secrets
import subprocess
import sys
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

APP_KEY = os.environ.get("APP_KEY", "")
MAX_FILE_BYTES = 100_000
MAX_OUTPUT_BYTES = 20_000
TIMEOUT_SECONDS = 10

app = FastAPI(title="NEXUS-X Python Runner")

def check_key(x_api_key: str | None):
    if not APP_KEY:
        raise HTTPException(status_code=503, detail="Server is not configured: APP_KEY is missing.")
    if not x_api_key or not secrets.compare_digest(x_api_key, APP_KEY):
        raise HTTPException(status_code=401, detail="Invalid access key.")

@app.get("/", response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / "templates" / "index.html").read_text(encoding="utf-8")

@app.get("/health")
def health():
    return {"status": "ok", "service": "NEXUS-X Python Runner"}

@app.post("/run")
async def run_script(
    script: UploadFile = File(...),
    x_api_key: str | None = Header(default=None),
):
    check_key(x_api_key)

    filename = Path(script.filename or "script.py").name
    if not filename.endswith(".py"):
        raise HTTPException(status_code=400, detail="Only .py files are accepted.")

    source = await script.read(MAX_FILE_BYTES + 1)
    if len(source) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="File too large (100 KB maximum).")
    try:
        source.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Script must be UTF-8 text.")

    # Important: subprocess limits reduce accidental runaway jobs; they are NOT a
    # security sandbox. Only run code you wrote and trust. Do not offer this publicly.
    with tempfile.TemporaryDirectory(prefix="nexus_job_") as temp_dir:
        script_path = Path(temp_dir) / "user_script.py"
        script_path.write_bytes(source)
        try:
            result = subprocess.run(
                [sys.executable, "-I", str(script_path)],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                check=False,
                env={"PATH": os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"},
            )
            stdout = result.stdout[-MAX_OUTPUT_BYTES:]
            stderr = result.stderr[-MAX_OUTPUT_BYTES:]
            return JSONResponse({
                "status": "finished",
                "exit_code": result.returncode,
                "stdout": stdout,
                "stderr": stderr,
                "note": "Execution completed. This service is for your own trusted scripts only."
            })
        except subprocess.TimeoutExpired as exc:
            out = exc.stdout or ""
            err = exc.stderr or ""
            if isinstance(out, bytes): out = out.decode("utf-8", "replace")
            if isinstance(err, bytes): err = err.decode("utf-8", "replace")
            return JSONResponse({
                "status": "timeout",
                "exit_code": None,
                "stdout": out[-MAX_OUTPUT_BYTES:],
                "stderr": (err + "\nStopped: 10-second time limit reached.")[-MAX_OUTPUT_BYTES:]
            }, status_code=408)
