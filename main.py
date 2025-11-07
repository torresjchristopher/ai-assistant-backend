# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI

app = FastAPI()
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# Allow your frontend domain to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yukora.site", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/api/chat")
def chat(req: ChatRequest):
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
    for h in req.history:
        messages.append({"role": "user", "content": h["user"]})
        messages.append({"role": "assistant", "content": h["bot"]})
    messages.append({"role": "user", "content": req.message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )

    return {"response": response.choices[0].message.content.strip()}
