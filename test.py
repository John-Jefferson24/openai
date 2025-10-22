import base64
from openai import OpenAI

client = OpenAI(
    base_url="https://your.triton.server/v1",
    api_key="your_api_key"
)

# 1. Read and encode the PDF
with open("document.pdf", "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

# 2. Build the message payload
response = client.chat.completions.create(
    model="your-model-name",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_file",
                    "input_file": {
                        "data": encoded,
                        "mime_type": "application/pdf",
                        "name": "document.pdf"
                    }
                },
                {
                    "type": "text",
                    "text": "Summarize this document in a few paragraphs."
                }
            ]
        }
    ]
)

# 3. Print the model’s output
print(response.choices[0].message.content)
