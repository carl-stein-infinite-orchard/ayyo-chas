#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai",
#     "pillow",
#     "rembg[cpu]",
# ]
# ///
"""
Stage 2: Can Mockup — Nano Banana Pro (Gemini) generates label art from brand_identity.json.

Usage:
    uv run pipeline/can_mockup.py posts/2026-04-10/brand_identity.json
    uv run pipeline/can_mockup.py posts/2026-04-10/brand_identity.json --model pro --size 2K
"""

import argparse
import json
import os
import sys

from google import genai
from google.genai import types
from PIL import Image

MODEL_IDS = {
    "flash": "gemini-2.5-flash-image",
    "pro": "gemini-3-pro-image-preview",
}

CAN_SYSTEM = """\
Generate a photorealistic non-alcoholic seltzer aluminium can with NO background color or image outside the can itself. The background must be completely transparent or solid white — nothing surrounding the can whatsoever. Just the can, isolated, floating.

The can should look like a real product photo:
- Standard 12oz slim aluminium seltzer can
- Photorealistic metallic material with natural light reflections
- Slight condensation droplets on the surface
- Professional product photography lighting (soft studio light, subtle shadow underneath only)
- The can label wraps around the can naturally with realistic curvature
- The flavor name is the dominant text element on the label
- The tagline appears smaller on the can
- Do NOT put any brand name on the can — just the flavor name and tagline
"""


def load_identity(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def build_prompt(identity: dict) -> str:
    base = identity.get("image_prompt", "")
    flavor = identity.get("flavor", "Unknown")
    tagline = identity.get("tagline", "")
    palette = identity.get("palette", {})
    category = identity.get("category", "interesting")

    category_hint = {
        "interesting": "The label design should feel intriguing and appetizing despite being unusual.",
        "gross": "The label design should lean into the gross factor — funny-disgusting, not actually repulsive.",
        "impossible": "The label design should be dreamy, abstract, and conceptual — illustrating a vibe as a beverage.",
    }

    prompt = f"""{CAN_SYSTEM}

Flavor: "{flavor}"
Tagline: "{tagline}"
Category: {category} — {category_hint.get(category, '')}
Label color palette: primary {palette.get('primary', '#4A90D9')}, accent {palette.get('accent', '#F5A623')}
Label vibe: {palette.get('vibe', 'modern-playful')}
Label art direction: {base}

CRITICAL: The output image must show ONLY the can — no background, no surface, no scenery, no props. Transparent or pure white background. One photorealistic aluminium seltzer can, isolated, centered."""

    return prompt


def generate_label(
    prompt: str,
    output_path: str,
    model: str = "flash",
    size: str = "1K",
) -> None:
    api_key = os.environ.get("NANOBANANA_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: NANOBANANA_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    model_id = MODEL_IDS[model]

    full_prompt = f"Generate a square image (1:1 aspect ratio). {prompt}"

    if model == "pro":
        config = types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="1:1",
                image_size=size,
            ),
        )
        response = client.models.generate_content(
            model=model_id,
            contents=[full_prompt],
            config=config,
        )
    else:
        response = client.models.generate_content(
            model=model_id,
            contents=[full_prompt],
        )

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    for part in response.parts:
        if part.text is not None:
            print(f"Model note: {part.text}")
        elif part.inline_data is not None:
            raw_image = part.as_image()
            raw_image.save(output_path)
            print(f"Raw image saved to: {output_path}")

            # Remove background → transparent PNG
            print("Removing background...")
            from rembg import remove

            pil_image = Image.open(output_path).convert("RGBA")
            result = remove(pil_image)
            result.save(output_path)
            print(f"Transparent PNG saved to: {output_path}")
            return

    print("Error: No image data in response", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Can Mockup — generate label art from brand_identity.json")
    parser.add_argument("identity", help="Path to brand_identity.json")
    parser.add_argument("--model", choices=["flash", "pro"], default="flash", help="Gemini model (default: flash)")
    parser.add_argument("--size", choices=["1K", "2K", "4K"], default="1K", help="Resolution for pro model")
    parser.add_argument("--output", default=None, help="Override output path")
    args = parser.parse_args()

    identity = load_identity(args.identity)
    prompt = build_prompt(identity)

    out_dir = os.path.dirname(args.identity)
    out_path = args.output or os.path.join(out_dir, "label.png")

    print(f"Generating can label for: {identity.get('flavor', '???')}")
    generate_label(prompt, out_path, args.model, args.size)
    print("Done.")


if __name__ == "__main__":
    main()
