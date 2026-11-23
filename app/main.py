# TODO (week 1): FastAPI app with an /ask endpoint. Write this yourself.
from fastapi import FastAPI, Depends
import importlib
import asyncio
import os
from pydantic import BaseModel, Field
from app.db.database import SessionLocal, Message, get_db, init_db

ollama = importlib.import_module("ollama")
client = ollama.Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))
app = FastAPI()
init_db()

class ChatRequest(BaseModel):
    user_id: str = "default"
    message: str = Field(min_length=1, max_length=10000)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/chat")
async def chat (payload: ChatRequest, db = Depends(get_db)):
   user_id = payload.user_id
   message = payload.message
   # Save the user's message to the database
   user_message = Message(user_id=user_id, role="user", content=message)
   db.add(user_message)
   db.commit()

    # Get the full message history for the user
   message_history = db.query(Message).filter(Message.user_id == user_id).order_by(Message.id).all()
   conversation = [{"role": msg.role, "content": msg.content} for msg in message_history]

    # Generate a response from the model
   response = await asyncio.to_thread(
        client.chat,
        model="llama3.2",
        messages=conversation)

   reply = response["message"]["content"]

    # Save the model's response to the database
   model_message = Message(user_id=user_id, role="assistant", content=reply)
   db.add(model_message)
   db.commit()
   

   return {"reply": reply}

@app.get("/history/{user_id}")
async def get_history(user_id: str):
    db = SessionLocal()
    rows = db.query(Message).filter(Message.user_id == user_id).order_by(Message.id).all()
    result = [{"role": m.role, "content": m.content, "time": m.created_at} for m in rows]
    return result