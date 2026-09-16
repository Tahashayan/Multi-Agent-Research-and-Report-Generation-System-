import json
import requests
import random

# --- CONFIGURATION ---
OLLAMA_MODEL = "qwen2.5:3b"  # <--- Change this to the model you have downloaded in Ollama!
OLLAMA_URL = "http://localhost:11434/api/chat"
INPUT_FILE = "perfect_chunks.json"
OUTPUT_JSONL = "training_dataset.jsonl"

TRAINING_SYSTEM_PROMPT = """You are an elite financial analyst and technical writer. Your task is to take raw, disorganized data points and write a highly professional, objective, and strictly formatted report section. Maintain a corporate, analytical tone. Do not use conversational filler."""

def reverse_engineer_text(perfect_text: str) -> str:
    """Uses Local Ollama to turn perfect text into messy bullet points."""
    prompt = f"""
    Read the following highly professional corporate text. 
    I want you to extract ONLY the core facts, data points, and names. 
    Output them as a disorganized, messy list of raw bullet points, as if a junior researcher just dumped their raw notes.
    Do NOT write full sentences. Do NOT be eloquent. Just give me the raw data points.
    
    TEXT:
    {perfect_text}
    """
    
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["message"]["content"]
    except Exception as e:
        print(f"⚠️ Ollama Error: {e}")
        return None

def build_dataset():
    print(f"📂 Loading perfect chunks from {INPUT_FILE}...")
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        all_chunks = json.load(f)

    # --- THE FIX: SHINK THE DATASET ---
    # Randomly select 400 chunks so the model gets a diverse mix of topics,
    # without taking a week to generate!
    SAMPLE_SIZE = 400
    if len(all_chunks) > SAMPLE_SIZE:
        chunks = random.sample(all_chunks, SAMPLE_SIZE)
    else:
        chunks = all_chunks

    print(f"🎯 Total chunks to process: {len(chunks)} (Reduced for laptop GPU)")
    
    # Open in 'append' mode
    with open(OUTPUT_JSONL, "a", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            perfect_text = chunk["text"]
            
            print(f"⏳ Processing chunk {i+1}/{len(chunks)} on GPU...")
            
            messy_input = reverse_engineer_text(perfect_text)
            
            if not messy_input:
                print("Skipping due to error...")
                continue
                
            row = {
                "messages": [
                    {"role": "system", "content": TRAINING_SYSTEM_PROMPT},
                    {"role": "user", "content": messy_input},
                    {"role": "assistant", "content": perfect_text}
                ]
            }
            
            f.write(json.dumps(row) + "\n")

    print(f"\n✅ SUCCESS! Dataset generated and saved to {OUTPUT_JSONL}")
    print("🧠 This file is now ready for QLoRA Fine-Tuning.")
    
if __name__ == "__main__":
    build_dataset()