from openai import OpenAI
import base64, json

client = OpenAI(base_url="http://<TRITON_HOST>:9000/v1", api_key="sk-offline")

with open("doc.pdf","rb") as f:
    b64 = base64.b64encode(f.read()).decode()

resp = client.chat.completions.create(
    model="llama-4-scout-17b-16e",  # use the ID shown by GET /v1/models
    messages=[{
        "role":"user",
        "content":[
            {"type":"text","text":"Summarize the document in 10 bullets. Then list any tables you found with page numbers."},
            {"type":"input_file","mime_type":"application/pdf","data": b64}
        ]
    }],
)

print(resp.choices[0].message.content)
