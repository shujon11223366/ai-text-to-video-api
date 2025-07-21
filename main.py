from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback

app = Flask(__name__)
CORS(app)

OPENAI_API_KEY = "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"

@app.route("/")
def home():
    return "AI Text to Video API is running."

@app.route("/generate", methods=["POST"])
def generate():
    print("🛠️ /generate route called")

    data = request.get_json()
    prompt = data.get("prompt") if data else None
    print("📩 Received prompt:", prompt)

    if not prompt:
        print("❌ No prompt provided!")
        return jsonify({"error": "No prompt provided"}), 400

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
        print("🔍 OpenAI Response Code:", resp.status_code)
        print("🔍 OpenAI Response Body:", resp.text)
        resp.raise_for_status()
        script = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ ERROR calling OpenAI:", str(e))
        traceback.print_exc()
        return jsonify({"error": f"Script generation failed: {str(e)}"}), 500

    print("✅ Script generated successfully")
    return jsonify({"script": script})

@app.route("/test")
def test():
    return jsonify({"message": "API is working"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
