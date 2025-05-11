from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
import json
import os
from fuzzywuzzy import process

# === Load the STG JSON ===
stg_file = os.path.join(os.path.dirname(__file__), "structured_stg_all_diseases.json")

if not os.path.exists(stg_file):
    raise FileNotFoundError(f"{stg_file} not found in project directory")

with open(stg_file, encoding="utf-8") as f:
    stg_data = json.load(f)

# === Prepare searchable list ===
condition_names = [entry["condition"] for entry in stg_data]

# === FastAPI app ===
app = FastAPI()

# === Fuzzy search function ===
def search_condition(query: str):
    match, score = process.extractOne(query, condition_names)
    for entry in stg_data:
        if entry["condition"] == match:
            return entry
    return None

# === WhatsApp endpoint (Twilio-compatible) ===
@app.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    To: str = Form(...)
):
    query = Body.strip()
    match = search_condition(query)

    if not match:
        return PlainTextResponse("❌ Disease not found. Please try again with a more specific name.")

    response = f"📘 *{match['condition']}* (Code: {match['section_code']})\n\n"
    if match['investigations']:
        response += "🧪 *Investigations:*\n" + "\n".join(f"- {item}" for item in match['investigations']) + "\n\n"
    if match['treatment']:
        response += "💊 *Treatment:*\n" + "\n".join(f"- {item}" for item in match['treatment']) + "\n"

    return PlainTextResponse(response)
