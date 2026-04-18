with open('web/templates/index.html', 'r') as f:
    text = f.read()

import re
head = text.split('<script>')[0]

script_content = """<script>
    let timeoutId;
    const editor = document.getElementById('md-editor');
    const previewFrame = document.getElementById('preview-frame');

    updatePreview();

    function debouncePreview() {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(updatePreview, 500);
    }

    function updatePreview() {
      const mdContent = editor.value;
      const endTextarea = String.fromCharCode(60) + '/textarea' + String.fromCharCode(62);
      const repTextarea = '&lt;/textarea&gt;';
      const cleanMd = mdContent.split(endTextarea).join(repTextarea);
      
      const endScript = String.fromCharCode(60) + '/script' + String.fromCharCode(62);
      
      const htmlContent = `
        <!DOCTYPE html>
        <html>
        <head>
          <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/reveal.min.css">
          <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/theme/black.min.css">
          <style>
            .reveal section img { max-height: 50vh; max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            .reveal .slides { text-align: left; }
            .reveal .slides h1, .reveal .slides h2 { text-align: center; }
          </style>
        </head>
        <body>
          <div class="reveal">
            <div class="slides">
              <section data-markdown>
                <textarea data-template>${cleanMd}</textarea>
              </section>
            </div>
          </div>
          <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/reveal.min.js">${endScript}
          <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.6.1/plugin/markdown/markdown.min.js">${endScript}
          <script>
            Reveal.initialize({ hash: false, plugins: [ RevealMarkdown ] });
          ${endScript}
        </body>
        </html>
      `;
      previewFrame.srcdoc = htmlContent;
    }

    function submitForm(actionUrl) {
      const form = document.getElementById('actions-form');
      document.getElementById('hidden-md').value = editor.value;
      form.action = actionUrl;
      form.submit();
    }

    async function generateSlides() {
      const prompt = document.getElementById('prompt-input').value;
      if (!prompt) return alert("Please enter a prompt!");
      
      toggleLoader('text-loader', true);
      document.getElementById('btn-generate').disabled = true;

      try {
        const res = await fetch('/api/generate_slides', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        editor.value = data.markdown;
        updatePreview();
      } catch (e) {
        alert("Error: " + e.message);
      } finally {
        toggleLoader('text-loader', false);
        document.getElementById('btn-generate').disabled = false;
      }
    }

    async function modifySlides() {
      const prompt = document.getElementById('prompt-input').value;
      if (!prompt) return alert("Please enter a prompt describing the changes!");
      
      toggleLoader('text-loader', true);
      document.getElementById('btn-modify').disabled = true;

      try {
        const res = await fetch('/api/modify_slides', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt, current_markdown: editor.value })
        });
        const data = await res.json();
        if (data.error) throw new Error(data.error);
        editor.value = data.markdown;
        updatePreview();
      } catch (e) {
        alert("Error: " + e.message);
      } finally {
        toggleLoader('text-loader', false);
        document.getElementById('btn-modify').disabled = false;
      }
    }

    async function autoGenerateImages() {
      toggleLoader('img-loader', true);
      document.getElementById('btn-images').disabled = true;
      
      try {
        let content = editor.value;
        
        // 1. Process inline images: ![prompt](auto)
        const inlineRegex = /!\[(.*?)\]\(auto\)/g;
        let inlineMatches = [...content.matchAll(inlineRegex)];
        for (const match of inlineMatches) {
          const prompt = match[1];
          console.log("Generating inline image for:", prompt);
          try {
            const res = await fetch('/api/generate_image', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ prompt: prompt })
            });
            const data = await res.json();
            if (data.image_url) {
              content = content.replace(match[0], `![${prompt}](${data.image_url})`);
            }
          } catch(e) { console.error(e); }
        }

        // 2. Process background images: <!-- bg: prompt -->
        const bgRegex = /<!--\\s*bg:\\s*(.*?)\\s*-->/g;
        let bgMatches = [...content.matchAll(bgRegex)];
        for (const match of bgMatches) {
          const prompt = match[1];
          console.log("Generating background for:", prompt);
          try {
            const res = await fetch('/api/generate_image', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ prompt: prompt })
            });
            const data = await res.json();
            if (data.image_url) {
              const bgTag = `<!-- .slide: data-background-image="${data.image_url}" data-background-opacity="0.3" -->`;
              content = content.replace(match[0], bgTag);
            }
          } catch(e) { console.error(e); }
        }
        
        editor.value = content;
        updatePreview();
        alert("Images generated successfully!");
      } catch (e) {
        alert("Error generating images: " + e.message);
      } finally {
        toggleLoader('img-loader', false);
        document.getElementById('btn-images').disabled = false;
      }
    }

    function toggleLoader(id, show) {
      document.getElementById(id).classList.toggle('hidden', !show);
    }
  </script>
</body>
</html>"""

new_text = head + script_content

with open('web/templates/index.html', 'w') as f:
    f.write(new_text)
