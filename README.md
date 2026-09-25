# Beauty Campaign Strategist

An intelligent conversational AI agent built for beauty marketing and merchandising teams. The agent assists brand managers and creative strategists in planning marketing campaigns, researching trending ingredients and viral beauty narratives, exploring curated product catalogs, generating visual concept mockups, and persisting campaign pitches.

---

## What the Agent Does

Based on the implemented codebase in `app/`, the agent provides:

1. **Long-Term Memory across Sessions**:
   - Integrated with **Vertex AI Memory Bank** via `PreloadMemoryTool` and an automated `after_agent_callback`.
   - Remembers user campaign preferences, target audiences, brand guidelines, past critique, and tone-of-voice constraints across conversations.

2. **Curated Product Catalog & Pitch Persistence (Firestore)**:
   - `list_products`: Queries the live product catalog in **Google Cloud Firestore** with category filters (e.g., Skincare, Hybrid Makeup, Lip Care), returning SKUs, ingredients, claims, and pricing.
   - `list_campaign_pitches`: Retrieves stored campaign pitches, editorial schedules, hooks, and statuses from Firestore.
   - `save_campaign_pitch`: Saves newly agreed campaign pitches and marketing angles directly into Firestore.

3. **Curated Trend Intelligence**:
   - `get_beauty_trends`: Searches curated viral beauty intelligence for ingredient momentum, trending hashtags, growth velocity, and target demographics.

4. **Visual Concept & Mockup Generation (Imagen / Gemini + Cloud Storage)**:
   - `generate_campaign_visual`: Generates creative concept art and product hero shot mockups using `gemini-3.1-flash-lite-image` via the Google GenAI Vertex AI client.
   - Saves the generated asset into session artifacts and uploads high-resolution images to a public **Google Cloud Storage** bucket, returning a permanent HTTPS asset URL.

5. **Rich A2UI Card Surfaces**:
   - Uses `a2ui-agent-sdk` (`A2uiSchemaManager` v0.8 + `BasicCatalog`) and an `after_model_callback` to format responses into clean UI cards (`Card`, `Column`, `Row`, `Text`, `Image`) instead of plain unstructured text.

---

## Architecture & Google Cloud Services

- **Reasoning Model**: `gemini-2.5-flash` via Google Vertex AI
- **Image Generation Model**: `gemini-3.1-flash-lite-image` (Global Region)
- **Agent Framework**: Google Agent Development Kit (ADK) / Agent Runtime (A2A protocol)
- **Memory Service**: Vertex AI Memory Bank (`VertexAiMemoryBankService`)
- **Database**: Google Cloud Firestore (`products` and `campaign_pitches` collections)
- **Object Storage**: Google Cloud Storage (`beauty-campaign-assets-*` bucket)
- **Frontend / Proxy**: Minimal FastAPI service talking A2A with Application Default Credentials and rendering A2UI components in a custom Sephora-themed UI.

---

## Status of Features from Project Brief

| Feature | Status | Notes |
| :--- | :--- | :--- |
| Cross-session Memory | **Implemented** | Vertex AI Memory Bank + `PreloadMemoryTool` |
| Product Catalog Search | **Implemented** | Cloud Firestore collection queries |
| Trend Intelligence | **Implemented** | Curated intelligence database (`get_beauty_trends`) |
| Image Concept Mockups | **Implemented** | `gemini-3.1-flash-lite-image` + Cloud Storage upload |
| A2UI Card Generation | **Implemented** | A2UI v0.8 schemas + custom web renderer |
| Campaign Pitch Storage | **Implemented** | Firestore persistence (`save_campaign_pitch`) |
| Code Sandbox ROI Modeling | *Planned, not yet implemented* | Sandbox calculation engine planned for future release |

---

## Getting Started Locally

### 1. Prerequisites
- Python 3.11+
- `uv` package manager installed
- Google Cloud CLI authenticated with Application Default Credentials:
  ```bash
  gcloud auth application-default login
  ```

### 2. Run the Agent Locally (ADK Web)
From the project root:
```bash
# Set your environment
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_CLOUD_LOCATION="us-east1"

# Launch the ADK development playground
uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://<memory-bank-id>
```

### 3. Run the Custom Frontend Locally
In a separate terminal:
```bash
cd frontend

# Set the deployed agent resource name
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-id>/locations/<region>/reasoningEngines/<id>"
export AGENT_DIRECTORY="app"
export PORT="8080"

# Install frontend dependencies and run
uv pip install -r requirements.txt --python .venv
.venv/bin/python main.py
```
