curl -s http://<HOST>:9000/v1/chat/completions \
 -H 'content-type: application/json' \
 -d '{"model":"<YOUR_MODEL_ID>","messages":[{"role":"user","content":"JUST_STRING_PING"}]}'

 curl -s http://<HOST>:9000/v1/chat/completions \
 -H 'content-type: application/json' \
 -d '{"model":"<YOUR_MODEL_ID>","messages":[{"role":"user","content":[{"type":"text","text":"ARRAY_TEXT_PING"}]}]}'
