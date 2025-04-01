from flask import Flask, request, jsonify
import fitz  # PyMuPDF
import spacy
import os

app = Flask(__name__)

try:
    nlp = spacy.load("en_core_web_sm")
except:
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

def extract_text_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def generate_recommendation_template(text, section="intro"):
    doc = nlp(text)
    keywords = [ent.text for ent in doc.ents if ent.label_ in ["PERSON", "ORG", "WORK_OF_ART", "EVENT"]]

    if section == "intro":
        return f"I am pleased to recommend {keywords[0] if keywords else 'the applicant'} for the Global Talent Visa. As a professional at {keywords[1] if len(keywords) > 1 else 'your institution'}, I have worked with them for several years, and witnessed their exceptional dedication to [your field]..."
    elif section == "body":
        return f"{keywords[0] if keywords else 'The applicant'} has demonstrated outstanding impact through projects such as {keywords[2] if len(keywords) > 2 else '[key projects]'}. Their leadership in international platforms like {keywords[1] if len(keywords) > 1 else '[organization]'} has made a significant mark in the global [field] community..."
    elif section == "conclusion":
        return f"I highly endorse {keywords[0] if keywords else 'this application'} for the Global Talent Visa. Their continued excellence and contribution to the creative sector will greatly benefit the UK and beyond."
    else:
        return "Section not recognized."

@app.route("/upload", methods=["POST"])
def upload_file():
    section = request.form.get("section")
    file = request.files["file"]
    file_path = f"/tmp/{file.filename}"
    file.save(file_path)

    try:
        text = extract_text_from_pdf(file_path)
        template = generate_recommendation_template(text, section)
        return jsonify({"template": template})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
