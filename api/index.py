import base64
import time
import json
import requests
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)

API_URL = "http://ver3.yacinelive.com"
KEY = "c!xZj+N9&G@Ev@vw"

def decrypt(enc, key):
    enc = base64.b64decode(enc.encode("ascii")).decode("ascii")
    result = ""
    for i in range(len(enc)):
        result += chr(ord(enc[i]) ^ ord(key[i % len(key)]))
    return result

def req(path):
    r = requests.get(API_URL + path)
    timestamp = r.headers.get("t", str(int(time.time())))
    try:
        data = json.loads(decrypt(r.text, key=KEY + timestamp))
        return data
    except Exception:
        return None

@app.route("/api/categories")
def get_categories():
    data = req("/api/categories")
    return jsonify(data)

@app.route("/api/categories/<int:category_id>/channels")
def get_category_channels(category_id):
    data = req(f"/api/categories/{category_id}/channels")
    return jsonify(data)

@app.route("/api/channel/<int:channel_id>")
def get_channel(channel_id):
    data = req(f"/api/channel/{channel_id}")
    return jsonify(data)

# === إضافة endpoint proxy لروابط m3u8 ===
@app.route("/live/<int:channel_id>.m3u8")
def proxy_m3u8(channel_id):
    data = req(f"/api/channel/{channel_id}")
    if data and "stream_url" in data:
        # إعادة توجيه مباشرة إلى رابط البث الحقيقي
        return redirect(data["stream_url"])
    else:
        return jsonify({"error": "Channel not found or cannot get stream URL"}), 404
