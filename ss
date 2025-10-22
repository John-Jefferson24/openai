python - <<'PY'
import inspect, sys
from importlib import import_module
m = import_module("openai_frontend.schemas.openai")
print("Loaded from:", m.__file__)
print("Has TypeInputFile? ", hasattr(m, "ChatCompletionRequestMessageContentPartInputFile"))
print("Has TypeInputImage? ", hasattr(m, "ChatCompletionRequestMessageContentPartInputImage"))
PY

python - <<'PY'
from importlib import import_module
r = import_module("openai_frontend.frontend.fastapi.routers.chat")
src = open(r.__file__, "r", encoding="utf-8").read()
print("Router:", r.__file__)
print("Has _has_image_parts:", "_has_image_parts" in src)
print("Reads VLLM_OPENAI_BASE:", "VLLM_OPENAI_BASE" in src)
PY

python - <<'PY'
import os
print("VLLM_OPENAI_BASE =", os.getenv("VLLM_OPENAI_BASE"))
PY

curl -s http://localhost:9000/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"whatever","messages":[{"role":"user","content":"ping"}]}'


