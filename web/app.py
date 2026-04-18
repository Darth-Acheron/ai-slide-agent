import os
import requests
import json
import base64
import uuid
import re
from flask import Flask, render_template, request, jsonify, send_from_directory, Response

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
API_BASE = "http://localhost:11211/api/openai/v1"
TEXT_MODEL = "gemini-3.1-pro-preview:latest"
IMAGE_MODEL = "gemini-3.1-flash-image-preview:latest"

os.makedirs(os.path.join(app.static_folder, "images"), exist_ok=True)

SYSTEM_PROMPT = """You are an expert presentation designer. Create/modify a slide deck based on the user's prompt.
Output ONLY the raw Markdown content. Separate each slide with a horizontal rule (---) surrounded by empty lines.
Do NOT include any markdown code block formatting (like ```markdown), just return the pure text.

CRITICAL FEATURES you MUST use:
1. **Background Images**: To add a generated background, include exactly `<!-- bg: [highly descriptive image prompt] -->` anywhere on the slide.
2. **Inline Illustrations**: To add a generated image inside the slide, use exactly `![[highly descriptive image prompt]](auto)`.
3. **Layout Structure**: Use HTML flexbox for multi-column layouts. Example:
<div style="display: flex; gap: 20px; align-items: center;">
  <div style="flex: 1;">
    - Left text point 1
    - Left text point 2
  </div>
  <div style="flex: 1;">
    ![[cinematic prompt for right side image]](auto)
  </div>
</div>

Ensure all image prompts (both bg and inline) are highly descriptive, cinematic, and optimized for an AI image generator."""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate_slides', methods=['POST'])
def generate_slides():
    user_prompt = request.json.get("prompt", "")
    try:
        resp = requests.post(f"{API_BASE}/chat/completions", json={
            "model": TEXT_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ]
        }, timeout=180)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        text = re.sub(r'^\s*```(?:markdown)?\s*\n?', '', text)
        text = re.sub(r'\n?\s*```\s*$', '', text)
        return jsonify({"markdown": text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/modify_slides', methods=['POST'])
def modify_slides():
    current_md = request.json.get("current_markdown", "")
    user_prompt = request.json.get("prompt", "")
    try:
        resp = requests.post(f"{API_BASE}/chat/completions", json={
            "model": TEXT_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT + "\nPreserve existing image tags and layouts unless asked to change them."},
                {"role": "user", "content": f"Existing Markdown:\n\n{current_md}\n\nModification Request: {user_prompt}"}
            ]
        }, timeout=180)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]
        text = re.sub(r'^\s*```(?:markdown)?\s*\n?', '', text)
        text = re.sub(r'\n?\s*```\s*$', '', text)
        return jsonify({"markdown": text.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_image', methods=['POST'])
def generate_image():
    image_prompt = request.json.get("prompt", "")
    print(f"Generating image with prompt: {image_prompt}")
    try:
        img_resp = requests.post(f"{API_BASE}/images/generations", json={
            "model": IMAGE_MODEL,
            "prompt": image_prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "b64_json"
        }, timeout=300)
        img_resp.raise_for_status()
        
        b64_img = img_resp.json()['data'][0]['b64_json']
        filename = f"{uuid.uuid4().hex[:8]}.png"
        os.makedirs(os.path.join(app.static_folder, "images"), exist_ok=True)
        filepath = os.path.join(app.static_folder, "images", filename)
        with open(filepath, "wb") as fh:
            fh.write(base64.b64decode(b64_img))
            
        return jsonify({"image_url": f"/static/images/{filename}"})
    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/play', methods=['POST'])
def play():
    md = request.form.get('markdown', '').replace('\r\n', '\n')
    return render_template('play.html', markdown=md)

@app.route('/export', methods=['POST'])
def export():
    md = request.form.get('markdown', '').replace('\r\n', '\n')
    
    # Bundle local images into base64 to make HTML file completely standalone
    def replace_img(match):
        url = match.group(1)
        if url.startswith('/static/images/'):
            filename = url.replace('/static/images/', '')
            filepath = os.path.join(app.static_folder, "images", filename)
            filepath = os.path.realpath(filepath)
            expected_dir = os.path.realpath(os.path.join(app.static_folder, "images"))
            if not filepath.startswith(expected_dir):
                return url
            if os.path.exists(filepath):
                with open(filepath, "rb") as img_f:
                    b64 = base64.b64encode(img_f.read()).decode('utf-8')
                    return f"data:image/png;base64,{b64}"
        return url
        
    md_b64 = re.sub(r'(/static/images/[^\s\)"\']+)', replace_img, md)
    md_escaped = md_b64.replace('</textarea>', '&lt;/textarea&gt;')
    html_content = "\n" + md_escaped + "\n"
    
    html = f'''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Exported Presentation</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/reveal.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/theme/black.min.css">
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <section data-markdown>
        <script type="text/template">
{md_escaped}
        </script>
      </section>
    </div>
  </div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/reveal.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/plugin/markdown/markdown.min.js"></script>
  <script>Reveal.initialize({{ hash: true, plugins: [ RevealMarkdown ] }});</script>
</body>
</html>'''
    
    return Response(
        html,
        mimetype="text/html",
        headers={"Content-disposition": "attachment; filename=presentation.html"}
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)