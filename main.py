from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import traceback

app = Flask(__name__)
CORS(app)

# WARNING: Hardcoding API keys is insecure! Use env vars in production.
OPENROUTER_API_KEY = "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"

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
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
        print("🔍 OpenRouter Response Code:", resp.status_code)
        print("🔍 OpenRouter Response Body:", resp.text)
        resp.raise_for_status()
        script = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("❌ ERROR calling OpenRouter:", str(e))
        traceback.print_exc()
        return jsonify({"error": f"Script generation failed: {str(e)}"}), 500

    print("✅ Script generated successfully")
    return jsonify({"script": script})

@app.route("/test")
def test():
    return jsonify({"message": "API is working"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
