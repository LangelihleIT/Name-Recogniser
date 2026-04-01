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

# ── 1. Load model ────────────────────────────────────────────────────────────
model = Model("model")
rec = KaldiRecognizer(model, 16000)
audio_queue = queue.Queue()

# ── 2. Variants & stems ──────────────────────────────────────────────────────
target_variants = [
    "langelihle", "langelile", "lungelihle",
    "like a leisure", "langley lisa",
    "black gay leisure", "langer lazy", "like a leisurely",
    "line get lisa", "longer nisha", "london is him",
    "last day use it", "lie gay new shit", "like to me sir",
    "like any shit", "the and gay leisure",
    "black gay lately", "priscilla his",
    "a line galaxy", "langley leisure", "lang a leash",
    "lang alicia", "lang illusion", "langley here",
    "lanky leisure", "lang lisa", "langley get lisa",
    # ── Added from Session 6 data ──
    "lang amnesia", "lang initiate", "lang in asia",
    "lang a nasa", "lang initially", "langa lisa",
    "langa leisure", "langa leash", "langa alicia",
]

TARGET_NAME = "langelihle"
counter = 0

# TIGHTENED: removed "like" and "language" — too common in normal speech
lang_stems = [
    "lang", "langley", "langer", "longer", "lanky",
    "languid", "lankan", "lung a", "langa", "lango"
]

ihle_stems = [
    "leash", "leisure", "leaky", "lazy", "leaking", "lesion",
    "deletion", "illusion", "elicit", "elation", "unleash",
    "alicia", "lisa", "leave", "listen", "nation",
    # ── Added from Session 6 data ──
    "amnesia", "initiate", "asia", "nasa", "initially",
    "nice yet", "a loser", "issue", "in asia",
]

# ── 3. Matching logic ────────────────────────────────────────────────────────
def is_match(heard_text):
    heard = heard_text.lower().strip()
    words = heard.split()

    # Check 1: Direct variant match
    if any(variant in heard for variant in target_variants):
        return True

    # Check 2: Two-part stem match (lang-stem + ihle-stem)
    has_lang = any(
        w.startswith(stem) or stem in w
        for stem in lang_stems
        for w in words
    )
    has_ihle = any(
        stem in w
        for stem in ihle_stems
        for w in words
    )
    if has_lang and has_ihle:
        return True

    # Check 3: Adjacent word-pair fuzzy match (NEW — fixes single-word misses)
    # e.g. "lang" + "deletion" joined → compared against "langelihle"
    pairs = [words[i] + words[i + 1] for i in range(len(words) - 1)]
    for pair in pairs:
        score = difflib.SequenceMatcher(None, pair, TARGET_NAME).ratio()
        if score >= 0.55:
            return True

    # Check 4: Individual word fuzzy (kept, but threshold raised slightly)
    for word in words:
        score = difflib.SequenceMatcher(None, word, TARGET_NAME).ratio()
        if score >= 0.50:
            return True

    # Check 5: Full phrase fuzzy
    score = difflib.SequenceMatcher(None, heard, TARGET_NAME).ratio()
    if score >= 0.40:
        return True

    return False

# ── 4. Mic callback ──────────────────────────────────────────────────────────
def callback(indata, frames, time, status):
    if status:
        print(f"⚠️  {status}")
    audio_queue.put(bytes(indata))

# ── 5. Main loop ─────────────────────────────────────────────────────────────
print("DEBUG: Opening microphone...")

with sd.RawInputStream(
    samplerate=16000,
    blocksize=8000,
    dtype='int16',
    channels=1,
    callback=callback
):
    print("\n=== WHO GETS CALLED THE MOST — LIVE COUNTER ===")
    print(f"Listening for: {TARGET_NAME.upper()}")
    print("Press Ctrl+C to stop.")
    print("================================================\n")

    chunks_received = 0

    try:
        while True:
            data = audio_queue.get()
            chunks_received += 1

            # Heartbeat — every ~8 seconds of audio
            if chunks_received % 16 == 0:
                print(f"[mic alive — chunks: {chunks_received}]", end="\r")

            # ── Final result path ──
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    matched = is_match(text)
                    status_icon = "✅" if matched else ""
                    print(f"Heard: {text}  {status_icon}")
                    if matched:
                        counter += 1
                        print(f">>> MATCH! Total count: {counter}\n")

            # ── Partial result path (NEW — catches name mid-utterance) ──
            else:
                partial = json.loads(rec.PartialResult())
                partial_text = partial.get("partial", "")
                if partial_text and is_match(partial_text):
                    print(f"[Partial match]: {partial_text}")

    except KeyboardInterrupt:
        print(f"\nStopped. Final count: {counter}")
        print(f"Total audio chunks processed: {chunks_received}")
