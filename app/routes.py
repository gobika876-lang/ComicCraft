import os
import zipfile

from flask import Blueprint, render_template, request, send_file

from .gemini_flash import generate_outline
from .gemini_pro import generate_comic_story
from .image_generator import generate_comic_images

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


# =========================================================
# GENERATE COMIC
# =========================================================

@main.route("/generate", methods=["POST"])
def generate():

    print(">>> GENERATE ROUTE CALLED <<<", flush=True)

    story_prompt = request.form.get("story_prompt", "").strip()
    character_name = request.form.get("character_name", "").strip()
    setting = request.form.get("setting", "").strip()
    tone = request.form.get("tone", "").strip()
    art_style = request.form.get("art_style", "").strip()

    if not story_prompt:
        return "Please enter a story prompt.", 400

    if not character_name:
        return "Please enter a character name.", 400

    if not setting:
        return "Please select a setting.", 400

    if not tone:
        return "Please select a story tone.", 400

    if not art_style:
        return "Please select an art style.", 400


    # =====================================================
    # STEP 1: GEMINI FLASH
    # =====================================================

    print("\n==============================")
    print("STEP 1: Gemini Flash")
    print("==============================", flush=True)

    panels = generate_outline(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style
    )

    print("5-panel outline generated.", flush=True)


    # =====================================================
    # STEP 2: GEMINI STORY
    # =====================================================

    print("\n==============================")
    print("STEP 2: Gemini Story")
    print("==============================", flush=True)

    detailed_panels = generate_comic_story(panels)

    print("Detailed comic story generated.", flush=True)


    # =====================================================
    # STEP 3: HUGGING FACE IMAGE GENERATOR
    # =====================================================

    print("\n==============================")
    print("STEP 3: Hugging Face Image Generator")
    print("==============================", flush=True)

    image_paths = generate_comic_images(
        detailed_panels,
        character_name=character_name,
        art_style=art_style
    )

    print("5 comic panel images generated.", flush=True)


    # =====================================================
    # CREATE STORY TXT FILE
    # =====================================================

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )

    generated_folder = os.path.join(
        project_root,
        "static",
        "images",
        "generated"
    )

    os.makedirs(generated_folder, exist_ok=True)

    story_file_path = os.path.join(
        generated_folder,
        "ComicCraft_Story.txt"
    )


    with open(
        story_file_path,
        "w",
        encoding="utf-8"
    ) as story_file:

        story_file.write(
            "========================================\n"
        )
        story_file.write(
            "        COMICRAFT - AI COMIC STORY\n"
        )
        story_file.write(
            "========================================\n\n"
        )

        story_file.write(
            f"Story Prompt: {story_prompt}\n"
        )

        story_file.write(
            f"Character: {character_name}\n"
        )

        story_file.write(
            f"Setting: {setting}\n"
        )

        story_file.write(
            f"Tone: {tone}\n"
        )

        story_file.write(
            f"Art Style: {art_style}\n\n"
        )

        story_file.write(
            "========================================\n\n"
        )


        # Write all 5 panels
        for index, panel in enumerate(
            detailed_panels,
            start=1
        ):

            title = panel.get(
                "title",
                f"Panel {index}"
            )

            scene = panel.get(
                "scene_description",
                ""
            )

            dialogue = panel.get(
                "dialogue",
                ""
            )

            image_prompt = panel.get(
                "image_prompt",
                ""
            )

            story_file.write(
                f"PANEL {index}\n"
            )

            story_file.write(
                f"Title: {title}\n\n"
            )

            story_file.write(
                "Scene Description:\n"
            )

            story_file.write(
                f"{scene}\n\n"
            )

            story_file.write(
                "Dialogue:\n"
            )

            story_file.write(
                f"{dialogue}\n\n"
            )

            story_file.write(
                "Image Generation Prompt:\n"
            )

            story_file.write(
                f"{image_prompt}\n\n"
            )

            story_file.write(
                "========================================\n\n"
            )


    print(
        "✅ ComicCraft_Story.txt created!",
        flush=True
    )


    # =====================================================
    # RESULT PAGE
    # =====================================================

    return render_template(
        "result.html",
        panels=detailed_panels,
        image_paths=image_paths,
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style
    )


# =========================================================
# DOWNLOAD COMIC ZIP
# =========================================================

@main.route("/download")
def download_comic():

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )

    generated_folder = os.path.join(
        project_root,
        "static",
        "images",
        "generated"
    )

    zip_path = os.path.join(
        project_root,
        "static",
        "ComicCraft_Comic.zip"
    )


    print("\n==============================")
    print("CREATING COMIC ZIP")
    print("==============================", flush=True)


    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED
    ) as zip_file:

        # Add 5 comic images
        for index in range(1, 6):

            image_path = os.path.join(
                generated_folder,
                f"panel{index}.png"
            )

            if os.path.exists(image_path):

                zip_file.write(
                    image_path,
                    f"panel{index}.png"
                )

                print(
                    f"✅ Added panel{index}.png",
                    flush=True
                )

            else:

                print(
                    f"⚠️ panel{index}.png not found",
                    flush=True
                )


        # Add story text file
        story_file_path = os.path.join(
            generated_folder,
            "ComicCraft_Story.txt"
        )

        if os.path.exists(story_file_path):

            zip_file.write(
                story_file_path,
                "ComicCraft_Story.txt"
            )

            print(
                "✅ Added ComicCraft_Story.txt",
                flush=True
            )

        else:

            print(
                "⚠️ ComicCraft_Story.txt not found",
                flush=True
            )


    if not os.path.exists(zip_path):

        return "Comic ZIP could not be created.", 500


    print(
        "✅ Comic ZIP created successfully!",
        flush=True
    )


    return send_file(
        zip_path,
        as_attachment=True,
        download_name="ComicCraft_Comic.zip",
        mimetype="application/zip"
    )
# =========================================================
# REGENERATE SINGLE COMIC PANEL
# =========================================================

@main.route("/regenerate/<int:panel_number>", methods=["POST"])
def regenerate_panel(panel_number):

    print(
        f"\n🔄 REGENERATE PANEL {panel_number}",
        flush=True
    )

    # Check panel number
    if panel_number < 1 or panel_number > 5:
        return "Invalid panel number.", 400


    # Get data from form
    character_name = request.form.get(
        "character_name",
        "Main Character"
    )

    art_style = request.form.get(
        "art_style",
        "Cartoon"
    )

    panel_title = request.form.get(
        "panel_title",
        f"Panel {panel_number}"
    )

    scene_description = request.form.get(
        "scene_description",
        ""
    )

    dialogue = request.form.get(
        "dialogue",
        ""
    )

    image_prompt = request.form.get(
        "image_prompt",
        ""
    )


    # Create panel data
    panel = {
        "title": panel_title,
        "scene_description": scene_description,
        "dialogue": dialogue,
        "image_prompt": image_prompt
    }


    # Import regeneration function
    from .image_generator import regenerate_single_comic_image


    # Generate only selected panel
    image_path = regenerate_single_comic_image(
        panel=panel,
        panel_number=panel_number,
        character_name=character_name,
        art_style=art_style
    )


    print(
        f"✅ Panel {panel_number} regenerated successfully!",
        flush=True
    )


    # Return JSON response
    return {
        "success": True,
        "panel_number": panel_number,
        "image_path": image_path
    }

@main.route("/download-pdf")
def download_pdf():

    from flask import send_file

    pdf_path = os.path.join(
        "static",
        "ComicCraft_Comic.pdf"
    )

    generated_folder = os.path.join(
        "static",
        "images",
        "generated"
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    story = []

    # Title
    story.append(
        Paragraph(
            "ComicCraft - AI Comic Story Creator",
            title_style
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Generated Five-Panel AI Comic",
            heading_style
        )
    )

    story.append(Spacer(1, 15))

    # Add all 5 comic panels
    for index in range(1, 6):

        image_path = os.path.join(
            generated_folder,
            f"panel{index}.png"
        )

        if os.path.exists(image_path):

            story.append(
                Paragraph(
                    f"Panel {index}",
                    heading_style
                )
            )

            story.append(Spacer(1, 8))

            img = Image(
                image_path,
                width=5.8 * inch,
                height=5.8 * inch
            )

            story.append(img)

            story.append(Spacer(1, 20))

    doc.build(story)

    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="ComicCraft_Comic.pdf"
    )