# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
import os, requests

# Initialize FastAPI
app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yukora.site", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Serper.dev for live search
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Define request model
class ChatRequest(BaseModel):
    message: str
    history: list = []

# --- Streaming Chat Endpoint ---
@app.post("/api/chat/stream")
async def chat_stream(req: ChatRequest):
    messages = [{"role": "system", "content": "You are Yukora — an elegant, intelligent assistant with an Apple-like tone: calm, precise, minimal, and helpful."}]
    for h in req.history:
        messages.append({"role": "user", "content": h.get("user", "")})
        messages.append({"role": "assistant", "content": h.get("bot", "")})
    messages.append({"role": "user", "content": req.message})

    def generate():
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    return StreamingResponse(generate(), media_type="text/event-stream")

# --- Search Endpoint ---
@app.post("/api/search")
def search_web(query: dict):
    q = query.get("query", "")
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": q}
    try:
        r = requests.post("https://google.serper.dev/search", headers=headers, json=payload)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# --- Health Check ---
@app.get("/")
def health_check():
    return {"status": "ok", "message": "Yukora backend running"}
