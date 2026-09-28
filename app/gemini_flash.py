import json
import os

try:
    from google import genai
except ImportError:
    genai = None


def generate_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):
    """
    Generate a structured 5-panel comic outline.

    Returns:
        list: Five comic panels.
    """

    # ---------------------------------------------------------
    # DEMO MODE
    # Used when Gemini package/API key is not available.
    # ---------------------------------------------------------
    api_key = os.getenv("GEMINI_API_KEY")

    if genai is None or not api_key:
        return create_demo_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style
        )

    # ---------------------------------------------------------
    # GEMINI MODE
    # ---------------------------------------------------------
    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are an expert comic story planner.

Create a 5-panel comic outline using the following user details.

Story Prompt:
{story_prompt}

Main Character:
{character_name}

Setting:
{setting}

Story Tone:
{tone}

Art Style:
{art_style}

Return ONLY valid JSON.

The JSON must have this structure:

{{
    "panels": [
        {{
            "panel_number": 1,
            "title": "string",
            "scene": "string",
            "dialogue": "string",
            "image_prompt": "string"
        }}
    ]
}}

Requirements:
- Exactly 5 panels.
- Keep the main character consistent.
- Keep the setting consistent.
- Follow the requested tone.
- Follow the requested art style.
- Each panel must continue naturally from the previous panel.
- Image prompts must describe the characters, environment, action and visual style.
- Do not add markdown.
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Remove accidental markdown code fences
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        data = json.loads(text)

        if "panels" not in data:
            raise ValueError("Gemini response does not contain panels.")

        return data["panels"]

    except Exception as error:
        print("Gemini Flash ERROR:", repr(error), flush=True)
        print("Using demo outline instead.")

        return create_demo_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style
        )


def create_demo_outline(
    story_prompt,
    character_name,
    setting,
    tone,
    art_style
):
    """
    Creates a local 5-panel outline when Gemini is unavailable.
    """

    return [
        {
            "panel_number": 1,
            "title": "The Beginning",
            "scene": (
                f"{character_name} begins an exciting adventure in "
                f"{setting}."
            ),
            "dialogue": (
                f"{character_name}: "
                "\"Something amazing is about to happen!\""
            ),
            "image_prompt": (
                f"A cute comic illustration of {character_name} "
                f"starting an adventure in {setting}, "
                f"{art_style} style, expressive face, colorful scene."
            )
        },
        {
            "panel_number": 2,
            "title": "The Problem",
            "scene": (
                f"{character_name} discovers an unexpected problem "
                f"while exploring {setting}."
            ),
            "dialogue": (
                f"{character_name}: "
                "\"Oh no! How am I going to solve this?\""
            ),
            "image_prompt": (
                f"{character_name} facing an unexpected problem in "
                f"{setting}, worried expression, cinematic composition, "
                f"{art_style} comic style."
            )
        },
        {
            "panel_number": 3,
            "title": "The Challenge",
            "scene": (
                f"{character_name} gathers courage and decides to "
                f"face the challenge."
            ),
            "dialogue": (
                f"{character_name}: "
                "\"I won't give up!\""
            ),
            "image_prompt": (
                f"{character_name} bravely facing the challenge in "
                f"{setting}, dynamic action pose, expressive character, "
                f"{art_style} comic illustration."
            )
        },
        {
            "panel_number": 4,
            "title": "The Solution",
            "scene": (
                f"{character_name} finds a creative way to solve "
                f"the problem."
            ),
            "dialogue": (
                f"{character_name}: "
                "\"I finally figured it out!\""
            ),
            "image_prompt": (
                f"{character_name} successfully solving the problem "
                f"in {setting}, happy expression, exciting atmosphere, "
                f"{art_style} comic style."
            )
        },
        {
            "panel_number": 5,
            "title": "The Ending",
            "scene": (
                f"{character_name} completes the adventure and "
                f"celebrates the happy ending."
            ),
            "dialogue": (
                f"{character_name}: "
                "\"What an incredible adventure!\""
            ),
            "image_prompt": (
                f"{character_name} celebrating at the end of the "
                f"adventure in {setting}, joyful expression, beautiful "
                f"final scene, {art_style} comic illustration."
            )
        }
    ]