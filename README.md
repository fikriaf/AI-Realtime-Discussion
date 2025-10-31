# AI Voice Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![LM Studio](https://img.shields.io/badge/LM%20Studio-Compatible-FF6B6B?style=flat)](https://lmstudio.ai/)

A real-time AI voice assistant with natural human-like conversation capabilities. Built for low latency and seamless interaction using browser-based speech recognition and local LLM inference.

## Features

- **Real-time Speech Recognition** - Browser-based speech-to-text with zero latency
- **Streaming AI Responses** - Token-by-token generation for instant feedback
- **Natural Conversation Flow** - Context-aware dialogue with conversation history
- **Interrupt Handling** - Stop AI mid-sentence for natural back-and-forth
- **Local LLM Integration** - Works with LM Studio for privacy and offline capability
- **Dual AI Mode** - Support for multiple AI personalities in conversation
- **Text-to-Speech** - Natural voice synthesis for AI responses
- **Docker Support** - Easy deployment with containerization

## Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **AI Model**: Qwen 3 (0.6B) via LM Studio
- **Speech**: Web Speech API (Browser), Faster Whisper
- **Audio**: SoundDevice, NumPy
- **Deployment**: Docker, Uvicorn

## Quick Start

### Prerequisites

- Python 3.8 or higher
- LM Studio with Qwen 3 model loaded
- Modern browser (Chrome/Edge recommended)
- Microphone access

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd ai-voice-assistant
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Start LM Studio
   - Open LM Studio
   - Load Qwen 3 (0.6B) model
   - Start the local server on port 1234

4. Run the backend
```bash
python backend_realtime.py
```

5. Open the web interface
   - Open `BUKA_INI.html` in your browser
   - Click "BUKA VOICE ASSISTANT"
   - Allow microphone access
   - Start talking

### Docker Deployment

```bash
docker-compose up -d
```

The service will be available at `http://localhost:8000`

## Usage

### Single AI Mode

Open `index_browser_speech.html` for standard voice assistant interaction.

### Dual AI Mode

Open `index_dual_speech.html` for conversations between two AI personalities.

### API Endpoints

- `POST /api/chat` - Send text and get AI response
- `POST /api/stream_chat` - Streaming AI responses
- `POST /api/transcribe` - Audio transcription
- `POST /api/tts` - Text-to-speech synthesis
- `GET /api/history` - Get conversation history
- `DELETE /api/history` - Clear conversation history

Full API documentation available at `http://localhost:8000/docs`

## Configuration

Edit `backend_realtime.py` to configure:

```python
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"
MAX_HISTORY = 20  # Conversation context length
```

## Project Structure

```
.
├── backend_realtime.py          # Main FastAPI backend
├── backend_realtime_ollama.py   # Ollama integration variant
├── tes.py                       # Real-time transcription test
├── index_browser_speech.html    # Single AI interface
├── index_dual_speech.html       # Dual AI interface
├── BUKA_INI.html               # Landing page
├── docker-compose.yml          # Docker configuration
├── Dockerfile                  # Container definition
└── START_ALL.bat              # Windows startup script
```

## Performance Optimization

- **Low Latency**: Streaming responses start in <100ms
- **Efficient Context**: Last 8 messages for speed
- **Short Responses**: Max 50 tokens for natural interruption
- **Browser Speech**: Native Web Speech API for zero-latency recognition
- **Chunked Audio**: Progressive TTS synthesis

## Browser Compatibility

| Browser | Speech Recognition | Text-to-Speech | Status |
|---------|-------------------|----------------|--------|
| Chrome  | Yes               | Yes            | Recommended |
| Edge    | Yes               | Yes            | Recommended |
| Firefox | Limited           | Yes            | Partial |
| Safari  | Limited           | Yes            | Partial |

## Troubleshooting

### Backend not connecting
- Ensure LM Studio is running on port 1234
- Check if the model is loaded in LM Studio
- Verify firewall settings

### Microphone not working
- Grant microphone permissions in browser
- Check system audio settings
- Use HTTPS or localhost only (browser security requirement)

### Poor audio quality
- Use headphones to prevent echo
- Reduce background noise
- Adjust microphone sensitivity in system settings

## Contributing

Contributions are welcome. Please open an issue first to discuss proposed changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LM Studio](https://lmstudio.ai/) - Local LLM inference
- [Faster Whisper](https://github.com/guillaumekln/faster-whisper) - Speech recognition
- [Qwen](https://github.com/QwenLM/Qwen) - Language model

## Support

For issues and questions, please open an issue on the repository.

---

Built with focus on natural conversation and real-time performance.
