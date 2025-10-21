import speech_recognition as sr
from deep_translator import GoogleTranslator
from langdetect import detect
import pyaudio
import wave
import threading
import queue
import time
import os
import numpy as np

# Configuration
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
MAX_CHUNK_DURATION = 1.5
OVERLAP_DURATION = 0.5
SILENCE_THRESHOLD = 1.0
MAX_QUEUE_SIZE = 10

# Ensure output directory exists
os.makedirs("output", exist_ok=True)

# Generate unique filenames with timestamp
TIMESTAMP = time.strftime("%Y-%m-%d_%H-%M-%S")
TRANSCRIPT_FILE = f"output/transcript_{TIMESTAMP}.txt"
CONVERSATION_FILE = f"output/conversation_{TIMESTAMP}.txt"

# Initialize components
recognizer = sr.Recognizer()
recognizer.energy_threshold = 200
recognizer.dynamic_energy_threshold = True
translator = GoogleTranslator(source='auto', target='en')
audio_queue = queue.Queue(maxsize=MAX_QUEUE_SIZE)
stop_event = threading.Event()
last_transcription = ""
recent_transcriptions = []

def save_to_files(original, language, translation):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(TRANSCRIPT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] Original ({language}): {original}\n")
        f.write(f"[{timestamp}] Translation: {translation}\n\n")
    with open(CONVERSATION_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] Caption: {original}\n")
        f.write(f"[{timestamp}] Detected Language: {language}\n")
        f.write(f"[{timestamp}] Translation: {translation}\n\n")
    print(f"Saved to {TRANSCRIPT_FILE} and {CONVERSATION_FILE}")

def detect_language(text):
    try:
        return detect(text)
    except:
        return 'en'

def normalize_text(text):
    return text.lower().strip()

def process_audio():
    global last_transcription, recent_transcriptions
    while not stop_event.is_set():
        try:
            audio_data = audio_queue.get(timeout=0.1)
            if not audio_data:
                continue

            with wave.open("temp.wav", 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(audio_data)

            with sr.AudioFile("temp.wav") as source:
                audio = recognizer.record(source)
                try:
                    start_time = time.time()
                    text = recognizer.recognize_google(audio, language='auto')
                    recognition_time = time.time() - start_time

                    normalized_text = normalize_text(text)
                    if normalized_text == normalize_text(last_transcription):
                        continue
                    last_transcription = text

                    recent_transcriptions.append(text)
                    if len(recent_transcriptions) > 2:
                        recent_transcriptions.pop(0)

                    combined_text = " ".join(recent_transcriptions)
                    lang = detect_language(combined_text)
                    lang_name = 'Arabic' if lang == 'ar' else 'English'

                    start_time = time.time()
                    if lang == 'ar':
                        translated = translator.translate(combined_text, source='ar', target='en')
                    else:
                        translated = GoogleTranslator(source='en', target='ar').translate(combined_text)
                    translation_time = time.time() - start_time

                    print(f"\nCaption: {combined_text}")
                    print(f"Detected Language: {lang_name}")
                    print(f"Translation: {translated}")
                    print(f"[Recognition: {recognition_time:.2f}s, Translation: {translation_time:.2f}s]")
                    save_to_files(combined_text, lang_name, translated)

                except sr.UnknownValueError:
                    print("[Skipped unclear audio]", end='', flush=True)
                except sr.RequestError as e:
                    print(f"Recognition error: {e}", end='', flush=True)
                except Exception as e:
                    print(f"Error processing audio: {e}", end='', flush=True)

        except queue.Empty:
            continue

def stream_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    print("🎙️ Listening for speech... (Speak now)")
    audio_buffer = b''
    overlap_buffer = b''
    chunk_start_time = time.time()
    last_speech_time = time.time()
    speech_detected = False

    while not stop_event.is_set():
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_buffer += data

            audio_array = np.frombuffer(data, dtype=np.int16)
            energy = np.sqrt(np.mean(audio_array**2))

            if energy > recognizer.energy_threshold:
                speech_detected = True
                last_speech_time = time.time()
            else:
                if speech_detected and (time.time() - last_speech_time >= SILENCE_THRESHOLD):
                    if audio_buffer:
                        chunk_to_process = overlap_buffer + audio_buffer
                        try:
                            audio_queue.put(chunk_to_process, block=False)
                        except queue.Full:
                            print("[Queue full, audio dropped]", end='', flush=True)
                        overlap_samples = int(OVERLAP_DURATION * RATE * 2)
                        overlap_buffer = audio_buffer[-overlap_samples:] if len(audio_buffer) > overlap_samples else audio_buffer
                        audio_buffer = b''
                        chunk_start_time = time.time()
                        speech_detected = False

            if time.time() - chunk_start_time >= MAX_CHUNK_DURATION:
                if audio_buffer:
                    chunk_to_process = overlap_buffer + audio_buffer
                    try:
                        audio_queue.put(chunk_to_process, block=False)
                    except queue.Full:
                        print("[Queue full, audio dropped]", end='', flush=True)
                    overlap_samples = int(OVERLAP_DURATION * RATE * 2)
                    overlap_buffer = audio_buffer[-overlap_samples:] if len(audio_buffer) > overlap_samples else audio_buffer
                    audio_buffer = b''
                    chunk_start_time = time.time()
                    speech_detected = False

        except Exception as e:
            print(f"Error capturing audio: {e}")
            break

    if audio_buffer or overlap_buffer:
        try:
            audio_queue.put(overlap_buffer + audio_buffer, block=False)
        except queue.Full:
            pass

    stream.stop_stream()
    stream.close()
    p.terminate()

def main():
    print("🧠 Starting Real-Time Caption & Translation System...")
    print(f"Logging to {TRANSCRIPT_FILE} and {CONVERSATION_FILE}")

    audio_thread = threading.Thread(target=stream_audio)
    process_thread = threading.Thread(target=process_audio)

    audio_thread.start()
    process_thread.start()

    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping caption system...")
        stop_event.set()

    audio_thread.join()
    process_thread.join()
    print(f"✅ System stopped. Results saved in 'output/' folder.")

if __name__ == "__main__":
    main()
