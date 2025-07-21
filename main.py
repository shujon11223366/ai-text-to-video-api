from flask import Flask, request, send_file
from gtts import gTTS
import uuid
import os
import requests

app = Flask(__name__)
OPENROUTER_API_KEY = "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"

@app.route("/")
def home():
    return "✅ AI Text-to-Video API is live on Render!"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt")

    # Generate script
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=body)
    script = resp.json()["choices"][0]["message"]["content"]

    # Generate speech
    audio_file = f"{uuid.uuid4().hex}.mp3"
    tts = gTTS(script)
    tts.save(audio_file)

    # Return file
    return send_file(audio_file, as_attachment=True)
    import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

