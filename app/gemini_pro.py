import os
import json

try:
    from google import genai
except ImportError:
    genai = None


def generate_comic_story(panels):
    """
    Generate a detailed 5-panel comic story
    from the Gemini Flash outline.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    # ---------------------------------------------------------
    # DEMO MODE
    # ---------------------------------------------------------
    if genai is None or not api_key:
        print("Gemini Pro unavailable.")
        print("Using demo detailed story.")

        return create_demo_story(panels)

    # ---------------------------------------------------------
    # GEMINI PRO MODE
    # ---------------------------------------------------------
    try:

        client = genai.Client(api_key=api_key)

        outline_text = ""

        for panel in panels:
            outline_text += f"""
Panel Number: {panel.get("panel_number", "")}
Title: {panel.get("title", "")}
Scene: {panel.get("scene", "")}
Dialogue: {panel.get("dialogue", "")}
Image Prompt: {panel.get("image_prompt", "")}

"""

        prompt = f"""
You are an expert comic book writer.

Create a detailed 5-panel comic story from the
following comic outline.

COMIC OUTLINE:
{outline_text}

Return ONLY valid JSON.

Use exactly this structure:

{{
    "panels": [
        {{
            "panel_number": 1,
            "title": "string",
            "detailed_scene": "string",
            "dialogue": "string",
            "image_prompt": "string"
        }}
    ]
}}

IMPORTANT REQUIREMENTS:

1. Return exactly 5 panels.
2. Keep the same main character in every panel.
3. Keep the same environment and visual identity.
4. Continue the story naturally from panel to panel.
5. Expand the scene with useful visual details.
6. Keep dialogue short and natural.
7. Make the story suitable for a comic book.
8. Make each image prompt detailed.
9. Include character appearance in image prompts.
10. Include environment, action, lighting and art style.
11. Do not add markdown.
12. Do not add explanations outside the JSON.
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        text = response.text.strip()

        # Remove markdown code fences if Gemini adds them
        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")
            text = text.strip()

        data = json.loads(text)

        if "panels" not in data:
            raise ValueError("Gemini Pro response does not contain panels.")

        detailed_panels = data["panels"]

        if len(detailed_panels) != 5:
            raise ValueError(
                f"Expected 5 panels, got {len(detailed_panels)}"
            )

        print("Gemini Pro generated 5 detailed panels successfully.")

        return detailed_panels

    except Exception as error:

        print("Gemini Pro ERROR:", repr(error), flush=True)
        print("Falling back to demo detailed story.")

        return create_demo_story(panels)


def create_demo_story(panels):
    """
    Local fallback when Gemini Pro is unavailable.
    """

    detailed_panels = []

    for panel in panels:

        panel_number = panel.get("panel_number", "")
        title = panel.get("title", "")
        scene = panel.get("scene", "")
        dialogue = panel.get("dialogue", "")
        image_prompt = panel.get("image_prompt", "")

        detailed_scene = (
            f"{scene} "
            f"The scene is presented as a colorful comic panel "
            f"with expressive characters, clear body language, "
            f"and a visually interesting environment."
        )

        detailed_panels.append(
            {
                "panel_number": panel_number,
                "title": title,
                "detailed_scene": detailed_scene,
                "dialogue": dialogue,
                "image_prompt": image_prompt
            }
        )

    return detailed_panels