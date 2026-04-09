#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "openai",
# ]
# ///
"""
Stage 1: Flavor Oracle — GPT-4o generates a daily brand_identity.json.

Usage:
    uv run pipeline/flavor_oracle.py
    uv run pipeline/flavor_oracle.py --date 2026-04-10
    uv run pipeline/flavor_oracle.py --category gross
"""

import argparse
import json
import os
import sys
from datetime import date

from openai import OpenAI

SYSTEM_PROMPT = """\
You are the flavor oracle for "Ayyo Chas, U Drinkin This?" — a novelty seltzer brand that invents one fake flavor per day.

Each flavor falls into exactly one category:
- **interesting**: Flavors that sound weird but you'd genuinely try (boysenberry, honeydew jalapeno, earl grey lavender)
- **gross**: Flavors that make people gag (broccoli & cheese, chicken wing, gym sock & lime)
- **impossible**: Flavors that aren't even flavors — abstract concepts, vibes, sensations (yacht rock, tuesday afternoon, the color beige)

Generate ONE new flavor. Return valid JSON matching this exact schema — no markdown, no explanation, just the JSON object:

{
  "flavor": "string — the flavor name, title case",
  "category": "interesting | gross | impossible",
  "tagline": "string — short, punchy, 2-6 words. Be provocative, a little unhinged, lowkey vulgar or inappropriate. Think things a drunk friend would yell. Examples: 'your ex can't afford this', 'smells like a decision', 'absolutely not FDA approved', 'do not operate heavy machinery'. PG-13 vulgar, not explicit.",
  "fake_ingredients": ["carbonated water", "natural flavors", "citric acid", "one or two absurd joke ingredients with asterisks"],
  "palette": {
    "primary": "#hex — dominant label color",
    "accent": "#hex — secondary color",
    "vibe": "string — 2-4 word aesthetic descriptor like 'retro-diner-grease' or 'zen-garden-mist'"
  },
  "image_prompt": "string — a short visual direction note (under 50 words) describing the label design style, key visual motifs, and mood for this specific flavor. Do NOT describe the can itself or the background — just the label artwork vibe and elements. Example: 'retro athletic stripes, cartoon gym sock mascot, lime wedge accents, bold block letters, slightly gross but charming'",
  "volume_oz": 12,
  "limited_edition": false,
  "disclaimer": "string — a short funny fake legal disclaimer",
  "testimonial": {
    "quote": "string — a fake 1-sentence review. Unhinged, slightly vulgar, sounds like a real review written by someone having a crisis. Examples: 'I showed this to my therapist and she quit.' / 'My body said no but I kept going.' / 'I've made worse decisions but not many.' / 'Tastes like calling your ex at 2am.' Go hard.",
    "author": "string — a fake name with an absurd credential. Examples: 'Dr. Brenda Coolidge, DDS' / 'Kyle M., registered sex offender (unrelated)' / 'Janet, 3 stars on Yelp' / 'Some guy at a gas station'"
  },
  "video_mood": {
    "energy": "explosive | smooth | unhinged | ethereal — pick the one that fits the flavor's personality. 'explosive' = thunderbolt cucumber, monster truck energy. 'smooth' = boysenberry cheesecake, cottage-core lovely. 'unhinged' = gym sock & lime, chaotic meme energy. 'ethereal' = the color beige, dreamy and existential.",
    "bg_tone": "#hex — a dark or muted background color that sets the mood. NOT black. Think: deep navy for electric, dusty rose for soft, toxic green for gross, muted lavender for dreamy."
  },
  "song_picks": [
    "string — 3 real, popular songs (artist - title) that match the flavor's vibe and would work as background audio for a 12-second Instagram Reel. Think about the energy, mood, and cultural associations. Pick songs people actually know — trending tracks, iconic bangers, or cult favorites. Mix it up: one safe pick, one hype pick, one wildcard. Format: 'Artist - Song Title'"
  ]
}

Rules:
- Be genuinely creative. No basic combos. Surprise people.
- The tagline should be provocative, unhinged, or lowkey vulgar. Make people screenshot it. Not try-hard edgy — more like drunk-friend-energy.
- fake_ingredients should start with real seltzer ingredients then get weird.
- The testimonial should be unhinged. Sounds like a real review at first, then goes off the rails. Make it quotable.
- image_prompt must be specific enough to generate consistent, compositable label art.
- song_picks should be 3 REAL songs that exist. Match the flavor's energy. One crowd-pleaser, one that goes hard, one weird/perfect pick.
- video_mood.energy should genuinely match the flavor. A delicate flavor should NOT be explosive. A disgusting flavor should probably be unhinged. An abstract flavor should be ethereal. Let the flavor drive the vibe.
- NEVER repeat a flavor you've seen before. Each day is unique.
"""


def generate_flavor(category: str | None = None) -> dict:
    client = OpenAI()

    user_msg = "Generate today's flavor."
    if category:
        user_msg = f"Generate today's flavor. It MUST be in the '{category}' category."

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=1.1,
        max_tokens=800,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def main():
    parser = argparse.ArgumentParser(description="Flavor Oracle — generate a daily brand_identity.json")
    parser.add_argument("--date", default=date.today().isoformat(), help="Date folder name (default: today)")
    parser.add_argument("--category", choices=["interesting", "gross", "impossible"], help="Force a specific category")
    parser.add_argument("--output-dir", default=None, help="Override output directory")
    args = parser.parse_args()

    if not os.environ.get("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    out_dir = args.output_dir or os.path.join(os.path.dirname(__file__), "..", "posts", args.date)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "brand_identity.json")

    print(f"Generating flavor for {args.date}...")
    identity = generate_flavor(args.category)
    identity["date"] = args.date

    with open(out_path, "w") as f:
        json.dump(identity, f, indent=2)

    print(f"Flavor: {identity['flavor']} ({identity['category']})")
    print(f"Tagline: {identity['tagline']}")
    print(f"Saved to: {out_path}")


if __name__ == "__main__":
    main()
