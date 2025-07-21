from flask import Flask, request, send_file
from flask_cors import CORS
from gtts import gTTS
import uuid
import os
import requests

app = Flask(__name__)
CORS(app)  # ✅ This line allows Blogger to access your API

OPENROUTER_API_KEY = os.environ.get("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")

# Google Drive direct download link for your background video
BACKGROUND_VIDEO_URL = "https://drive.google.com/uc?id=1THOvJdc0rnL56mxeKCCVq5lIl6Nrun6K"

def download_background_video():
    video_path = "background.mp4"
    if not os.path.exists(video_path):
        print("Downloading background video...")
        r = requests.get(BACKGROUND_VIDEO_URL, stream=True)
        with open(video_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return video_path

@app.route("/")
def home():
    return "✅ AI Text-to-Video API with subtitles is live!"

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    prompt = data.get("prompt", "")
    if not prompt:
        return {"error": "Prompt is required"}, 400

    # 1. Generate script using OpenRouter
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
        return {"error": f"Script generation failed: {str(e)}"}, 500

    # 2. Text to speech (gTTS)
    audio_filename = f"{uuid.uuid4().hex}.mp3"
    tts = gTTS(text=script)
    tts.save(audio_filename)

    # 3. Generate subtitle (.srt)
    subtitle_filename = f"{uuid.uuid4().hex}.srt"
    with open(subtitle_filename, "w") as f:
        f.write(f"1\n00:00:00,000 --> 00:00:20,000\n{script}")

    # 4. Download background video if missing
    background_video_path = download_background_video()

    # 5. Merge video, audio, subtitles with ffmpeg
    output_filename = f"{uuid.uuid4().hex}_output.mp4"
    ffmpeg_cmd = (
        f"ffmpeg -y -i {background_video_path} -i {audio_filename} "
        f"-vf subtitles={subtitle_filename} -c:v libx264 -c:a aac -shortest {output_filename}"
    )
    os.system(ffmpeg_cmd)

    # 6. Clean up temp audio and subtitle
    os.remove(audio_filename)
    os.remove(subtitle_filename)

    # 7. Return final video file
    return send_file(output_filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
