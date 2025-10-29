"""
Real-time AI Voice Assistant - Natural Human-like Conversation
Using Ollama Phi3 Mini for local inference
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import tempfile
import os
import io
import ollama
import json
import asyncio

app = FastAPI(title="AI Voice Assistant - Real-time (Ollama)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
OLLAMA_MODEL = "phi3:mini"
conversation_history = []
MAX_HISTORY = 20

class ChatRequest(BaseModel):
    text: str
    history: Optional[List[dict]] = []

class ChatResponse(BaseModel):
    response: str
    history: List[dict]

class TTSRequest(BaseModel):
    text: str


def check_ollama():
    """Check Ollama connection and model availability"""
    try:
        models = ollama.list()
        model_names = [m['name'] for m in models.get('models', [])]
        
        if OLLAMA_MODEL in model_names or any(OLLAMA_MODEL in name for name in model_names):
            print(f"✅ Ollama connected - Model: {OLLAMA_MODEL}")
            return True
        else:
            print(f"⚠️ Model {OLLAMA_MODEL} not found. Available models: {model_names}")
            print(f"💡 Run: ollama pull {OLLAMA_MODEL}")
            return False
    except Exception as e:
        print(f"⚠️ Ollama not accessible: {e}")
        print(f"💡 Make sure Ollama is running: ollama serve")
        return False


@app.on_event("startup")
async def startup_event():
    print("=" * 70)
    print("🎙️ Real-time AI Voice Assistant - Natural Conversation (Ollama)")
    print("=" * 70)
    print()
    print(f"🤖 Model: {OLLAMA_MODEL}")
    print(f"⚡ Mode: Real-time streaming")
    print(f"🎯 Goal: Natural human-like conversation")
    print()
    check_ollama()
    print()
    print("🚀 Server ready on: http://localhost:8000")
    print("=" * 70)


@app.get("/")
async def root():
    ollama_connected = check_ollama()
    return {
        "status": "running",
        "backend": "Ollama",
        "ollama_connected": ollama_connected,
        "model": OLLAMA_MODEL,
        "mode": "real-time streaming",
        "optimizations": [
            "Low latency response",
            "Streaming text generation",
            "Chunked audio synthesis",
            "Context-aware conversation",
            "Natural flow optimization"
        ],
        "endpoints": {
            "chat": "/api/chat",
            "stream_chat": "/api/stream_chat",
            "tts": "/api/tts",
            "history": "/api/history"
        }
    }


@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe endpoint - use browser speech for best results"""
    return JSONResponse({
        "text": "",
        "success": False,
        "message": "Use browser speech recognition for real-time performance"
    })


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Generate AI response with optimizations for natural conversation
    """
    global conversation_history
    
    try:
        # Add user message
        user_message = {"role": "user", "content": request.text}
        conversation_history.append(user_message)
        
        # Maintain history
        if len(conversation_history) > MAX_HISTORY * 2:
            conversation_history = conversation_history[-MAX_HISTORY * 2:]
        
        # Build optimized prompt for natural conversation
        messages = [
            {
                "role": "system",
                "content": (
                    "You're a chill person chatting. Keep it real and short:\n"
                    "- Simple stuff: 3-5 words (\"cool\", \"nice\", \"I feel you\")\n"
                    "- Normal chat: 1 sentence max\n"
                    "- Deep stuff: 2 sentences max\n\n"
                    "Talk like texting: yeah, nah, totally, I get it, fair enough.\n"
                    "DON'T ask questions back. DON'T be philosophical. DON'T explain.\n"
                    "Just react and keep it moving."
                )
            }
        ]
        
        # Add recent context (last 8 messages for speed)
        messages.extend(conversation_history[-8:])
        
        print(f"💬 User: {request.text}")
        
        # Send to Ollama with DYNAMIC response settings
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages,
            options={
                "temperature": 0.7,      # Focused but natural
                "num_predict": 35,       # Shorter max (dynamic: 5-35 tokens)
                "top_p": 0.85,
                "top_k": 30,
                "repeat_penalty": 1.3,
                "stop": ["\n\n"],        # Stop at double newline only
            }
        )
        
        ai_text = response['message']['content'].strip()
        
        # Clean up response for natural speech
        ai_text = ai_text.replace("*", "").replace("_", "")  # Remove markdown
        ai_text = " ".join(ai_text.split())  # Normalize whitespace
        
        # Remove emojis and emoticons
        import re
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        ai_text = emoji_pattern.sub('', ai_text)
        
        # Remove common emoticons
        ai_text = re.sub(r'[:;=][oO\-]?[D\)\]\(\[pP/\\OpP]', '', ai_text)
        ai_text = ai_text.strip()
        
        # Add to history
        assistant_message = {"role": "assistant", "content": ai_text}
        conversation_history.append(assistant_message)
        
        print(f"🤖 AI: {ai_text}")
        
        return ChatResponse(
            response=ai_text,
            history=conversation_history
        )
    
    except Exception as e:
        print(f"❌ Error: {e}")
        if "connection" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="Cannot connect to Ollama. Make sure it's running: ollama serve"
            )
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/stream_chat")
async def stream_chat(request: ChatRequest):
    """
    Streaming chat for even lower latency
    Tokens arrive as they're generated
    """
    global conversation_history
    
    try:
        user_message = {"role": "user", "content": request.text}
        conversation_history.append(user_message)
        
        if len(conversation_history) > MAX_HISTORY * 2:
            conversation_history = conversation_history[-MAX_HISTORY * 2:]
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You're a chill person chatting. Keep it real and short:\n"
                    "- Simple stuff: 3-5 words (\"cool\", \"nice\", \"I feel you\")\n"
                    "- Normal chat: 1 sentence max\n"
                    "- Deep stuff: 2 sentences max\n\n"
                    "Talk like texting: yeah, nah, totally, I get it, fair enough.\n"
                    "DON'T ask questions back. DON'T be philosophical. DON'T explain.\n"
                    "Just react and keep it moving."
                )
            }
        ]
        messages.extend(conversation_history[-6:])
        
        print(f"💬 User: {request.text}")
        
        async def generate():
            full_response = ""
            
            try:
                # Stream from Ollama with DYNAMIC response settings
                stream = ollama.chat(
                    model=OLLAMA_MODEL,
                    messages=messages,
                    stream=True,
                    options={
                        "temperature": 0.7,      # Focused but natural
                        "num_predict": 35,       # Shorter max (dynamic: 5-35 tokens)
                        "top_p": 0.85,
                        "top_k": 30,
                        "repeat_penalty": 1.3,
                        "stop": ["\n\n"],        # Stop at double newline only
                    }
                )
                
                for chunk in stream:
                    if 'message' in chunk:
                        content = chunk['message'].get('content', '')
                        if content:
                            full_response += content
                            yield f"data: {json.dumps({'token': content})}\n\n"
                
                # Clean up response
                import re
                full_response = full_response.replace("*", "").replace("_", "")
                emoji_pattern = re.compile("["
                    u"\U0001F600-\U0001F64F"
                    u"\U0001F300-\U0001F5FF"
                    u"\U0001F680-\U0001F6FF"
                    u"\U0001F1E0-\U0001F1FF"
                    u"\U00002702-\U000027B0"
                    u"\U000024C2-\U0001F251"
                    "]+", flags=re.UNICODE)
                full_response = emoji_pattern.sub('', full_response)
                full_response = re.sub(r'[:;=][oO\-]?[D\)\]\(\[pP/\\OpP]', '', full_response)
                full_response = full_response.strip()
                
                # Save to history
                assistant_message = {"role": "assistant", "content": full_response}
                conversation_history.append(assistant_message)
                
                print(f"🤖 AI: {full_response}")
                
                yield f"data: {json.dumps({'done': True, 'full_text': full_response})}\n\n"
                
            except Exception as e:
                print(f"❌ Stream error: {e}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
        
        return StreamingResponse(generate(), media_type="text/event-stream")
    
    except Exception as e:
        print(f"❌ Stream error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Fast TTS for real-time response
    """
    try:
        text = request.text
        
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        import pyttsx3
        engine = pyttsx3.init()
        
        # Optimize for natural speech
        engine.setProperty('rate', 160)  # Slightly faster for natural flow
        engine.setProperty('volume', 1.0)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio:
            engine.save_to_file(text, temp_audio.name)
            engine.runAndWait()
            temp_path = temp_audio.name
        
        with open(temp_path, 'rb') as f:
            audio_data = f.read()
        
        os.unlink(temp_path)
        
        return StreamingResponse(io.BytesIO(audio_data), media_type="audio/wav")
    
    except Exception as e:
        print(f"❌ TTS error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/history")
async def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history = []
    return {"status": "success", "message": "History cleared"}


@app.get("/api/history")
async def get_history():
    """Get conversation history"""
    return {"history": conversation_history}


if __name__ == "__main__":
    import uvicorn
    print()
    print("=" * 70)
    print("🎙️ Real-time AI Voice Assistant (Ollama)")
    print("=" * 70)
    print()
    print("🎯 Optimized for natural human-like conversation")
    print("⚡ Low latency, streaming responses")
    print("💬 Context-aware, engaging dialogue")
    print()
    print(f"🤖 Model: {OLLAMA_MODEL}")
    print(f"🔧 Backend: Ollama (local)")
    print()
    print("=" * 70)
    print()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
