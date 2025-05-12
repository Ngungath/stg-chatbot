from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse, JSONResponse
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

# === Load short form map or define default ===
shortform_file = os.path.join(os.path.dirname(__file__), "short_forms.json")
if os.path.exists(shortform_file):
    with open(shortform_file, "r", encoding="utf-8") as f:
        short_forms = json.load(f)
else:
    short_forms = {
        "uti": "urinary tract infection",
        "tb": "tuberculosis",
        "hiv": "hiv and aids",
        "copd": "chronic obstructive pulmonary disease",
        "htn": "hypertension",
        "dm": "diabetes mellitus",
        "pid": "pelvic inflammatory disease",
        "rtis": "reproductive tract infections"
    }

# === FastAPI app ===
app = FastAPI()

# === Swahili translation stub ===
def translate_to_swahili(text: str) -> str:
    return f"[Swahili] {text}"

# === Enhanced search function ===
def search_condition(query: str):
    query = query.strip().lower()

    # Handle short form lookup
    if query in short_forms:
        query = short_forms[query]

    # Try exact match with ICD section code
    for entry in stg_data:
        if query == entry["section_code"].lower():
            return entry

    # Fuzzy match condition names
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
    is_swahili = query.lower().startswith("sw:")

    if is_swahili:
        query = query[3:].strip()

    match = search_condition(query)

    if not match:
        return PlainTextResponse("❌ Disease not found. Please try again with a more specific name, abbreviation, or ICD code.")

    response = f"📘 *{match['condition'].title()}*\n📄 *Code:* {match['section_code']}\n\n"
    if match['definition']:
        response += f"🧾 *Definition:*\n{match['definition']}\n\n"
    if match['investigations']:
        response += "🧪 *Investigations:*\n" + "\n".join(f"🔹 {item}" for item in match['investigations']) + "\n\n"
    if match['treatment']:
        response += "💊 *Treatment:*\n" + "\n".join(f"🔸 {item}" for item in match['treatment']) + "\n"

    if is_swahili:
        response = translate_to_swahili(response)

    return PlainTextResponse(response)

# === API to view/edit short forms ===
@app.get("/shortforms")
async def get_shortforms():
    return JSONResponse(short_forms)

@app.post("/shortforms")
async def update_shortform(key: str = Form(...), value: str = Form(...)):
    short_forms[key.lower()] = value.lower()
    with open(shortform_file, "w", encoding="utf-8") as f:
        json.dump(short_forms, f, indent=2)
    return {"message": f"Updated: {key} -> {value}"}
