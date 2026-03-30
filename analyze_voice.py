import json
import wave
import subprocess
import os
from vosk import Model, KaldiRecognizer

# Step 1: Convert your mp4 to wav using ffmpeg
# Run this in terminal first if you haven't:
# ffmpeg -i Langelihle.mp4 -ar 16000 -ac 1 Langelihle.wav

WAV_FILE = "Langelihle.wav"

if not os.path.exists(WAV_FILE):
    print("Converting mp4 to wav...")
    subprocess.run([
        "ffmpeg", "-i", "Langelihle.mp4",
        "-ar", "16000", "-ac", "1", WAV_FILE
    ])

# Step 2: Run through Vosk and collect all outputs
model = Model("model")
rec = KaldiRecognizer(model, 16000)
rec.SetWords(True)

all_results = []

with wave.open(WAV_FILE, "rb") as wf:
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text = result.get("text", "")
            if text:
                all_results.append(text)
                print(f"Heard: {text}")

# Final partial result
final = json.loads(rec.FinalResult())
if final.get("text"):
    all_results.append(final["text"])
    print(f"Heard: {final['text']}")

print("\n--- ALL VARIANTS DETECTED ---")
for r in all_results:
    print(f'  "{r}"')