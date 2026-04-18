# AI Slide Agent

AI Slide Agent is a web-based full-stack application that transforms simple text prompts or Markdown content into interactive, fully styled Reveal.js presentations. It integrates deeply with local AI models to dynamically generate slide content and slide imagery.

![AI Slide Agent Preview](web/static/images/hero-preview.png) *(Note: Placeholder image path)*

## Features

- **Interactive Chat/Editor UI**: A split-screen layout where you can write prompts to generate Markdown, manually edit the generated Markdown, and interact with the AI assistant.
- **Live Preview**: An iframe-based live preview utilizing Reveal.js to render the Markdown with auto-scaling images and custom HTML layouts (e.g., flexbox for columns).
- **AI Content Generation**: Send natural language prompts to a local LLM to output Reveal.js-compatible Markdown.
- **AI Image Generation**: Automatically parses the Markdown for specific image tags (`<!-- bg: [prompt] -->` and `![[prompt]](auto)`), dispatches requests to the local image model, saves the results, and injects the paths back into the frontend preview.
- **Export to Offline HTML**: Download a standalone HTML file of your presentation, with all generated images bundled as Base64 strings.

## Architecture

This project is built following Spec Driven Development (SDD) principles. Detailed architecture and task breakdowns can be found in the `specs/` directory.

- **Backend:** Flask (Python 3.9+)
- **Frontend:** HTML, Tailwind CSS, JavaScript, Reveal.js (4.6.1)
- **AI Models:** 
  - Text: `gemini-3.1-pro-preview:latest` (via local Ollama node or OpenAI-compatible API)
  - Image: `gemini-3.1-flash-image-preview:latest` (or `imagen-4.0-generate-001:latest`)
- **Data Storage:** Local filesystem (`static/images` for generated visuals).

## Getting Started

### Prerequisites

- Python 3.9 or higher
- A local AI provider (e.g., Ollama or a custom OpenAI-compatible endpoint) running on `http://localhost:11211/api/openai/v1`.

### Installation

1. Clone the repository:
   ```bash
   git clone git@github.com:Darth-Acheron/ai-slide-agent.git
   cd ai-slide-agent
   ```

2. Install backend dependencies:
   ```bash
   pip install flask requests pytest
   ```

3. Run the Flask application:
   ```bash
   cd web
   python3 app.py
   ```

4. Open your browser and navigate to `http://localhost:8080`.

## Usage & Markdown Syntax

The AI agent generates standard Reveal.js markdown, but introduces two special tags for automatic image generation:

1. **Slide Backgrounds**: Use an HTML comment to prompt a full-screen background image.
   ```html
   <!-- bg: A cinematic shot of a futuristic city at night -->
   ```

2. **Inline Images**: Use double brackets with the `(auto)` suffix to generate an inline image.
   ```markdown
   ![[A robot painting on an easel]](auto)
   ```

Click the **"Auto-Gen Images (Bg + Inline)"** button in the UI to parse these tags, trigger the local image generation model, and replace the tags with the generated image paths.

## Testing

The project includes a suite of functional and integration tests covering the API endpoints, markdown parsing logic, and image generation flow.

To run the tests:
```bash
python3 -m pytest test_app.py
```

## Security & Constraints

- **Local Execution Only**: The Flask server runs on `0.0.0.0:8080` without authentication. It is designed as a local tool and should **not** be exposed to the public internet without adding API key authentication and sanitizing the Markdown input.
- **Image Generation Timeouts**: Local image generation models can take 40-130 seconds per image. The application backend uses generous timeouts (`timeout=300`), but frontend UI feedback (loading spinners) is critical during this process.

## License

MIT License
