# chat.py (DROP-IN)
# Minimal PDF support + (optional) image sidecar proxy to a local vLLM OpenAI server.
# Keeps Triton OpenAI frontend on :9000. Requests without PDFs/images follow the original text path.

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
import os, base64, requests
from typing import Any, Dict, List

from .pdf_processor import process_pdf_bytes, build_system_preamble
from .media_validate import preflight_input_image

router = APIRouter()

# Limits & toggles
FILE_MAX = int(os.getenv("PDF_MAX_BYTES", "10000000"))            # 10 MB PDF hard cap
VLLM_OPENAI_BASE = os.getenv("VLLM_OPENAI_BASE", "disabled").strip()  # "disabled" or "http://127.0.0.1:8000/v1"

# ---- IMPORT SHIM: your existing text-only handler ----
# Replace with your real import if needed:
_handle_text_only = None
_import_errors = []

for dotted in (
    "python.openai.openai_frontend.text:handle_text_only",
    "python.openai.openai_frontend.routes_chat:handle_text_only",
    "python.openai.openai_frontend.chat_text:handle_text_only",
):
    try:
        mod, func = dotted.split(":")
        _handle_text_only = getattr(__import__(mod, fromlist=[func]), func)
        break
    except Exception as e:
        _import_errors.append(f"{dotted} -> {type(e).__name__}: {e}")

if _handle_text_only is None:
    raise RuntimeError(
        "Could not locate the original text-only handler. Update the import shim in chat.py. Tried:\n  - "
        + "\n  - ".join(_import_errors)
    )

# ---- Utilities ----

def _is_pdf_part(part: Dict[str, Any]) -> bool:
    return (
        part.get("type") == "input_file"
        and part.get("mime_type") == "application/pdf"
        and ("data" in part)
        and isinstance(part["data"], str)
        and len(part["data"]) > 0
    )

def _has_input_images(messages: List[Dict[str, Any]]) -> bool:
    for m in messages or []:
        c = m.get("content")
        if isinstance(c, list):
            for p in c:
                if p.get("type") == "input_image":
                    return True
    return False

def _preflight_images(messages: List[Dict[str, Any]]):
    for m in messages or []:
        c = m.get("content")
        if isinstance(c, list):
            for p in c:
                if p.get("type") == "input_image":
                    preflight_input_image(p)

def _normalize_messages_for_pdf(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Replace any base64 PDF part with a compact analysis pack (text)."""
    new_msgs: List[Dict[str, Any]] = []
    for m in messages or []:
        c = m.get("content")
        if not isinstance(c, list):
            new_msgs.append(m)
            continue

        new_content: List[Dict[str, Any]] = []
        for part in c:
            if _is_pdf_part(part):
                try:
                    pdf_bytes = base64.b64decode(part["data"])
                except Exception:
                    raise HTTPException(status_code=400, detail="Invalid base64 for PDF")
                if len(pdf_bytes) > FILE_MAX:
                    raise HTTPException(status_code=413, detail="PDF too large")

                pack = process_pdf_bytes(pdf_bytes)
                system_text = build_system_preamble(pack)
                new_content.append({"type": "text", "text": system_text})
            else:
                new_content.append(part)

        new_msgs.append({**m, "content": new_content})
    return new_msgs

# ---- Route ----

@router.post("/v1/chat/completions")
async def chat_completions(req: Request):
    """
    Behavior:
      - PDFs (base64) → analysis pack text → continues via original text path.
      - Images (base64) → validate; if VLLM_OPENAI_BASE=disabled → 400; else → forward unchanged to local vLLM OpenAI server and stream back.
      - Otherwise → original text path unchanged.
    """
    payload = await req.json()
    messages = payload.get("messages", [])

    # PDFs → analysis text
    needs_pdf = any(
        isinstance(m.get("content"), list)
        and any(_is_pdf_part(p) for p in m["content"])
        for m in messages
    )
    if needs_pdf:
        payload = {**payload, "messages": _normalize_messages_for_pdf(messages)}

    # Images → either 400 or proxy to local vLLM OpenAI server
    if _has_input_images(payload.get("messages", [])):
        try:
            _preflight_images(payload.get("messages", []))
        except ValueError as e:
            return JSONResponse(
                status_code=400,
                content={"error": {"type": "invalid_image", "message": str(e)}},
            )

        if VLLM_OPENAI_BASE == "disabled":
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "type": "unsupported_media",
                        "message": (
                            "Image inputs are disabled on this deployment. "
                            "Set VLLM_OPENAI_BASE to a local vLLM OpenAI server to enable."
                        ),
                    }
                },
            )

        # Forward unchanged to vLLM's OpenAI server (local/sidecar), stream response back
        try:
            r = requests.post(
                f"{VLLM_OPENAI_BASE}/chat/completions",
                json=payload,
                stream=True,
                timeout=300,
            )
        except requests.RequestException as e:
            return JSONResponse(
                status_code=502,
                content={"error": {"type": "backend_unreachable", "message": str(e)}},
            )
        return StreamingResponse(
            r.iter_content(chunk_size=8192),
            status_code=r.status_code,
            media_type=r.headers.get("content-type", "application/json"),
        )

    # No PDFs, no images → original text path
    return await _handle_text_only(payload)
