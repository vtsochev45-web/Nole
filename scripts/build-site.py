#!/usr/bin/env python3
"""Build UK Farm Blog with GitHub Pages compatible links"""

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

# Base URL for GitHub Pages
BASE_URL = "https://vtsochev45-web.github.io/Nole"

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
    """Convert markdown to HTML"""
    if MARKDOWN_AVAILABLE:
        md = markdown.Markdown(extensions=['tables', 'fenced_code'])
        return md.convert(text)
    
    # Basic fallback
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    text = re.sub(r'\n\n', '</p><p>', text)
    text = '<p>' + text + '</p>'
    return text

def get_content(file_path):
    """Load content from markdown file"""
    path = PROJECT_ROOT / file_path
    if path.exists():
        content = path.read_text()
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    return ""

def get_card_summary(section_id):
    """Generate a card summary"""
    data_file = DATA_DIR / f"{section_id}.json"
    if data_file.exists():
        try:
            data = json.loads(data_file.read_text())
            if section_id == "weather" and "alerts" in data:
                return f"{len(data['alerts'])} alerts"
        except:
            pass
    content = get_content(f"content/{section_id}.md")
    if content:
        lines = [l.strip() for l in content.split('\n') if l.strip() and not l.startswith('#')]
        return lines[0][:80] + "..." if lines else "View →"
    return "Explore →"

def get_gradient(section_id):
    gradients = {
        "daily-brief": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "weather": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "grants": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "markets": "linear-gradient(135deg, #30cfd0 0%, #330867 100%)",
        "equipment": "linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)",
        "livestock": "linear-gradient(135deg, #ff9a9e 0%, #fecfef 99%)",
        "crops": "linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)",
        "seasonal": "linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)",
        "tools": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
    }
    return gradients.get(section_id, "linear-gradient(135deg, #667eea 0%, #764ba2 100%)")

def get_icon(section_id):
    icons = {
        "daily-brief": "📰", "weather": "🌦", "grants": "💰",
        "markets": "📈", "equipment": "🚜", "livestock": "🐄",
        "crops": "🌾", "seasonal": "📅", "tools": "🧰",
    }
    return icons.get(section_id, "📋")

# Simplified CSS
COMMON_CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: 100vh; color: #333; line-height: 1.7; }
header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 60px 20px; text-align: center; }
header h1 { font-size: 2.5em; margin-bottom: 10px; }
header p { font-size: 1.2em; opacity: 0.9; max-width: 600px; margin: 0 auto; }
nav { background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 15px; text-align: center; position: sticky; top: 0; z-index: 100; }
nav a { color: white; text-decoration: none; margin: 0 10px; padding: 8px 16px; border-radius: 20px; transition: all 0.3s; }
nav a:hover { background: rgba(255,255,255,0.2); }
main { max-width: 1300px; margin: 0 auto; padding: 40px 20px; }
.hero { background: linear-gradient(135deg, #2d5a27 0%, #4a7c43 100%); color: white; padding: 40px; border-radius: 20px; margin-bottom: 50px; box-shadow: 0 10px 40px rgba(45,90,39,0.3); }
.hero h2 { font-size: 2em; margin-bottom: 20px; }
.hero-content { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 12px; margin: 20px 0; border-left: 4px solid #ffd700; }
.btn { display: inline-block; background: #ffd700; color: #1e3c72; padding: 14px 28px; text-decoration: none; border-radius: 30px; font-weight: 600; margin-top: 20px; transition: all 0.3s; }
.btn:hover { transform: translateY(-3px); box-shadow: 0 6px 20px rgba(255,215,0,0.4); }
.section-heading { font-size: 1.8em; color: #1e3c72; margin-bottom: 30px; }
.sections-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px; margin-bottom: 50px; }
.section-card { background: white; border-radius: 16px; padding: 30px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); transition: all 0.3s; }
.section-card:hover { transform: translateY(-5px); box-shadow: 0 8px 30px rgba(0,0,0,0.12); }
.section-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 5px; background: var(--card-gradient); border-radius: 16px 16px 0 0; }
.section-card-icon { font-size: 3em; margin-bottom: 15px; }
.section-card h3 { color: #1e3c72; margin-bottom: 10px; font-size: 1.4em; }
.card-btn { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 10px 20px; text-decoration: none; border-radius: 20px; font-size: 0.9em; font-weight: 500; }
.content-page { background: white; border-radius: 20px; padding: 50px; max-width: 900px; margin: 40px auto; box-shadow: 0 4px 30px rgba(0,0,0,0.1); }
.content-page h1 { color: #1e3c72; font-size: 2.5em; margin-bottom: 30px; border-bottom: 3px solid #eee; padding-bottom: 20px; }
.content-page h2 { color: #2d5a27; margin: 40px 0 20px; padding-left: 15px; border-left: 4px solid #ffd700; font-size: 1.6em; }
.content-page table { width: 100%; border-collapse: collapse; margin: 25px 0; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
.content-page th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: left; }
.content-page td { padding: 15px; border-bottom: 1px solid #eee; }
.content-page tr:nth-child(even) { background: #f8f9fa; }
footer { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; text-align: center; padding: 50px 20px; margin-top: 80px; }
.updated { font-size: 0.9em; opacity: 0.7; }
@media (max-width: 768px) { header h1 { font-size: 2em; } .sections-grid { grid-template-columns: 1fr; } .content-page { padding: 25px; } }
"""

def build_homepage():
    """Build the main homepage"""
    brief_content = get_content("content/daily-brief.md")[:600]
    
    cards_html = ""
    for section_id, title, desc in SECTIONS:
        gradient = get_gradient(section_id)
        icon = get_icon(section_id)
        summary = get_card_summary(section_id)
        # Use relative links for GitHub Pages compatibility
        cards_html += f'''
        <div class="section-card" style="--card-gradient: {gradient}; position: relative;">
            <div class="section-card-icon">{icon}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
            <p style="font-size: 0.85em; color: #888; margin: 10px 0;">{summary}</p>
            <a href="./{section_id}/" class="card-btn">Explore →</a>
        </div>
        '''
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UK Farm Blog - Daily Farming Updates</title>
    <meta name="description" content="Daily updates for British farmers: weather, grants, market prices, and seasonal advice.">
    <base href="{BASE_URL}/">
    <style>{COMMON_CSS}</style>
</head>
<body>
    <header>
        <h1>🌾 UK Farm Blog</h1>
        <p>Daily updates, weather alerts, grants, and market prices for British farmers</p>
    </header>
    <nav>
        <a href="./">🏠 Home</a>
        <a href="./daily-brief/">📰 Daily Brief</a>
        <a href="./weather/">🌦 Weather</a>
        <a href="./markets/">📈 Markets</a>
        <a href="./grants/">💰 Grants</a>
        <a href="./tools/">🧰 Tools</a>
    </nav>
    <main>
        <div class="hero">
            <h2>📰 Today's Farm Brief</h2>
            <div class="hero-content">
                {md_to_html(brief_content)}
            </div>
            <a href="./daily-brief/" class="btn">Read Full Brief →</a>
        </div>
        <h2 class="section-heading">📂 Browse Sections</h2>
        <div class="sections-grid">
            {cards_html}
        </div>
    </main>
    <footer>
        <p>🚜 UK Farm Blog - Your daily farming companion</p>
        <p>Weather • Grants • Markets • Equipment • Livestock • Crops</p>
        <p class="updated">Last updated: {datetime.now().strftime('%d %B %Y at %H:%M UTC')}</p>
    </footer>
</body>
</html>"""
    return html

def build_section_page(section_id, title, desc):
    """Build a section page"""
    content_paths = [
        f"content/{section_id}/latest.md",
        f"content/{section_id}.md",
        f"content/{section_id}/index.md",
    ]
    
    content = ""
    for path in content_paths:
        if (PROJECT_ROOT / path).exists():
            content = get_content(path)
            break
    
    if not content:
        content = f"<p>New {title.lower()} content coming soon. Check back tomorrow!</p>"
    
    # Build relative navigation
    nav_links = '<a href="../">🏠 Home</a>'
    for sid, stitle, _ in SECTIONS:
        if sid == section_id:
            continue
        nav_links += f' <a href="../{sid}/">{get_icon(sid)} {stitle.split(" ", 1)[1]}</a>'
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - UK Farm Blog</title>
    <base href="{BASE_URL}/">
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
                <a href="../" class="btn">← Back to Home</a>
            </p>
        </article>
    </main>
    <footer>
        <p>🚜 UK Farm Blog - {title}</p>
        <p class="updated">Last updated: {datetime.now().strftime('%d %B %Y at %H:%M UTC')}</p>
    </footer>
</body>
</html>"""
    return html

def main():
    print("🔨 Building UK Farm Blog...")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Build homepage
    homepage = build_homepage()
    (OUTPUT_DIR / "index.html").write_text(homepage)
    print("✅ Homepage built")
    
    # Build section pages
    for section_id, title, desc in SECTIONS:
        section_dir = OUTPUT_DIR / section_id
        section_dir.mkdir(exist_ok=True)
        page = build_section_page(section_id, title, desc)
        (section_dir / "index.html").write_text(page)
        print(f"  ✅ {title}")
    
    # Copy interactive tools
    tools_src = PROJECT_ROOT / "content" / "tools"
    if tools_src.exists():
        tools_dir = OUTPUT_DIR / "tools"
        for html_file in tools_src.glob("*.html"):
            dest = tools_dir / html_file.name
            content = html_file.read_text()
            # Inject base tag if not present
            if '<base' not in content:
                content = content.replace('<head>', f'<head>\n    <base href="{BASE_URL}/">')
            dest.write_text(content)
            print(f"  ✅ Tool: {html_file.name}")
    
    # Copy community features
    community_src = PROJECT_ROOT / "content" / "community"
    if community_src.exists():
        community_dir = OUTPUT_DIR / "community"
        community_dir.mkdir(exist_ok=True)
        
        # Copy HTML files with base tag injection
        for html_file in community_src.glob("*.html"):
            dest = community_dir / html_file.name
            content = html_file.read_text()
            # Inject base tag if not present
            if '<base' not in content:
                content = content.replace('<head>', f'<head>\n    <base href="{BASE_URL}/">')
            dest.write_text(content)
            print(f"  ✅ Community: {html_file.name}")
        
        # Convert markdown to HTML
        for md_file in community_src.glob("*.md"):
            content = md_file.read_text()
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    content = parts[2].strip()
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Community - UK Farm Blog</title>
    <base href="{BASE_URL}/">
    <style>{COMMON_CSS}</style>
</head>
<body>
    <header>
        <h1>🌾 Community Hub</h1>
        <p>Connect with fellow UK farmers</p>
    </header>
    <nav>
        <a href="../">🏠 Home</a>
        <a href="./ask-question.html">❓ Ask Question</a>
        <a href="./share-story.html">📖 Share Story</a>
        <a href="./utility-tracker.html">💰 Value Tracker</a>
    </nav>
    <main>
        <article class="content-page">
            {md_to_html(content)}
            <p style="text-align: center; margin-top: 40px;">
                <a href="../" class="btn">← Back to Home</a>
            </p>
        </article>
    </main>
    <footer>
        <p>🚜 UK Farm Blog - Community</p>
        <p class="updated">Last updated: {datetime.now().strftime('%d %B %Y at %H:%M UTC')}</p>
    </footer>
</body>
</html>"""
            dest = community_dir / (md_file.stem + ".html")
            dest.write_text(html_content)
            print(f"  ✅ Community: {md_file.stem}.html")
    
    print(f"\n📁 Site built in {OUTPUT_DIR}")
    print(f"   Sections: {len(SECTIONS) + 1} pages")
    print(f"   Base URL: {BASE_URL}")
    print("\n🚀 Ready to deploy!")

if __name__ == "__main__":
    main()
