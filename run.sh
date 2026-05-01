#!/bin/bash
# Ayyo Chas, U Drinkin This? — full daily pipeline
#
# Usage:
#   ./run.sh                        # today, random category, auto-approve
#   ./run.sh --date 2026-04-13      # specific date
#   ./run.sh --category gross       # force category
#   ./run.sh --approve              # pause for manual approval before render
#
# By default: generates flavor → generates can → renders video. No stops.
# With --approve: opens approval UI between can gen and render.

set -e
cd "$(dirname "$0")"

# Defaults
DATE=$(date +%Y-%m-%d)
CATEGORY=""
MANUAL_APPROVE=false

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --date) DATE="$2"; shift 2 ;;
    --category) CATEGORY="$2"; shift 2 ;;
    --approve) MANUAL_APPROVE=true; shift ;;
    *) echo "Unknown arg: $1"; exit 1 ;;
  esac
done

# Load keys
export OPENAI_API_KEY=$(grep '^OPENAI_API_KEY=' /Users/cstein/io/.credentials | cut -d= -f2)
export NANOBANANA_API_KEY=$(grep '^NANOBANANA_API_KEY=' /Users/cstein/io/.credentials | cut -d= -f2)

CATEGORY_FLAG=""
[ -n "$CATEGORY" ] && CATEGORY_FLAG="--category $CATEGORY"

echo "╔══════════════════════════════════════╗"
echo "║  AYYO CHAS, U DRINKIN THIS?         ║"
echo "║  Date: $DATE                    ║"
echo "╚══════════════════════════════════════╝"
echo ""

# 1. Flavor
echo "▸ 1/3 FLAVOR ORACLE"
uv run pipeline/flavor_oracle.py --date "$DATE" $CATEGORY_FLAG
echo ""

# 2. Can
echo "▸ 2/3 CAN MOCKUP"
uv run pipeline/can_mockup.py "posts/$DATE/brand_identity.json"
echo ""

# 3. Approve (manual or auto)
if [ "$MANUAL_APPROVE" = true ]; then
  echo "▸ APPROVAL — review at http://localhost:8642"
  echo "  Press Ctrl+C after approving to continue to render."
  uv run pipeline/approve.py "posts/$DATE"
else
  # Auto-approve
  mkdir -p "posts/$DATE"
  echo "approved" > "posts/$DATE/approved.flag"
  echo "▸ Auto-approved"
fi
echo ""

# 4. Render
echo "▸ 3/3 RENDER VIDEO"
uv run pipeline/render_video.py "posts/$DATE"

echo ""
echo "════════════════════════════════════════"
# render_video.py renames posts/$DATE → posts/$DATE-<slug>, so find the actual folder
POST_DIR=$(ls -d posts/${DATE}-* 2>/dev/null | head -1)
[ -z "$POST_DIR" ] && POST_DIR="posts/$DATE"
FLAVOR=$(python3 -c "import json; print(json.load(open('$POST_DIR/brand_identity.json'))['flavor'])")
echo "✓ $FLAVOR"
echo "  Video: $(ls "$POST_DIR"/video_*.mp4 2>/dev/null | head -1)"
echo "  Caption: ayyo chas, u drinkin this?"
echo ""
python3 -c "
import json
d = json.load(open('$POST_DIR/brand_identity.json'))
songs = d.get('song_picks', [])
if songs:
    print('  Song picks:')
    for i, s in enumerate(songs, 1):
        print(f'    {i}. {s}')
"
echo "════════════════════════════════════════"
