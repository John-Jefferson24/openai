curl -s http://<HOST>:9000/v1/chat/completions \
 -H 'content-type: application/json' \
 -d '{"model":"<YOUR_MODEL_ID>","messages":[{"role":"user","content":"JUST_STRING_PING"}]}'

 curl -s http://<HOST>:9000/v1/chat/completions \
 -H 'content-type: application/json' \
 -d '{"model":"<YOUR_MODEL_ID>","messages":[{"role":"user","content":[{"type":"text","text":"ARRAY_TEXT_PING"}]}]}'


 curl -s http://localhost:9000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "your-model-name",
    "messages": [{"role": "user", "content": "test all sampling params"}],
    "max_tokens": 32,
    "temperature": 0.7,
    "top_p": 0.5,
    "top_k": 5,
    "presence_penalty": 1.2,
    "frequency_penalty": 0.8,
    "seed": 42,
    "n": 2,
    "stop": ["END"],
    "logprobs": 5,
    "logit_bias": {"32": -5, "100": 3},
    "ignore_eos": true
  }' | jq

