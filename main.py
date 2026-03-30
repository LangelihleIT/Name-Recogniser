import os
import json
import queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

print("--- LOG: Script Starting ---")

# Check model folder
if os.path.exists("model"):
    print("--- LOG: Model folder found! ---")
else:
    print("--- LOG: ERROR - Model folder NOT found!")
    exit(1)

# 1. Load the Model
model = Model("model")
rec = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()

# 2. The "Zulu Hack" - phonetic variants of the name
target_variants = ["langelihle", "langelile", "lungelihle", "longe-lee-leh"]
counter = 0

def callback(indata, frames, time, status):
    if status:
        print(f"⚠️ Stream status: {status}")
    audio_queue.put(bytes(indata))

print("DEBUG: Attempting to open Microphone...")

# 3. Keep the while loop INSIDE the with block so the stream stays open
with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== WHO GETS CALLED THE MOST — LIVE COUNTER ===")
    print(f"Listening for: {target_variants[0].upper()}")
    print("Press Ctrl+C to stop.")
    print("================================================\n")

    try:
        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")

                if text:
                    print(f"Heard: {text}")  # 👈 helpful for debugging

                if any(variant in text for variant in target_variants):
                    counter += 1
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print(f"✅ MATCH DETECTED!")
                    print(f"Heard: \"{text}\"")
                    print(f"Total Count: {counter}")
                    print("\nListening...")

    except KeyboardInterrupt:
        print(f"\n\nStopped. Final count: {counter}")