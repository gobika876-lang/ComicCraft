import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN not found in .env")

client = InferenceClient(
    api_key=HF_TOKEN,
    provider="auto"
)

OUTPUT_FOLDER = os.path.join(
    "static",
    "images",
    "generated"
)

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


def generate_comic_images(
    panels,
    character_name="Main Character",
    art_style="Cartoon"
):

    image_paths = []

    print("\n🎨 Starting AI comic image generation...", flush=True)
    print(f"👤 Character: {character_name}", flush=True)
    print(f"🎨 Art Style: {art_style}", flush=True)

    # Same identity instructions are used for every panel
    character_description = f"""
MAIN CHARACTER:

The main character is named {character_name}.

Keep {character_name} visually consistent across all five
comic panels.

The character should maintain:
- the same face
- the same hairstyle
- the same skin tone
- the same age
- the same body proportions
- the same clothing
- the same important accessories
- the same overall identity

Do not redesign the character between panels.
Do not randomly change the character's appearance.
"""

    style_description = f"""
ART STYLE:

{art_style} style comic illustration.

Use the selected style consistently across all five panels.
High-quality digital artwork,
clear line art,
good lighting,
vibrant colors,
expressive characters,
detailed backgrounds,
professional comic composition.
"""

    for index, panel in enumerate(panels, start=1):

        print(f"\n🖼️ Generating Panel {index}...", flush=True)

        image_prompt = panel.get("image_prompt", "")

        if not image_prompt:
            image_prompt = panel.get(
                "scene_description",
                ""
            )

        prompt = f"""
Create Panel {index} of a five-panel AI comic.

{character_description}

{style_description}

STORY SCENE:

{image_prompt}

IMPORTANT CHARACTER CONSISTENCY:

{character_name} must be the same main character
throughout the entire comic.

Keep the character recognizable from previous panels.

The scene may change, the character's pose may change,
and the facial expression may change according to the story,
but the character's identity must remain consistent.

Show the correct action and environment described in the scene.

Do not add panel numbers.
Do not add captions.
Do not add watermarks.
Do not add logos.
Do not put written text inside the image.
"""

        negative_prompt = f"""
different character,
different face,
different hairstyle,
different age,
different body type,
different skin tone,
different clothing,
character redesign,
duplicate character,
extra person,
deformed face,
bad anatomy,
extra fingers,
extra arms,
extra legs,
blurry image,
low quality,
watermark,
logo,
caption,
text,
panel number
"""

        try:

            image = client.text_to_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                model="black-forest-labs/FLUX.1-schnell",
                width=768,
                height=768
            )

            filename = f"panel{index}.png"

            filepath = os.path.join(
                OUTPUT_FOLDER,
                filename
            )

            image.save(filepath)

            print(
                f"✅ Panel {index} generated successfully!",
                flush=True
            )

            print(
                f"📁 Saved: {filepath}",
                flush=True
            )

            image_paths.append(
                f"/static/images/generated/{filename}"
            )

        except Exception as e:

            print(
                f"❌ Panel {index} generation failed:",
                flush=True
            )

            print(str(e), flush=True)

            image_paths.append(
                "/static/images/panel-placeholder.png"
            )

    print(
        "\n🎉 All comic images processed!",
        flush=True
    )

    return image_paths
# =========================================================
# REGENERATE ONE COMIC PANEL
# =========================================================

def regenerate_single_comic_image(
    panel,
    panel_number,
    character_name="Main Character",
    art_style="Cartoon"
):

    print(
        f"\n🔄 Regenerating Panel {panel_number}...",
        flush=True
    )

    image_prompt = panel.get(
        "image_prompt",
        ""
    )

    if not image_prompt:
        image_prompt = panel.get(
            "scene_description",
            ""
        )


    # Same character identity instructions
    character_description = f"""
MAIN CHARACTER:

The main character is named {character_name}.

Keep the character visually consistent.

Maintain:
- same face
- same hairstyle
- same skin tone
- same age
- same body proportions
- same clothing
- same accessories
- same overall identity

Do not redesign the character.
"""


    # Art style
    style_description = f"""
ART STYLE:

{art_style} style comic illustration.

Use:
- high quality digital artwork
- clear line art
- good lighting
- vibrant colors
- expressive characters
- detailed background
- professional comic composition
"""


    prompt = f"""
Create Panel {panel_number} of an AI comic.

{character_description}

{style_description}

STORY SCENE:

{image_prompt}

IMPORTANT:

The character named {character_name}
must remain visually consistent.

The character's pose and facial expression
can change according to the story.

Keep the same character identity.

Show the correct environment and action.

Do not add:
- captions
- panel numbers
- watermarks
- logos
- written text
"""


    negative_prompt = """
different character,
different face,
different hairstyle,
different age,
different body type,
different skin tone,
different clothing,
character redesign,
extra person,
duplicate character,
deformed face,
bad anatomy,
extra fingers,
extra arms,
extra legs,
blurry image,
low quality,
watermark,
logo,
caption,
text,
panel number
"""


    try:

        image = client.text_to_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            model="black-forest-labs/FLUX.1-schnell",
            width=768,
            height=768
        )


        filename = f"panel{panel_number}.png"

        filepath = os.path.join(
            OUTPUT_FOLDER,
            filename
        )


        # Replace old panel image
        image.save(filepath)


        print(
            f"✅ Panel {panel_number} regenerated!",
            flush=True
        )

        print(
            f"📁 Saved: {filepath}",
            flush=True
        )


        return (
            f"/static/images/generated/{filename}"
        )


    except Exception as e:

        print(
            f"❌ Panel {panel_number} regeneration failed:",
            flush=True
        )

        print(
            str(e),
            flush=True
        )

        return (
            "/static/images/panel-placeholder.png"
        )