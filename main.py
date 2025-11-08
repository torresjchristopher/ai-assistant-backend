from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import requests
import json
from fastapi.responses import StreamingResponse
import os

app = FastAPI()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
SERPER_KEY = os.getenv("SERPER_API_KEY")

# Allow frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yukora.site", "http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/api/chat-stream")
def chat_stream(req: ChatRequest):
    def generate():
        messages = [{"role": "system", "content": "You are a smart assistant with live search ability."}]
        
        # Properly handle history with roles
        for h in req.history:
            # Each history item should have 'role' and 'content'
            if isinstance(h, dict) and "role" in h and "content" in h:
                messages.append({"role": h["role"], "content": h["content"]})
        
        # Add the current user message
        messages.append({"role": "user", "content": req.message})

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            stream=True,
        )
        
        for chunk in completion:
            if chunk.choices[0].delta.content:
                yield json.dumps({"delta": chunk.choices[0].delta.content}) + "\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.get("/api/search")
def search(q: str):
    headers = {"X-API-KEY": SERPER_KEY, "Content-Type": "application/json"}
    payload = {"q": q, "num": 5}
    r = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
    data = r.json()
    return {"results": data.get("organic", [])}