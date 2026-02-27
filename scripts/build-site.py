#!/usr/bin/env python3
"""Build UK Farm Blog with GitHub Pages compatible absolute links"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False

PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"
OUTPUT_DIR = PROJECT_ROOT / "_site"
DATA_DIR = PROJECT_ROOT / "data"

# GitHub Pages path - MUST include /Nole prefix
BASE_PATH = "/Nole"

SECTIONS = [
    ("daily-brief", "🗞 Daily Farm Brief", "Daily farming updates"),
    ("weather", "🌦 Weather Alerts", "Weather risks & forecasts"),
    ("grants", "💰 Grants & Funding", "Available grants & deadlines"),
    ("markets", "📈 Market Prices", "Livestock & commodity prices"),
    ("equipment", "🚜 Equipment", "Machinery & tech updates"),
    ("livestock", "🐄 Livestock", "Animal health & markets"),
    ("crops", "🌾 Crops", "Crop management & agronomy"),
    ("seasonal", "📅 Seasonal Tasks", "Monthly farming checklists"),
    ("tools", "📊 Tools", "Calculators & resources"),
    ("community", "👥 Community", "Ask questions, share stories"),
]

def md_to_html(text):
    if MARKDOWN_AVAILABLE:
        md = markdown.Markdown(extensions=['tables', 'fenced_code'])
        return md.convert(text)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return text

def get_content(file_path):
    path = PROJECT_ROOT / file_path
    if path.exists():
        content = path.read_text()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    return ""

def get_icon(section_id):
    icons = {"daily-brief": "📰", "weather": "🌦", "grants": "💰", "markets": "📈", 
             "equipment": "🚜", "livestock": "🐄", "crops": "🌾", "seasonal": "📅", 
             "tools": "🧰", "community": "👥"}
    return icons.get(section_id, "📋")

def get_gradient(section_id):
    return "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

COMMON_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; color: #333; line-height: 1.7; }
header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 60px 20px; text-align: center; }
header h1 { font-size: 2.5em; margin-bottom: 10px; }
nav { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 15px; text-align: center; position: sticky; top: 0; z-index: 100; }
nav a { color: white; text-decoration: none; margin: 0 8px; padding: 8px 16px; border-radius: 20px; transition: all 0.3s; }
nav a:hover { background: rgba(255,255,255,0.2); }
main { max-width: 1300px; margin: 0 auto; padding: 40px 20px; }
.hero { background: linear-gradient(135deg, #2d5a27 0%, #4a7c43 100%); color: white; padding: 40px; border-radius: 20px; margin-bottom: 50px; }
.btn { display: inline-block; background: #ffd700; color: #1e3c72; padding: 14px 28px; text-decoration: none; border-radius: 30px; font-weight: 600; margin-top: 20px; }
.section-card { background: white; border-radius: 16px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: all 0.3s; }
.section-card:hover { transform: translateY(-5px); }
.sections-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 24px; }
.card-btn { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; text-decoration: none; border-radius: 20px; }
.content-page { background: white; border-radius: 20px; padding: 50px; max-width: 900px; margin: 40px auto; box-shadow: 0 4px 30px rgba(0,0,0,0.1); }
.content-page h1 { color: #1e3c72; font-size: 2.5em; margin-bottom: 30px; border-bottom: 3px solid #eee; padding-bottom: 20px; }
.content-page h2 { color: #2d5a27; margin: 40px 0 20px; padding-left: 15px; border-left: 4px solid #ffd700; }
footer { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; text-align: center; padding: 50px 20px; margin-top: 80px; }
"""

def build_homepage():
    brief_content = get_content("content/daily-brief.md")[:600]
    
    # Navigation with absolute paths
    nav_links = ' '.join(f'<a href="{BASE_PATH}/{sid}/">{get_icon(sid)} {stitle.split(" ", 1)[1]}</a>' for sid, stitle, _ in SECTIONS)
    
    cards_html = ""
    for section_id, title, desc in SECTIONS:
        cards_html += f'<div class="section-card"><h3>{title}</h3><p>{desc}</p><a href="{BASE_PATH}/{section_id}/" class="card-btn">Explore →</a></div>'
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UK Farm Blog - Daily Farming Updates</title>
    <style>{COMMON_CSS}</style>
</head>
<body>
    <header>
        <h1>🌾 UK Farm Blog</h1>
        <p>Daily updates for British farmers</p>
    </header>
    <nav>
        {nav_links}
    </nav>
    <main>
        <div class="hero">
            <h2>📰 Today's Farm Brief</h2>
            {md_to_html(brief_content)}
            <a href="{BASE_PATH}/daily-brief/" class="btn">Read Full Brief →</a>
        </div>
        <h2 style="color: #1e3c72; margin-bottom: 30px;">📂 Browse Sections</h2>
        <div class="sections-grid">
            {cards_html}
        </div>
    </main>
    <footer>
        <p>🚜 UK Farm Blog - Updated {datetime.now().strftime('%d %B %Y')}</p>
    </footer>
</body>
</html>"""

def build_section_page(section_id, title, desc):
    # Get content
    content = ""
    for path in [f"content/{section_id}/latest.md", f"content/{section_id}/index.md", f"content/{section_id}.md"]:
        if (PROJECT_ROOT / path).exists():
            content = get_content(path)
            break

    if not content:
        content = f"<p>{title} content coming soon!</p>"

    # Navigation - ALL absolute paths with BASE_PATH
    nav_links = f'<a href="{BASE_PATH}/">🏠 Home</a>'
    for sid, stitle, _ in SECTIONS:
        label = stitle.split(" ", 1)[1] if sid != section_id else f"<strong>{stitle.split(' ', 1)[1]}</strong>"
        nav_links += f' <a href="{BASE_PATH}/{sid}/">{label}</a>'
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - UK Farm Blog</title>
    <style>{COMMON_CSS}</style>
</head>
<body>
    <header>
        <h1>{get_icon(section_id)} {title}</h1>
        <p>{desc}</p>
    </header>
    <nav>
        {nav_links}
    </nav>
    <main>
        <article class="content-page">
            {md_to_html(content)}
            <p style="text-align: center; margin-top: 40px;">
                <a href="{BASE_PATH}/" class="btn">← Back to Home</a>
            </p>
        </article>
    </main>
    <footer>
        <p>🚜 UK Farm Blog - {title}</p>
    </footer>
</body>
</html>"""

def main():
    print("🔨 Building UK Farm Blog v3.0...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Homepage
    (OUTPUT_DIR / "index.html").write_text(build_homepage())
    print("✅ Homepage")
    
    # Section pages
    for section_id, title, desc in SECTIONS:
        section_dir = OUTPUT_DIR / section_id
        section_dir.mkdir(exist_ok=True)
        (section_dir / "index.html").write_text(build_section_page(section_id, title, desc))
        print(f"  ✅ {title}")
    
    # Copy tools (update links)
    tools_src = PROJECT_ROOT / "content" / "tools"
    if tools_src.exists():
        tools_dir = OUTPUT_DIR / "tools"
        tools_dir.mkdir(exist_ok=True)
        for html_file in tools_src.glob("*.html"):
            content = html_file.read_text()
            # Update any links to use BASE_PATH
            content = content.replace('href="/', f'href="{BASE_PATH}/')
            content = content.replace('href="./', f'href="{BASE_PATH}/')
            (tools_dir / html_file.name).write_text(content)
            print(f"  ✅ Tool: {html_file.name}")
    
    # Copy community (update links)
    community_src = PROJECT_ROOT / "content" / "community"
    if community_src.exists():
        community_dir = OUTPUT_DIR / "community"
        community_dir.mkdir(exist_ok=True)
        for f in community_src.glob("*.html"):
            content = f.read_text()
            content = content.replace('href="/', f'href="{BASE_PATH}/')
            content = content.replace('href="./', f'href="{BASE_PATH}/')
            (community_dir / f.name).write_text(content)
            print(f"  ✅ Community: {f.name}")
    
    print(f"\n📁 Built in {OUTPUT_DIR}")
    print(f"   Using base path: {BASE_PATH}")
    print("🚀 Ready to deploy!")

if __name__ == "__main__":
    main()