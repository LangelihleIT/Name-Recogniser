# Name Recogniser

A live microphone listener that detects when the name **Langelihle** is spoken, 
and keeps a running count.

---

## How It Works
The script listens frame by frame using Vosk (offline speech recognition) and 
discards audio after each frame — no storage buffer.

When speech is detected, it runs through a 4-layer matching system:
1. **Direct variant match** — known phonetic mishearings hardcoded as variants
2. **Two-part pattern match** — Vosk consistently hears "Langel" as lang-stems 
   (lang, langley, langer) and "ihle" as ihle-stems (leash, leisure, lazy). 
   If both parts appear in the heard text, it's a match.
3. **Word-by-word fuzzy match** — each heard word scored against target name
4. **Full phrase fuzzy match** — entire phrase scored against target name

---

## Key Finding: The "Zulu Split"
Vosk splits the name into two phonetic clusters:
- **"Langel"** → lang / langley / langer / longer / lanky
- **"ihle"**   → leash / leisure / lazy / lesion / deletion / illusion

This two-part pattern is the most reliable detection signal.

---

## Stack
- Python 3.12
- Vosk (offline STT) + vosk-model-small-en-us-0.15
- sounddevice (microphone input)
- difflib (fuzzy matching)

---

## Versions
- **v1** — basic listener, exact string match only
- **v2** — fuzzy matching + two-part pattern matching (lang-stem + ihle-stem)
