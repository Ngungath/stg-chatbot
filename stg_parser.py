import fitz  # PyMuPDF
import re
import json

pdf_path = "stg_guidelines.pdf"
def extract_diseases_from_pdf(pdf_path, output_json_path):
    # Load the PDF file
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    # Regex to match section codes like 5.2.1 or 13.5.2 etc.
    pattern = re.compile(r'\n(\d{1,2}(?:\.\d+){1,2})\s+(.*?)\n(.*?)(?=\n\d{1,2}(?:\.\d+){1,2}\s+)', re.DOTALL)
    matches = pattern.findall(full_text)

    # Structure entries
    results = []
    for code, title, content in matches:
        definition = ""
        investigations = []
        treatment = []

        # Attempt to find definition/description
        desc_match = re.search(r'(Definition|Description|Overview):\s*(.*?)(\n[A-Z][a-z]+:|\nInvestigations?:|\nTreatment:)', content, re.DOTALL)
        if desc_match:
            definition = desc_match.group(2).strip()

        # Investigations
        inv_match = re.search(r'Investigations?:\s*(.*?)(\n[A-Z][a-z]+:|\nTreatment:|\nManagement:)', content, re.DOTALL)
        if inv_match:
            investigations = [line.strip() for line in inv_match.group(1).split('\n') if line.strip()]

        # Treatment or Management
        treat_match = re.search(r'(Treatment|Management):\s*(.*?)(\n[A-Z][a-z]+:|\Z)', content, re.DOTALL)
        if treat_match:
            treatment = [line.strip() for line in treat_match.group(2).split('\n') if line.strip()]

        results.append({
            "section_code": code.strip(),
            "condition": title.strip(),
            "definition": definition,
            "investigations": investigations,
            "treatment": treatment
        })

    # Save to JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted {len(results)} disease entries to: {output_json_path}")

# === RUN SCRIPT ===
pdf_input = "stg_guidelines.pdf"  # Replace with your STG file path
json_output = "structured_stg_all_diseases.json"
extract_diseases_from_pdf(pdf_input, json_output)
