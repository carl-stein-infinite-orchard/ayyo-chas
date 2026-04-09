#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Stage 3: Approval — local web UI to review can art + brand identity.

Usage:
    uv run pipeline/approve.py posts/2026-04-10
    uv run pipeline/approve.py posts/2026-04-10 --port 8642

Opens a browser with the label preview and brand identity card.
Approve → writes approved.flag, triggers next pipeline stage.
Reject → deletes label, you re-run can_mockup.py.
"""

import argparse
import base64
import http.server
import json
import os
import sys
import threading
import webbrowser


def load_identity(post_dir: str) -> dict | None:
    path = os.path.join(post_dir, "brand_identity.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def load_image_b64(post_dir: str, filename: str = "label.png") -> str | None:
    path = os.path.join(post_dir, filename)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def build_html(post_dir: str) -> str:
    identity = load_identity(post_dir)
    image_b64 = load_image_b64(post_dir)
    approved = os.path.exists(os.path.join(post_dir, "approved.flag"))

    if not identity:
        return "<html><body><h1>No brand_identity.json found</h1><p>Run flavor_oracle.py first.</p></body></html>"

    flavor = identity.get("flavor", "???")
    category = identity.get("category", "???")
    tagline = identity.get("tagline", "")
    palette = identity.get("palette", {})
    ingredients = identity.get("fake_ingredients", [])
    disclaimer = identity.get("disclaimer", "")
    date = identity.get("date", "")
    primary = palette.get("primary", "#4A90D9")
    accent = palette.get("accent", "#F5A623")
    vibe = palette.get("vibe", "")

    cat_colors = {"interesting": "#1D9E75", "gross": "#E85D24", "impossible": "#7F77DD"}
    cat_color = cat_colors.get(category, "#888")
    cat_emoji = {"interesting": "&#129300;", "gross": "&#129326;", "impossible": "&#127744;"}

    img_block = ""
    if image_b64:
        img_block = f'<img src="data:image/png;base64,{image_b64}" class="label-img" />'
    else:
        img_block = '<div class="no-image">No label generated yet.<br>Run can_mockup.py first.</div>'

    status_block = ""
    if approved:
        status_block = '<div class="status approved">APPROVED</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Approve: {flavor}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Mono:wght@400;500&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Syne', system-ui, sans-serif;
    background: #0D0D0D;
    color: #E8E8E8;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    padding: 2rem;
  }}
  .container {{ max-width: 520px; width: 100%; }}
  .eyebrow {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #666;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 6px;
  }}
  .title {{
    font-size: 28px;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
  }}
  .title em {{ font-style: normal; color: {primary}; }}
  .tagline {{
    font-size: 14px;
    color: #888;
    margin-bottom: 1.5rem;
    font-style: italic;
  }}
  .category-badge {{
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 99px;
    color: {cat_color};
    border: 1px solid {cat_color}33;
    background: {cat_color}15;
    margin-bottom: 1.5rem;
  }}
  .label-img {{
    width: 100%;
    border-radius: 12px;
    border: 1px solid #222;
    margin-bottom: 1.5rem;
  }}
  .no-image {{
    width: 100%;
    aspect-ratio: 1;
    border-radius: 12px;
    border: 1px dashed #333;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: #555;
    font-size: 14px;
    margin-bottom: 1.5rem;
  }}
  .meta {{
    border: 1px solid #222;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 1.5rem;
    background: #141414;
  }}
  .meta-row {{
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    padding: 6px 0;
    border-bottom: 1px solid #1a1a1a;
    font-size: 13px;
  }}
  .meta-row:last-child {{ border-bottom: none; }}
  .meta-key {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #555;
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }}
  .meta-val {{ color: #bbb; text-align: right; max-width: 60%; }}
  .palette-swatch {{
    display: inline-block;
    width: 14px; height: 14px;
    border-radius: 3px;
    vertical-align: middle;
    margin-right: 4px;
    border: 1px solid #333;
  }}
  .ingredients {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: #666;
    line-height: 1.8;
    margin-bottom: 1.5rem;
    padding: 12px 16px;
    background: #111;
    border-radius: 8px;
    border: 1px solid #1a1a1a;
  }}
  .ingredients span {{ color: #888; }}
  .disclaimer {{
    font-size: 11px;
    color: #444;
    text-align: center;
    margin-bottom: 2rem;
    font-style: italic;
  }}
  .actions {{
    display: flex;
    gap: 10px;
  }}
  .btn {{
    flex: 1;
    padding: 14px;
    border: none;
    border-radius: 10px;
    font-family: 'Syne', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    transition: opacity 0.15s;
  }}
  .btn:hover {{ opacity: 0.85; }}
  .btn-approve {{ background: #1D9E75; color: #fff; }}
  .btn-reject {{ background: #E24B4A; color: #fff; }}
  .btn-regen {{ background: #222; color: #bbb; border: 1px solid #333; }}
  .status {{
    text-align: center;
    padding: 12px;
    border-radius: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.08em;
    margin-bottom: 1rem;
  }}
  .status.approved {{ background: #1D9E7520; color: #1D9E75; border: 1px solid #1D9E7540; }}
  .feedback {{ display: none; text-align: center; padding: 16px; font-size: 14px; color: #888; margin-top: 1rem; }}
</style>
</head>
<body>
<div class="container">
  <div class="eyebrow">Chas, U Drinkin This? &middot; {date}</div>
  <div class="title"><em>{flavor}</em></div>
  <div class="tagline">"{tagline}"</div>
  <div><span class="category-badge">{cat_emoji.get(category, '')} {category}</span></div>

  {status_block}
  {img_block}

  <div class="meta">
    <div class="meta-row"><span class="meta-key">Palette</span><span class="meta-val"><span class="palette-swatch" style="background:{primary}"></span>{primary} <span class="palette-swatch" style="background:{accent}"></span>{accent}</span></div>
    <div class="meta-row"><span class="meta-key">Vibe</span><span class="meta-val">{vibe}</span></div>
    <div class="meta-row"><span class="meta-key">Volume</span><span class="meta-val">{identity.get('volume_oz', 12)} oz</span></div>
  </div>

  <div class="ingredients">
    <span>Ingredients:</span> {", ".join(ingredients)}
  </div>

  <div class="disclaimer">{disclaimer}</div>

  <div class="actions">
    <button class="btn btn-approve" onclick="decide('approve')">Approve</button>
    <button class="btn btn-regen" onclick="decide('regen')">Regenerate</button>
    <button class="btn btn-reject" onclick="decide('reject')">Reject</button>
  </div>
  <div class="feedback" id="feedback"></div>
</div>
<script>
async function decide(action) {{
  const res = await fetch('/decide', {{
    method: 'POST',
    headers: {{'Content-Type': 'application/json'}},
    body: JSON.stringify({{action}})
  }});
  const data = await res.json();
  const fb = document.getElementById('feedback');
  fb.style.display = 'block';
  fb.textContent = data.message;
  if (action === 'approve') {{
    fb.style.color = '#1D9E75';
  }} else if (action === 'reject') {{
    fb.style.color = '#E24B4A';
  }} else {{
    fb.style.color = '#BA7517';
  }}
}}
</script>
</body>
</html>"""


class ApprovalHandler(http.server.BaseHTTPRequestHandler):
    post_dir: str = ""

    def log_message(self, format, *args):
        pass  # quiet

    def do_GET(self):
        html = build_html(self.post_dir)
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        if self.path == "/decide":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            action = body.get("action", "")

            msg = ""
            if action == "approve":
                flag_path = os.path.join(self.post_dir, "approved.flag")
                with open(flag_path, "w") as f:
                    f.write("approved")
                msg = "Approved. Run the next pipeline stage."
                print(f"\n>>> APPROVED — {flag_path}")
            elif action == "reject":
                label = os.path.join(self.post_dir, "label.png")
                if os.path.exists(label):
                    os.remove(label)
                msg = "Rejected. Label deleted. Re-run can_mockup.py."
                print("\n>>> REJECTED — label.png removed")
            elif action == "regen":
                msg = "Regenerate requested. Re-run can_mockup.py with a new seed."
                print("\n>>> REGEN requested")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"action": action, "message": msg}).encode())
            return

        self.send_response(404)
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description="Approval UI — review can art before video production")
    parser.add_argument("post_dir", help="Path to the post directory (e.g. posts/2026-04-10)")
    parser.add_argument("--port", type=int, default=8642, help="Port (default: 8642)")
    parser.add_argument("--no-open", action="store_true", help="Don't auto-open browser")
    args = parser.parse_args()

    post_dir = os.path.abspath(args.post_dir)
    if not os.path.isdir(post_dir):
        print(f"Error: {post_dir} is not a directory", file=sys.stderr)
        sys.exit(1)

    ApprovalHandler.post_dir = post_dir

    server = http.server.HTTPServer(("127.0.0.1", args.port), ApprovalHandler)
    url = f"http://localhost:{args.port}"
    print(f"Approval UI running at {url}")
    print(f"Reviewing: {post_dir}")
    print("Press Ctrl+C to stop.\n")

    if not args.no_open:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
