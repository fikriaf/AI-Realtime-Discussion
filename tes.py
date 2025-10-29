import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
import queue, threading

# Load model tiny, INT8
model = WhisperModel("tiny", device="cpu")

audio_q = queue.Queue()
last_text = ""  # untuk menyimpan teks sebelumnya

# Callback mic
def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_q.put(indata.copy())

# Fungsi realtime transcription smooth
def transcribe_stream():
    global last_text
    samplerate = 16000
    block_size = int(3 * samplerate)    # 3 detik
    overlap = int(1 * samplerate)       # 1 detik overlap
    audio_buffer = np.zeros(0, dtype=np.float32)

    while True:
        data = audio_q.get()
        audio_buffer = np.concatenate((audio_buffer, data[:, 0]))

        while len(audio_buffer) >= block_size:
            segment = audio_buffer[:block_size]
            audio_buffer = audio_buffer[block_size - overlap:]  # simpan overlap

            # Normalisasi audio
            segment = segment / (np.max(np.abs(segment)) + 1e-9)

            # Transcribe
            segments, _ = model.transcribe(segment, language="en", beam_size=3)
            new_text = " ".join([seg.text.strip() for seg in segments if seg.text.strip()])

            # Gabungkan dengan teks sebelumnya (hilangkan duplikat)
            if new_text:
                combined = last_text.strip()
                if combined:
                    # cek kata overlap terakhir
                    overlap_words = min(len(combined.split()), len(new_text.split()))
                    for i in range(overlap_words, 0, -1):
                        if combined.split()[-i:] == new_text.split()[:i]:
                            combined += " " + " ".join(new_text.split()[i:])
                            break
                    else:
                        combined += " " + new_text
                else:
                    combined = new_text

                print("🗣️", combined)
                last_text = combined

# Start thread
threading.Thread(target=transcribe_stream, daemon=True).start()

# Start mic stream
with sd.InputStream(samplerate=16000, channels=1, callback=callback):
    print("🎙️ Listening (Ctrl+C to stop)...")
    while True:
        pass
