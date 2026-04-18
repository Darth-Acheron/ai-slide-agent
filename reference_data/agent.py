import requests
import json
import re
import os
import base64

API_URL = "http://localhost:11211/api/openai/v1/images/generations"
MODEL = "imagen-4.0-generate-001:latest"
WORKSPACE = os.path.expanduser("~/projects/markdown-to-slides")

def generate_image(prompt, index):
    print(f"[{index}] Generating image for prompt: '{prompt}'...")
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024",
        "response_format": "b64_json"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        response.raise_for_status()
        
        res_json = response.json()
        b64_img = res_json['data'][0]['b64_json']
        
        filename = f"slide_{index}_bg.png"
        filepath = os.path.join(WORKSPACE, filename)
        
        with open(filepath, "wb") as fh:
            fh.write(base64.b64decode(b64_img))
        
        print(f"[{index}] Successfully saved image to {filename}")
        return filename
    except Exception as e:
        print(f"[{index}] Failed to generate image: {e}")
        return None

def main():
    md_path = os.path.join(WORKSPACE, "presentation.md")
    html_path = os.path.join(WORKSPACE, "index.html")
    
    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    slides = re.split(r'\n---\n', content)
    
    html_sections = []
    
    for i, slide_text in enumerate(slides):
        slide_text = slide_text.strip()
        if not slide_text:
            continue
            
        note_match = re.search(r'<!--\s*note:\s*(.*?)\s*-->', slide_text, re.IGNORECASE | re.DOTALL)
        
        bg_attr = ""
        if note_match:
            prompt = note_match.group(1).strip()
            slide_text = re.sub(r'<!--\s*note:\s*.*?\s*-->', '', slide_text, flags=re.IGNORECASE | re.DOTALL).strip()
            
            img_file = generate_image(prompt, i + 1)
            if img_file:
                bg_attr = f' data-background-image="{img_file}" data-background-opacity="0.3"'
        
        section = f"""      <section{bg_attr} data-markdown>
        <textarea data-template>
{slide_text}
        </textarea>
      </section>"""
        html_sections.append(section)
        
    with open(html_path, "r", encoding="utf-8") as f:
        html_template = f.read()
        
    # we need to be careful not to keep adding them. Let's just create a fresh template
    fresh_template = '''<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Agent Generated Slides</title>
  <link rel="stylesheet" href="node_modules/reveal.js/dist/reset.css">
  <link rel="stylesheet" href="node_modules/reveal.js/dist/reveal.css">
  <link rel="stylesheet" href="node_modules/reveal.js/dist/theme/black.css">
  <link rel="stylesheet" href="node_modules/reveal.js/dist/plugin/highlight/monokai.css">
</head>
<body>
  <div class="reveal">
    <div class="slides">
      <!-- SLIDES_GO_HERE -->
    </div>
  </div>
  <script src="node_modules/reveal.js/dist/reveal.js"></script>
  <script src="node_modules/reveal.js/dist/plugin/notes.js"></script>
  <script src="node_modules/reveal.js/dist/plugin/markdown.js"></script>
  <script src="node_modules/reveal.js/dist/plugin/highlight.js"></script>
  <script>
    Reveal.initialize({
      hash: true,
      plugins: [ RevealMarkdown, RevealHighlight, RevealNotes ]
    });
  </script>
</body>
</html>'''

    new_slides_html = "\n".join(html_sections)
    html_out = fresh_template.replace("<!-- SLIDES_GO_HERE -->", new_slides_html)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_out)
        
    print(f"\nDone! Successfully updated {html_path}. You can now open it in your browser.")

if __name__ == "__main__":
    main()