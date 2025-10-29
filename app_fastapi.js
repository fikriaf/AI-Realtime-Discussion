// Global state
let isListening = false;
let mediaRecorder = null;
let audioContext = null;
let conversationHistory = [];
let isSpeaking = false;
let currentAudio = null;
let audioQueue = [];
const MAX_HISTORY = 20;

// DOM elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const clearBtn = document.getElementById('clearBtn');
const statusEl = document.getElementById('status');
const userTranscriptEl = document.getElementById('userTranscript');
const aiResponseEl = document.getElementById('aiResponse');
const conversationHistoryEl = document.getElementById('conversationHistory');
const backendUrlInput = document.getElementById('backendUrl');
const backendStatusEl = document.getElementById('backendStatus');

// Event listeners
startBtn.addEventListener('click', startListening);
stopBtn.addEventListener('click', stopListening);
clearBtn.addEventListener('click', clearHistory);

// Check backend status on load
checkBackendStatus();

async function checkBackendStatus() {
    try {
        const response = await fetch(`${backendUrlInput.value}/`, {
            method: 'GET'
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.model_loaded) {
                backendStatusEl.textContent = '✅ Connected (Model Loaded)';
                backendStatusEl.style.color = '#4CAF50';
            } else {
                backendStatusEl.textContent = '⚠️ Connected (Model Not Loaded)';
                backendStatusEl.style.color = '#ff9800';
            }
        } else {
            backendStatusEl.textContent = '❌ Not Connected';
            backendStatusEl.style.color = '#f44336';
        }
    } catch (error) {
        backendStatusEl.textContent = '❌ Not Connected';
        backendStatusEl.style.color = '#f44336';
    }
}

// Initialize audio context
function initAudioContext() {
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
}

// Start listening to microphone
async function startListening() {
    try {
        updateStatus('🎤 Requesting microphone access...', false);
        
        const stream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 16000
            } 
        });
        
        initAudioContext();
        
        // Create media recorder
        const options = { mimeType: 'audio/webm' };
        mediaRecorder = new MediaRecorder(stream, options);
        
        let audioChunks = [];
        
        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };
        
        mediaRecorder.onstop = async () => {
            if (audioChunks.length > 0) {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                audioChunks = [];
                
                // Process the audio
                await processAudio(audioBlob);
            }
        };
        
        // Start recording in chunks
        mediaRecorder.start(1000);
        
        isListening = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        updateStatus('🎤 Listening...', true);
        
        // Auto-process every 3 seconds
        startContinuousListening();
        
    } catch (error) {
        console.error('Error accessing microphone:', error);
        updateStatus('❌ Error: ' + error.message, false);
        alert('Could not access microphone. Please check permissions.');
    }
}

// Continuous listening with auto-processing
function startContinuousListening() {
    if (!isListening) return;
    
    setTimeout(() => {
        if (isListening && mediaRecorder && mediaRecorder.state === 'recording') {
            // Stop current recording to process
            mediaRecorder.stop();
            
            // Restart recording after a brief pause
            setTimeout(() => {
                if (isListening) {
                    mediaRecorder.start(1000);
                    startContinuousListening();
                }
            }, 100);
        }
    }, 3000);
}

// Stop listening
function stopListening() {
    isListening = false;
    
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
    
    startBtn.disabled = false;
    stopBtn.disabled = true;
    updateStatus('⏹️ Stopped', false);
}

// Process audio and send to STT
async function processAudio(audioBlob) {
    try {
        const backendUrl = backendUrlInput.value;
        
        // Create form data
        const formData = new FormData();
        formData.append('audio', audioBlob, 'audio.webm');
        
        updateStatus('🔄 Transcribing...', true);
        
        const response = await fetch(`${backendUrl}/api/transcribe`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('STT request failed');
        }
        
        const data = await response.json();
        const transcript = data.text || '';
        
        if (transcript.trim()) {
            userTranscriptEl.textContent = transcript;
            
            // Pause TTS if speaking
            if (isSpeaking) {
                pauseTTS();
            }
            
            // Send to AI
            await sendToAI(transcript);
        }
        
        updateStatus('🎤 Listening...', true);
        
    } catch (error) {
        console.error('Error processing audio:', error);
        updateStatus('❌ Error: ' + error.message, false);
    }
}

// Send text to AI backend
async function sendToAI(userText) {
    try {
        updateStatus('🤔 AI thinking...', true);
        
        // Add user message to history
        conversationHistory.push({
            role: 'user',
            content: userText
        });
        
        // Maintain max history
        if (conversationHistory.length > MAX_HISTORY * 2) {
            conversationHistory = conversationHistory.slice(-MAX_HISTORY * 2);
        }
        
        updateConversationDisplay();
        
        const backendUrl = backendUrlInput.value;
        
        const response = await fetch(`${backendUrl}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: userText,
                history: conversationHistory
            })
        });
        
        if (!response.ok) {
            throw new Error('AI request failed');
        }
        
        const data = await response.json();
        const aiText = data.response;
        
        // Update history from backend
        conversationHistory = data.history;
        
        aiResponseEl.textContent = aiText;
        updateConversationDisplay();
        
        // Convert to speech
        await textToSpeech(aiText);
        
        updateStatus('🎤 Listening...', true);
        
    } catch (error) {
        console.error('Error sending to AI:', error);
        updateStatus('❌ Error: ' + error.message, false);
        aiResponseEl.textContent = 'Error: Could not get AI response. Make sure backend is running.';
    }
}

// Convert text to speech and play
async function textToSpeech(text) {
    try {
        // Break text into chunks for streaming
        const chunks = breakIntoChunks(text);
        
        for (const chunk of chunks) {
            await speakChunk(chunk);
            
            // Check if user started speaking
            if (!isListening || !isSpeaking) {
                break;
            }
        }
        
    } catch (error) {
        console.error('Error in TTS:', error);
    }
}

// Break text into smaller chunks
function breakIntoChunks(text) {
    // Split by sentences
    const sentences = text.match(/[^.!?]+[.!?]+/g) || [text];
    const chunks = [];
    
    for (const sentence of sentences) {
        if (sentence.length > 100) {
            // Break long sentences at commas
            const parts = sentence.split(',').map(p => p.trim()).filter(p => p);
            chunks.push(...parts);
        } else {
            chunks.push(sentence.trim());
        }
    }
    
    return chunks.filter(c => c);
}

// Speak a single chunk
async function speakChunk(text) {
    return new Promise(async (resolve, reject) => {
        try {
            const backendUrl = backendUrlInput.value;
            
            const response = await fetch(`${backendUrl}/api/tts`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            if (!response.ok) {
                throw new Error('TTS request failed');
            }
            
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            
            const audio = new Audio(audioUrl);
            currentAudio = audio;
            isSpeaking = true;
            
            audio.onended = () => {
                isSpeaking = false;
                URL.revokeObjectURL(audioUrl);
                resolve();
            };
            
            audio.onerror = (error) => {
                isSpeaking = false;
                reject(error);
            };
            
            await audio.play();
            
        } catch (error) {
            console.error('Error speaking chunk:', error);
            isSpeaking = false;
            resolve(); // Continue even if one chunk fails
        }
    });
}

// Pause TTS
function pauseTTS() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
    }
    isSpeaking = false;
}

// Clear conversation history
async function clearHistory() {
    try {
        const backendUrl = backendUrlInput.value;
        
        await fetch(`${backendUrl}/api/history`, {
            method: 'DELETE'
        });
        
        conversationHistory = [];
        conversationHistoryEl.innerHTML = '<p style="color: #999; text-align: center;">No messages yet. Start speaking!</p>';
        userTranscriptEl.textContent = 'Waiting for input...';
        aiResponseEl.textContent = 'Waiting for your message...';
        
        updateStatus('🗑️ History cleared', false);
        setTimeout(() => {
            if (isListening) {
                updateStatus('🎤 Listening...', true);
            } else {
                updateStatus('Ready', false);
            }
        }, 2000);
        
    } catch (error) {
        console.error('Error clearing history:', error);
    }
}

// Update status display
function updateStatus(message, listening) {
    statusEl.textContent = message;
    if (listening) {
        statusEl.classList.add('listening');
    } else {
        statusEl.classList.remove('listening');
    }
}

// Update conversation history display
function updateConversationDisplay() {
    if (conversationHistory.length === 0) {
        conversationHistoryEl.innerHTML = '<p style="color: #999; text-align: center;">No messages yet. Start speaking!</p>';
        return;
    }
    
    conversationHistoryEl.innerHTML = '';
    
    conversationHistory.forEach(msg => {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msg.role}`;
        
        const roleDiv = document.createElement('div');
        roleDiv.className = 'message-role';
        roleDiv.textContent = msg.role === 'user' ? '👤 You' : '🤖 AI Assistant';
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = msg.content;
        
        messageDiv.appendChild(roleDiv);
        messageDiv.appendChild(contentDiv);
        conversationHistoryEl.appendChild(messageDiv);
    });
    
    // Scroll to bottom
    conversationHistoryEl.scrollTop = conversationHistoryEl.scrollHeight;
}

// Initialize
updateStatus('Ready', false);

// Periodic backend status check
setInterval(checkBackendStatus, 30000); // Check every 30 seconds
