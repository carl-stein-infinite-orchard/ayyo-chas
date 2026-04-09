#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Stage 4: Render — reads brand_identity.json, writes Root.tsx props, copies can, renders video.

Usage:
    uv run pipeline/render_video.py posts/2026-04-10
    uv run pipeline/render_video.py posts/2026-04-10 --skip-check
"""

import argparse
import json
import os
import shutil
import subprocess
import sys


def load_identity(post_dir: str) -> dict:
    path = os.path.join(post_dir, "brand_identity.json")
    if not os.path.exists(path):
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def json_str(s: str) -> str:
    """Escape a string for safe inclusion in JS/TS."""
    return json.dumps(s)


def write_root_tsx(identity: dict, video_dir: str) -> None:
    flavor = identity["flavor"]
    tagline = identity.get("tagline", "")
    ingredients = identity.get("fake_ingredients", [])
    palette = identity.get("palette", {})
    disclaimer = identity.get("disclaimer", "")
    testimonial = identity.get("testimonial", {})
    video_mood = identity.get("video_mood", {"energy": "explosive", "bg_tone": "#0A0A0A"})

    # Build ingredient array
    ingredients_ts = ",\n    ".join(json_str(i) for i in ingredients)

    root_tsx = f'''import {{ Composition }} from "remotion";
import {{ ChasVideo }} from "./ChasVideo";

const defaultProps = {{
  flavor: {json_str(flavor)},
  tagline: {json_str(tagline)},
  fakeIngredients: [
    {ingredients_ts},
  ],
  palette: {{
    primary: {json_str(palette.get("primary", "#4A90D9"))},
    accent: {json_str(palette.get("accent", "#F5A623"))},
  }},
  disclaimer: {json_str(disclaimer)},
  testimonial: {{
    quote: {json_str(testimonial.get("quote", "No comment."))},
    author: {json_str(testimonial.get("author", "Anonymous"))},
  }},
  videoMood: {{
    energy: {json_str(video_mood.get("energy", "explosive"))} as const,
    bgTone: {json_str(darken_bg(video_mood.get("bg_tone", "#0A0A0A")))},
  }},
  canImageSrc: "assets/label.png",
}};

export const Root: React.FC = () => {{
  return (
    <Composition
      id="ChasVideo"
      component={{ChasVideo}}
      durationInFrames={{400}}
      fps={{30}}
      width={{1080}}
      height={{1920}}
      defaultProps={{defaultProps}}
    />
  );
}};
'''

    out_path = os.path.join(video_dir, "src", "Root.tsx")
    with open(out_path, "w") as f:
        f.write(root_tsx)
    print(f"Root.tsx written: {out_path}")


def darken_bg(hex_color: str) -> str:
    """Ensure bg_tone is dark enough for video backgrounds."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return "#0A0A0A"
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    if luminance > 0.25:
        # Too bright — darken it
        factor = 0.15 / max(luminance, 0.01)
        r = int(min(r * factor, 255))
        g = int(min(g * factor, 255))
        b = int(min(b * factor, 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def main():
    parser = argparse.ArgumentParser(description="Render video from brand_identity.json")
    parser.add_argument("post_dir", help="Path to the post directory (e.g. posts/2026-04-10)")
    parser.add_argument("--skip-check", action="store_true", help="Skip approval check")
    args = parser.parse_args()

    post_dir = os.path.abspath(args.post_dir)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    video_dir = os.path.join(project_root, "video")

    # Check approval
    if not args.skip_check:
        flag = os.path.join(post_dir, "approved.flag")
        if not os.path.exists(flag):
            print("Warning: Not approved yet. Use --skip-check to override.", file=sys.stderr)
            print("Run: uv run pipeline/approve.py " + args.post_dir, file=sys.stderr)
            sys.exit(1)

    # Load identity
    identity = load_identity(post_dir)
    flavor = identity.get("flavor", "unknown")
    print(f"Rendering: {flavor}")

    # Copy can image
    label_src = os.path.join(post_dir, "label.png")
    label_dst = os.path.join(video_dir, "public", "assets", "label.png")
    if not os.path.exists(label_src):
        print(f"Error: {label_src} not found", file=sys.stderr)
        sys.exit(1)
    shutil.copy2(label_src, label_dst)
    print(f"Can image copied to: {label_dst}")

    # Write Root.tsx
    write_root_tsx(identity, video_dir)

    # Render
    flavor_slug = flavor.lower().replace(" ", "-").replace("&", "and").replace("'", "")
    date = identity.get("date", "unknown")
    folder_name = f"{date}-{flavor_slug}"
    out_name = f"video_{flavor_slug}"

    # Rename post dir to date-flavor format
    new_post_dir = os.path.join(os.path.dirname(post_dir), folder_name)
    if os.path.abspath(post_dir) != os.path.abspath(new_post_dir):
        os.rename(post_dir, new_post_dir)
        post_dir = new_post_dir
        print(f"Post folder: {post_dir}")

    # Temp render path, final lives in post dir
    tmp_out = os.path.join(video_dir, "out", f"{out_name}.mp4")
    post_video = os.path.join(post_dir, f"{out_name}.mp4")

    print(f"Rendering video...")
    result = subprocess.run(
        ["npx", "remotion", "render", "ChasVideo", tmp_out, "--image-format", "png", "--crf", "18"],
        cwd=video_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print("Render failed:", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)

    # Move to post dir
    shutil.move(tmp_out, post_video)

    # Write post markdown
    songs = identity.get("song_picks", [])
    tagline = identity.get("tagline", "")
    testimonial = identity.get("testimonial", {})
    disclaimer = identity.get("disclaimer", "")
    mood = identity.get("video_mood", {}).get("energy", "?")
    date = identity.get("date", "")

    md_lines = [
        f"# {flavor}",
        f"",
        f"**Caption:** ayyo chas, u drinkin this?",
        f"",
        f"**Tagline:** {tagline}",
        f"**Mood:** {mood}",
        f"**Disclaimer:** {disclaimer}",
        f"",
    ]

    if songs:
        md_lines.append("## Song Picks")
        md_lines.append("")
        for i, song in enumerate(songs, 1):
            md_lines.append(f"{i}. {song}")
        md_lines.append("")

    if testimonial:
        md_lines.append(f'> "{testimonial.get("quote", "")}"')
        md_lines.append(f'> — {testimonial.get("author", "")}')
        md_lines.append("")

    md_path = os.path.join(post_dir, "post.md")
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines))

    # Clean up intermediate files
    for f in ["brand_identity.json", "label.png", "approved.flag"]:
        p = os.path.join(post_dir, f)
        if os.path.exists(p):
            os.remove(p)


    print(f"\nDone!")
    print(f"  Video: {post_video}")
    print(f"  Post:  {md_path}")
    print(f"  Flavor: {flavor} ({mood})")

    if songs:
        print(f"\n  Song picks:")
        for i, song in enumerate(songs, 1):
            print(f"    {i}. {song}")


if __name__ == "__main__":
    main()
