import re

with open('web/templates/index.html', 'r') as f:
    content = f.read()

# We need to completely rewrite the script block to avoid the parser errors.
# The issue is primarily with `<!` inside the javascript and `/.../g` regex syntax
# getting mangled by the jinja or html parsers.

script_start = content.find('<script>')
if script_start != -1:
    head = content[:script_start]
else:
    head = content

# Write out the safe script block
safe_script = """<script>
    let timeoutId;
    const editor = document.getElementById('md-editor');
    const previewFrame = document.getElementById('preview-frame');

    updatePreview();

    function debouncePreview() {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(updatePreview, 500);
    }

    function generateSlides() { promptAgent('generate'); }
    function modifySlides() { promptAgent('modify'); }

    function submitForm(action) {
      document.getElementById('hidden-md').value = editor.value;
      const form = document.getElementById('actions-form');
      form.action = action;
      form.submit();
    }

    function updatePreview() {
      const mdContent = editor.value;
      const lt = String.fromCharCode(60);
      const gt = String.fromCharCode(62);
      
      const doc = `
<!DOCTYPE html>
<html>
<head>
  <base href="${window.location.origin}/">
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <base href="${window.location.origin}/">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reset.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/theme/black.min.css" id="theme">
  <style>
    .reveal section img { background: none; border: none; box-shadow: none; max-height: 50vh; }
    .reveal .slides { text-align: left; }
    .reveal h1, .reveal h2, .reveal h3 { text-transform: none; }
  </style>
</head>
<body>
  <div class="reveal">
    <div class="slides">
      ${lt}section data-markdown${gt}
        ${lt}textarea data-template${gt}
${mdContent.replace(/<\\/textarea>/ig, "&lt;/textarea&gt;")}
        ${lt}/textarea${gt}
      ${lt}/section${gt}
    </div>
  </div>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.js"><\\/script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/plugin/markdown/markdown.min.js"><\\/script>
  <script>
    Reveal.initialize({
      plugins: [ RevealMarkdown ],
      slideNumber: true,
      hash: true
    });
  <\\/script>
</body>
</html>`;
      
      const blob = new Blob([doc], { type: 'text/html' });
      previewFrame.src = URL.createObjectURL(blob);
    }

    async function promptAgent(action) {
      const promptText = document.getElementById('prompt-input').value;
      const btn = (action === 'generate') ? document.getElementById('btn-generate') : document.getElementById('btn-modify');
      const originalText = btn.innerHTML;
      
      if(!promptText.trim()) {
        alert("Please enter a prompt.");
        return;
      }

      btn.innerHTML = `<span class="animate-spin inline-block mr-2">⏳</span> Working...`;
      btn.disabled = true;

      try {
        const payload = { prompt: promptText };
        if (action === 'modify') {
            payload.current_markdown = editor.value;
        }

        const res = await fetch('/api/prompt', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        
        if (data.markdown) {
            editor.value = data.markdown;
            updatePreview();
        } else if (data.error) {
            alert("Error: " + data.error);
        }
      } catch (err) {
        alert("Failed to contact agent: " + err);
      } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    }

    async function autoGenerateImages() {
      const btn = document.getElementById('btn-images');
      const originalText = btn.innerHTML;
      btn.innerHTML = `<span class="animate-spin inline-block mr-2">⏳</span> Generating Images... (~130s each)`;
      btn.disabled = true;

      let currentMd = editor.value;
      
      // We use new RegExp to avoid slash parsing issues in the HTML context
      // Background regex: <!-- bg: (prompt) -->
      const bgRegex = new RegExp('<'+'!--\\s*bg:\\s*(.*?)\\s*--'+'>', 'g');
      // Inline regex: ![alt](auto)
      const inlineRegex = new RegExp('!\\[(.*?)\\]\\(auto\\)', 'g');

      try {
        // Find backgrounds
        const bgMatches = [...currentMd.matchAll(bgRegex)];
        for (const match of bgMatches) {
          const fullMatch = match[0];
          const prompt = match[1];
          console.log("Generating bg image for:", prompt);
          
          const res = await fetch('/api/generate_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
          });
          const data = await res.json();
          if (data.error) { throw new Error(data.error); }
          if (data.image_url) {
            // Replace with standard markdown image or revealjs data-background-image
            const newTag = `<!-- .slide: data-background-image="${data.image_url}" -->`;
            currentMd = currentMd.replace(fullMatch, newTag);
            editor.value = currentMd;
            updatePreview();
          }
        }

        // Find inline
        const inlineMatches = [...currentMd.matchAll(inlineRegex)];
        for (const match of inlineMatches) {
          const fullMatch = match[0];
          const prompt = match[1];
          console.log("Generating inline image for:", prompt);
          
          const res = await fetch('/api/generate_image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
          });
          const data = await res.json();
          if (data.error) { throw new Error(data.error); }
          if (data.image_url) {
            const newTag = `<img src="${data.image_url}" alt="${prompt}" style="max-width:100%; border-radius:8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">`;
            currentMd = currentMd.replace(fullMatch, newTag);
            editor.value = currentMd;
            updatePreview();
          }
        }
        
      } catch (err) {
        alert("Image generation failed: " + err);
      } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
      }
    }
</script>
</body>
</html>
"""

with open('web/templates/index.html', 'w') as f:
    f.write(head + safe_script)

print("index.html rewritten successfully.")
