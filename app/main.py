# stg_chatbot_fastapi.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
import json
import uvicorn
from typing import Optional
from fuzzywuzzy import process
import os

# Load STG data from JSON
stg_file = "structured_stg_all_diseases.json"
if not os.path.exists(stg_file):
    raise FileNotFoundError(f"{stg_file} not found in project directory")

with open(stg_file, encoding="utf-8") as f:
    stg_data = json.load(f)

# Prepare list of condition names for fuzzy search
condition_names = [entry["condition"] for entry in stg_data]

# FastAPI app
app = FastAPI()

# Fuzzy match helper
def search_condition(query: str) -> Optional[dict]:
    match, score = process.extractOne(query, condition_names)
    for entry in stg_data:
        if entry["condition"] == match:
            return entry
    return None

# WhatsApp Twilio webhook route
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

# Run server locally
if __name__ == "__main__":
    pass
    # uvicorn.run("stg_chatbot_fastapi:app", host="0.0.0.0", port=8000, reload=True)
