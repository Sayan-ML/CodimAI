from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from flask_cors import CORS
from dotenv import load_dotenv
import re

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allows all domains (including Netlify) to access the API

# === CONFIGURE GEMINI ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# === Relevant keyword list (symptoms / medical context) ===
MEDICAL_KEYWORDS = [
    # General symptoms
    "pain", "headache", "nausea", "vomiting", "fever", "cough", "cold",
    "fatigue", "dizziness", "sore throat", "body ache", "bloating", "indigestion",
    "diarrhea", "constipation", "acidity", "heartburn", "loss of appetite",
    "shortness of breath", "difficulty breathing", "sweating", "palpitations",
    "swelling", "weakness", "cramps", "inflammation", "burning sensation",
    
    # Chronic diseases
    "diabetes", "hypertension", "high blood pressure", "low blood pressure",
    "cholesterol", "obesity", "asthma", "thyroid", "hypothyroidism", "hyperthyroidism",
    "anemia", "pcos", "pcod", "arthritis", "osteoporosis", "migraine", "epilepsy",
    "eczema", "psoriasis", "ulcer", "gastritis", "gerd", "ibs", "irritable bowel",
    "colitis", "gout", "liver disease", "hepatitis", "kidney stones",
    
    # Metabolic & hormonal
    "insulin", "hormonal imbalance", "metabolic syndrome", "cortisol", "testosterone",
    "estrogen", "menopause", "thyroxine", "androgen", "progesterone",

    # Organ-specific
    "stomach", "liver", "kidney", "pancreas", "lungs", "skin", "gut", "intestine",
    "colon", "gallbladder", "prostate", "heart",

    # Women's health
    "period", "menstrual", "menstruation", "irregular periods", "pcos", "pcod",
    "menopause", "pregnancy", "fertility", "fibroids", "endometriosis",

    # Nutritional conditions
    "malnutrition", "vitamin d deficiency", "calcium deficiency", "iron deficiency",
    "protein deficiency", "b12 deficiency", "overweight", "underweight",

    # Infections
    "infection", "viral", "bacterial", "fungal", "flu", "covid", "allergy",
    "sinusitis", "bronchitis", "urinary tract infection", "uti", "cold sore",

    # Lifestyle-related
    "stress", "sleep", "insomnia", "sedentary", "alcohol", "smoking", "junk food",
    "fast food", "lack of exercise"
]


def is_medical_related(text):
    """Basic keyword-based filter for medical relevance."""
    text_lower = text.lower()
    for keyword in MEDICAL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", text_lower):
            return True
    return False

# === GET DIET PLAN FROM GEMINI ===
def get_diet_plan(symptom_text):
    prompt = f"""
    I am building a diet assistant chatbot. The user has reported the following symptom(s): "{symptom_text}".
    Based on these symptoms, suggest a simple, healthy, and practical daily diet plan.
    Keep it clear, concise, and beginner-friendly, just give me the diet plan, don't say unnecessary stuff, and don't give asterisk.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Failed to get response from Gemini: {e}"

# === API ENDPOINT ===
@app.route("/diet", methods=["POST"])
def diet():
    data = request.get_json()
    symptoms = data.get("symptoms", "")
    if not symptoms:
        return jsonify({"reply": "No symptoms provided."}), 400

    if not is_medical_related(symptoms):
        return jsonify({
            "reply": "⚠️ Please tell me about your medical condition or symptoms. I am a medical chatbot trained to provide personalized diet plans."
        })

    response = get_diet_plan(symptoms)
    return jsonify({"reply": response})

@app.route("/", methods=["GET"])
def home():
    return "✅ Gemini Diet API is running."

# === RUN APP ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
