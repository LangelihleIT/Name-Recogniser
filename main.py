import time
import os
import json
import queue
import difflib
import sounddevice as sd
from vosk import Model, KaldiRecognizer

print("--- LOG: Script Starting ---")

if not os.path.exists("model"):
    print("ERROR: model folder not found!")
    exit(1)

print("--- LOG: Model folder found! ---")

# 1. Load model
model = Model("model")
rec = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()

#1.1 HEARTBEAT: IN CASES OF NO OUTPUT

# Add this counter before the while loop
chunks_received = 0

while True:
    data = audio_queue.get()
    chunks_received += 1

    # Heartbeat — prints every ~2 seconds (16000 rate / 8000 blocksize = 2 chunks/sec)
    if chunks_received % 16 == 0:
        print(f"[mic alive — chunks: {chunks_received}]", end="\r")

    if rec.AcceptWaveform(data):
        result = json.loads(rec.Result())
        text = result.get("text", "")

        if text:
            matched = is_match(text)
            print(f"Heard: {text}  {'✅' if matched else ''}")
            if matched:
                counter += 1
                print(f">>> MATCH! Total count: {counter}\n")
                
                
# 2. All known variants — from live testing + voice note analysis
target_variants = [
    "langelihle", "langelile", "lungelihle",
    "like a leisure", "like a leaky", "langley lisa",
    "black gay leisure", "langer lazy", "like a leisurely",
    "line get lisa", "longer nisha", "london is him",
    "last day use it", "lie gay new shit", "like to me sir",
    "like any shit", "the and gay leisure", "like a it",
    "black gay lately", "like a leaky", "priscilla his",
    "a line galaxy", "langley leisure", "lang a leash", "lang alicia", "lang illusion",
    "langley here", "lanky leisure", "lang lisa", "langley get lisa"]

TARGET_NAME = "langelihle"
counter = 0

def is_match(heard_text):
    heard = heard_text.lower().strip()
    words = heard.split()
    
    #Check 1: Direct Varient Match
    if any(variant in heard for variant in target_variants):
        return True
    
    
    #Check 2: Two-part pattern match -- lang-stem + ihle-stem
    lang_stems = ["lang", "langley", "langer", "longer", "lanky", "languid", "lankan","like", "language", "lung a"]
    ihle_stems = ["leash", "leisure", "leaky", "lazy", "leaking", "lesion",
                  "deletion", "illusion", "elicit", "elation", "unleash",
                  "alicia", "lisa", "leave", "listen", "nation"]
    
    has_lang = any(any(w.startswith(stem) or stem in w for stem in lang_stems) for w in words)
    has_ihle = any(any(stem in w for stem in ihle_stems) for w in words)
    

    def checking():
        if text:
            matched = is_match(text)
            print(f"Heard: {text}  {'✅' if matched else ''}")

        if matched:
            counter += 1
            print(f">>> MATCH! Total count: {counter}\n")
    
    name_detected = checking()
    
    if has_lang and has_ihle:
        return True
    
    #Check 3: Word-by-word fuzzy match
    for word in words:
        score = difflib.SequenceMatcher(None, word, TARGET_NAME).ratio()
        if score >= 0.45:
            return name_detected
        
    score = difflib.SequenceMatcher(None, heard, TARGET_NAME).ratio()
    if score >= 0.40:
        return name_detected
    
    return False
    
def callback(indata, frames, time, status):
    if status:
        print(f"⚠️ {status}")
    audio_queue.put(bytes(indata))

print("DEBUG: Opening microphone...")

with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1, callback=callback):

    os.system('cls')
    print("=== WHO GETS CALLED THE MOST — LIVE COUNTER ===")
    print(f"Listening for: {TARGET_NAME.upper()}")
    print("Press Ctrl+C to stop.")
    print("================================================\n")

    try:
        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")

                if text:
                    matched = is_match(text)
                    print(f"Heard: {text}  {'✅' if matched else ''}")

                    if matched:
                        counter += 1
                        print(f">>> MATCH! Total count: {counter}\n")

    except KeyboardInterrupt:
        print(f"\nStopped. Final count: {counter}")
