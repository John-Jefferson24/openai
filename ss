command:
  - /bin/bash
  - -lc
  - |
    # 1) start local vLLM OpenAI server on 127.0.0.1:8000
    python -m vllm.entrypoints.openai.api_server \
      --model /model_files/llama-4-scout-17b-16e \
      --host 127.0.0.1 --port 8000 \
      --dtype auto --gpu-memory-utilization 0.90 &

    # 2) export the proxy base so the frontend can route image requests
    export VLLM_OPENAI_BASE=http://127.0.0.1:8000/v1

    # 3) start Triton OpenAI frontend on :9000 (your existing line)
    python3 /opt/tritonserver/python/openai/openai_frontend/main.py \
      --model-repository ${MODEL_REPOSITORY} \
      --tokenizer ${TOKENIZER}
