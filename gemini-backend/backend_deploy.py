from flask import Flask, request, jsonify
import google.generativeai as genai
import os
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
CORS(app)  # 👈 This allows all domains (including Netlify) to access the API


# === CONFIGURE GEMINI ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Use environment variable
genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.0-flash")

# === GET DIET PLAN FROM GEMINI ===
def get_diet_plan(symptom_text):
    prompt = f"""
    I am building a diet assistant chatbot. The user has reported the following symptom(s): "{symptom_text}".
    Based on these symptoms, suggest a simple, healthy, and practical daily diet plan.
    Keep it clear, concise, and beginner-friendly.
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

    response = get_diet_plan(symptoms)
    return jsonify({"reply": response})

@app.route("/", methods=["GET"])
def home():
    return "✅ Gemini Diet API is running."

# === RUN APP ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
