# 01 System Architecture and Design

## Project: AI Slide Agent

### 1. Overview
The AI Slide Agent is a web-based full-stack application that transforms simple text prompts or Markdown content into interactive, fully styled Reveal.js presentations. It integrates deeply with local AI models to dynamically generate slide content and slide imagery.

### 2. Architecture
- **Backend:** Flask (Python)
- **Frontend:** HTML, JavaScript, CSS (Reveal.js integrated)
- **AI Models:** 
  - Text: `gemini-3.1-pro-preview:latest` (Local Ollama node via OpenAI-compatible endpoint on port 11211)
  - Image: `gemini-3.1-flash-image-preview:latest` (or `imagen-4.0-generate-001:latest`) via local port 11211.
- **Data Storage:** Local filesystem (`static/images` for generated visuals, and in-memory variables for the current presentation state).

### 3. Core Features
1. **Interactive Chat/Editor UI**: A split-screen layout where the user can write prompts to generate Markdown, manually edit the generated Markdown, and interact with the AI assistant.
2. **Live Preview**: An iframe-based live preview utilizing Reveal.js to render the Markdown with auto-scaling images and custom HTML layouts (e.g., flexbox for columns).
3. **AI Content Generation**: Sending natural language prompts to a local LLM to output Reveal.js compatible Markdown.
4. **AI Image Generation**: Automatically parse the Markdown for specific image tags (`<!-- bg: [prompt] -->` and `![[prompt]](auto)`), dispatch requests to the local image model, save the results, and inject the paths back into the frontend preview.

### 4. Key Endpoints
- `GET /`: Renders the main `index.html` interface.
- `POST /api/generate_slides`: Takes user instruction and uses LLM to generate raw markdown.
- `POST /api/modify_slides`: Modifies existing markdown based on instruction.
- `POST /api/generate_image`: Takes an image generation prompt, calls the local image model, and saves the image to `static/images/`.

### 5. Known Constraints and Workarounds
- Image generation models locally take ~40-130s. API timeouts must be generous.
- Frontend JavaScript Regex for parsing image prompts requires specific strict string-escaping due to Jinja2 template rendering.
- Markdown images nested in `<div>` flexbox layouts break Reveal.js/marked.js, requiring dynamic JS replacement to raw `<img>` tags.