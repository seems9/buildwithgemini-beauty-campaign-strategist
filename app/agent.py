# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import datetime
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import ToolContext
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
import google.auth
import google.auth.transport.requests
from google.cloud import firestore, storage
from google import genai
from google.genai import types
import requests

from .a2ui_utils import a2ui_callback

# Hardcoded project ID as string to avoid project number issues on Agent Platform
PROJECT_ID = "qwiklabs-gcp-04-3d5d3b45ddf7"
LOCATION = "us-east1"
MEMORY_BANK_ID = "7430154333859086336"
BUCKET_NAME = "beauty-campaign-assets-qwiklabs-gcp-04-3d5d3b45ddf7"
MODEL = "gemini-2.5-flash"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def list_products(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """List beauty products from the catalog in Firestore, optionally filtering by category.

    Args:
        category: Optional category filter, e.g. 'Skincare', 'Hybrid Makeup', or 'Lip Care'.

    Returns:
        A list of matching product items with SKU, name, brand, category, price, hero ingredients, and claims.
    """
    db = _get_firestore_client()
    query = db.collection("products")
    if category:
        query = query.where("category", "==", category)
    docs = query.stream()
    return [doc.to_dict() for doc in docs]


def list_campaign_pitches(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetch existing beauty campaign pitches and scheduled calendar entries from Firestore.

    Args:
        status: Optional filter by status ('Draft', 'Approved', 'Scheduled').

    Returns:
        A list of campaign pitch documents with hook, target audience, format, platform, and impact score.
    """
    db = _get_firestore_client()
    query = db.collection("campaign_pitches")
    if status:
        query = query.where("status", "==", status)
    docs = query.stream()
    return [doc.to_dict() for doc in docs]


def save_campaign_pitch(
    campaign_id: str,
    title: str,
    hook: str,
    target_audience: str,
    format: str,
    platform: str,
    scheduled_week: str,
    impact_score: int,
    impact_basis: str,
    status: str = "Draft",
    region: str = "US",
) -> Dict[str, Any]:
    """Save or update a campaign pitch in the Firestore campaign_pitches collection.

    Args:
        campaign_id: Unique campaign identifier (e.g., 'CAMP-LIP-04').
        title: Campaign title or concept name.
        hook: One-line compelling hook for the campaign.
        target_audience: Target consumer persona or audience demographic.
        format: Creative format (e.g., 'IG Carousel', 'TikTok UGC 15s', 'Email Hero').
        platform: Target platform(s) (e.g., 'Instagram', 'TikTok', 'YouTube Shorts').
        scheduled_week: Target calendar rollout (e.g., 'Week 3', '2026-10-15').
        impact_score: Projected impact score (1-100).
        impact_basis: Rationale for the impact score.
        status: Campaign status ('Draft', 'Approved', 'Scheduled'). Defaults to 'Draft'.
        region: Geographic region ('US', 'CA-EN', 'CA-FR'). Defaults to 'US'.

    Returns:
        Confirmation dictionary with the saved campaign details.
    """
    db = _get_firestore_client()
    data = {
        "campaign_id": campaign_id,
        "title": title,
        "hook": hook,
        "target_audience": target_audience,
        "format": format,
        "platform": platform,
        "scheduled_week": scheduled_week,
        "impact_score": impact_score,
        "impact_basis": impact_basis,
        "status": status,
        "region": region,
        "updated_at": datetime.datetime.now(ZoneInfo("UTC")).isoformat(),
    }
    db.collection("campaign_pitches").document(campaign_id).set(data, merge=True)
    return {"status": "success", "message": f"Campaign pitch '{campaign_id}' saved successfully.", "campaign": data}


def get_beauty_trends(
    category: Optional[str] = None,
    concern_or_tag: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetch real-time beauty intelligence: trending ingredients, viral social hooks, search growth, and platform hashtags.

    Args:
        category: Optional category filter: 'Skincare', 'Hybrid Makeup', or 'Lip Care'.
        concern_or_tag: Optional search term or concern (e.g., 'barrier', 'glow', 'hydration', 'minimalism').

    Returns:
        List of trend intelligence objects including trend name, growth velocity, viral hooks, top hashtags, and marketing implications.
    """
    trends_database = [
        {
            "trend_name": "Skin Streaming & Anti-Routine",
            "category": "Skincare",
            "search_growth_yoy": "+142%",
            "top_hashtags": ["#SkinStreaming", "#Skinimalism", "#LessStepsMoreGlow"],
            "hero_ingredients": ["Ceramides", "Hyaluronic Acid", "Centella Asiatica"],
            "viral_hook_angles": [
                "Stop layering 8 serums: Here is the 3-step routine dermatologists actually use.",
                "How I cut my morning routine from 15 mins to 3 drops.",
            ],
            "marketing_takeaway": "Focus on 3-in-1 multi-benefit hero products that combat skin barrier exhaustion.",
        },
        {
            "trend_name": "Glass-Skin Serum Tints with SPF",
            "category": "Hybrid Makeup",
            "search_growth_yoy": "+185%",
            "top_hashtags": ["#SerumTint", "#GlassSkin", "#NoMakeupMakeup", "#DewyBase"],
            "hero_ingredients": ["Niacinamide", "Peptides", "Mineral SPF 30+"],
            "viral_hook_angles": [
                "Foundation is out, skincare tints with SPF are in.",
                "This serum tint looks like real skin, but on its best vacation day.",
            ],
            "marketing_takeaway": "Position as skincare-first hybrid makeup with effortless finger-application appeal.",
        },
        {
            "trend_name": "Glaze & Cushion Peptide Lip Oils",
            "category": "Lip Care",
            "search_growth_yoy": "+210%",
            "top_hashtags": ["#LipOilObsession", "#GlazeLip", "#PeptidePlump"],
            "hero_ingredients": ["Tripeptides", "Jojoba Oil", "Vitamin E"],
            "viral_hook_angles": [
                "The only lip product that gives sticky-free high shine and 8-hour cushion.",
                "Lip gloss that doubles as an intensive peptide treatment.",
            ],
            "marketing_takeaway": "High impulse-buy / checkout addition; prioritize ASMR texture swatches and applicator macro videos.",
        },
        {
            "trend_name": "Ectoin & Barrier SOS Recovery",
            "category": "Skincare",
            "search_growth_yoy": "+195%",
            "top_hashtags": ["#BarrierRepair", "#SkinBarrierSOS", "#EctoinSkincare"],
            "hero_ingredients": ["Ectoin", "Bifida Ferment", "Colloidal Oat"],
            "viral_hook_angles": [
                "Over-exfoliated? Here is the exact reset formula to rescue your barrier in 48 hours.",
                "Why every dermatologist is swapping pure retinol for ectoin barrier buffers.",
            ],
            "marketing_takeaway": "Clinically-grounded educational angles targeting redness, post-treatment recovery, and winter transition.",
        },
    ]

    results = trends_database
    if category:
        results = [t for t in results if t["category"].lower() == category.lower()]
    if concern_or_tag:
        term = concern_or_tag.lower()
        results = [
            t
            for t in results
            if term in t["trend_name"].lower()
            or term in t["marketing_takeaway"].lower()
            or any(term in h.lower() for h in t["top_hashtags"])
            or any(term in ing.lower() for ing in t["hero_ingredients"])
        ]
    return results


async def generate_campaign_visual(
    prompt: str,
    asset_name: str,
    tool_context: ToolContext,
) -> Dict[str, Any]:
    """Generate a visual creative concept or mockup image using gemini-3.1-flash-lite-image in the global region.

    The image is saved as a session artifact and uploaded to the public Cloud Storage bucket.

    Args:
        prompt: Detailed creative art-direction prompt describing the product hero shot, social mockup, or campaign visual.
        asset_name: Short kebab-case or snake_case name for the image asset (e.g. 'milky-toner-hero', 'skin-streaming-carousel-01').
        tool_context: ADK ToolContext automatically injected by the runtime.

    Returns:
        A dictionary containing the public Cloud Storage URL (https://storage.googleapis.com/<bucket>/<object>),
        artifact details, and confirmation message.
    """
    clean_name = asset_name.strip().lower().replace(" ", "-").replace(".jpg", "").replace(".jpeg", "")
    filename = f"{clean_name}.jpg"

    # 1. Generate image using gemini-3.1-flash-lite-image in global region via Vertex AI
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    image_bytes = None
    for part in response.parts:
        if part.inline_data and part.inline_data.data:
            image_bytes = part.inline_data.data
            break

    if not image_bytes:
        return {"status": "error", "message": "Failed to generate image from model."}

    # 2. Save image as an artifact so it appears in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 3. Upload image bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    timestamp = datetime.datetime.now(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")
    object_name = f"mockups/{timestamp}_{filename}"
    blob = bucket.blob(object_name)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"

    return {
        "status": "success",
        "message": f"Visual concept generated and saved as artifact '{filename}'.",
        "public_url": public_url,
        "artifact_name": filename,
    }


async def generate_campaign_video(
    prompt: str,
    asset_name: str,
    tool_context: ToolContext,
    aspect_ratio: str = "9:16",
    duration: str = "3s",
) -> Dict[str, Any]:
    """Generate a short social media ad video for a beauty item or campaign using Google's Omni model (gemini-omni-flash-preview) in the global region.

    The video is saved as a session artifact and uploaded to the public Cloud Storage bucket.

    Args:
        prompt: Detailed creative prompt describing the short social media video ad (e.g. 'Aesthetic 3-second macro video of liquid beauty serum droplet dropping into water with soft lighting').
        asset_name: Short kebab-case or snake_case name for the video asset (e.g. 'hydrating-toner-social-ad', 'lip-oil-glaze-reel').
        tool_context: ADK ToolContext automatically injected by the runtime.
        aspect_ratio: Video aspect ratio, e.g. '9:16' for vertical reels/TikTok or '16:9' for horizontal landscape.
        duration: Video duration between '3s' and '10s' (e.g. '3s', '5s').

    Returns:
        A dictionary containing the public Cloud Storage URL (https://storage.googleapis.com/<bucket>/<object>),
        artifact details, and confirmation message.
    """
    clean_name = asset_name.strip().lower().replace(" ", "-").replace(".mp4", "")
    filename = f"{clean_name}.mp4"

    # 1. Acquire Google Auth credentials for Interactions API call
    credentials, _ = google.auth.default()
    auth_req = google.auth.transport.requests.Request()
    credentials.refresh(auth_req)

    url = f"https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/global/interactions"
    headers = {
        "Authorization": f"Bearer {credentials.token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "gemini-omni-flash-preview",
        "input": [{"type": "text", "text": prompt}],
        "response_format": [
            {
                "type": "video",
                "aspect_ratio": aspect_ratio if aspect_ratio in ["9:16", "16:9"] else "9:16",
                "duration": duration if duration in ["3s", "4s", "5s", "6s", "7s", "8s", "9s", "10s"] else "3s",
            }
        ],
        "generation_config": {
            "video_config": {
                "task": "text_to_video"
            }
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=180)
    if resp.status_code != 200:
        return {
            "status": "error",
            "message": f"Failed to generate video with gemini-omni-flash-preview: HTTP {resp.status_code} - {resp.text}",
        }

    resp_data = resp.json()
    video_bytes = None
    for step in resp_data.get("steps", []):
        if step.get("type") == "model_output":
            for content_item in step.get("content", []):
                if content_item.get("type") == "video" and "data" in content_item:
                    video_bytes = base64.b64decode(content_item["data"])
                    break

    if not video_bytes:
        return {"status": "error", "message": "No video data returned from gemini-omni-flash-preview."}

    # 2. Save video as a session artifact
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 3. Upload video bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    timestamp = datetime.datetime.now(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")
    object_name = f"videos/{timestamp}_{filename}"
    blob = bucket.blob(object_name)
    blob.upload_from_string(video_bytes, content_type="video/mp4")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{object_name}"

    return {
        "status": "success",
        "message": f"Social media ad video generated and saved as artifact '{filename}'.",
        "public_url": public_url,
        "artifact_name": filename,
    }


async def generate_memories_callback(callback_context: CallbackContext):
    """Save session to Memory Bank after each turn to extract user preferences and durable facts."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

ROLE_DESCRIPTION = """You are the Content Intelligence & Campaign Strategist for Sephora Marketing.
Given campaign goals and context, you propose marketing strategies, angles, tailored content pitches, and editorial calendars.
You remember the user's stated preferences, brand voice guardrails, past critique, and campaign constraints across conversations and use them to personalize your strategy.

You have access to:
1. `generate_campaign_visual`: Generate visual concept mockups using gemini-3.1-flash-lite-image in the global region. Saves to Artifacts and uploads to Cloud Storage returning a public HTTPS URL.
2. `get_beauty_trends`: Curated beauty intelligence database (trending ingredients, viral social hooks, growth velocity, and platform hashtags).
3. `list_products`: Curated beauty catalog items in Firestore (SKUs, brands, hero ingredients, claims, pricing).
4. `list_campaign_pitches`: Stored campaign pitches, editorial schedules, hooks, and statuses in Firestore.
5. `save_campaign_pitch`: Save or update campaign pitches directly to Firestore.

Always ground pitch concepts in trending data and products from the catalog."""

INSTRUCTION = schema_manager.generate_system_prompt(
    role_description=ROLE_DESCRIPTION,
    workflow_description="Analyze the beauty marketing request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[
        PreloadMemoryTool(),
        generate_campaign_visual,
        generate_campaign_video,
        get_beauty_trends,
        list_products,
        list_campaign_pitches,
        save_campaign_pitch,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)

