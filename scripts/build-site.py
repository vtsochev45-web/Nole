#!/usr/bin/env python3
"""Build UK Farm Blog with proper section structure"""

import os
import json
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
CONTENT_DIR = PROJECT_ROOT / "content"
OUTPUT_DIR = PROJECT_ROOT / "_site"

SECTIONS = [
    ("daily-brief", "🗞 Daily Farm Brief", "content/daily-brief.md"),
    ("weather", "🌦 Weather + Risk Alerts", "content/weather/latest.md"),
    ("grants", "💰 Grants & Money Updates", "content/grants/latest.md"),
    ("markets", "📈 Market Prices", "content/markets/latest.md"),
    ("equipment", "🚜 Equipment & Tech", "content/equipment/latest.md"),
    ("livestock", "🐄 Livestock", "content/livestock/latest.md"),
    ("crops", "🌾 Crops", "content/crops/latest.md"),
    ("seasonal", "📅 Seasonal Checklist", "content/seasonal"),
    ("tools", "📊 Tools & Calculators", "content/tools/index.md"),
]

def get_content(file_path):
    """Load content from markdown file"""
    path = PROJECT_ROOT / file_path
    if path.exists():
        return path.read_text()
    return ""

def build_section_card(section_id, title, content_path):
    """Build a section card for the homepage"""
    content = ""
    if isinstance(content_path, str) and content_path.endswith('.md'):
        content = get_content(content_path)
        # Simple markdown strip
        content = content.split('---')[2] if '---' in content else content
        content = content[:300] + "..." if len(content) > 300 else content
    
    return f'''
    <div class="section-card">
        <h3>{title}</h3>
        <a href="/{section_id}/" class="btn">View Section →</a>
    </div>'''

def build_homepage():
    """Build the main homepage"""
    sections_html = "\n".join(
        build_section_card(sid, title, path) 
        for sid, title, path in SECTIONS
    )
    
    # Get latest daily brief
    brief = get_content("content/daily-brief.md")
    brief_excerpt = brief.split('---')[-1][:500] if '---' in brief else brief[:500]
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UK Farm Blog - Daily Updates for British Farmers</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f0; color: #333; line-height: 1.6; }}
        header {{ background: #2d5a27; color: white; padding: 40px 20px; text-align: center; }}
        header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        header p {{ font-size: 1.2em; opacity: 0.9; }}
        nav {{ background: #1e3d1a; padding: 15px; text-align: center; }}
        nav a {{ color: white; text-decoration: none; margin: 0 15px; padding: 8px 15px; border-radius: 4px; }}
        nav a:hover {{ background: #3d6b3d; }}
        main {{ max-width: 1200px; margin: 0 auto; padding: 40px 20px; }}
        .hero {{ background: white; padding: 30px; border-radius: 8px; margin-bottom: 40px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .hero h2 {{ color: #2d5a27; margin-bottom: 15px; }}
        .sections-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }}
        .section-card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s; }}
        .section-card:hover {{ transform: translateY(-3px); }}
        .section-card h3 {{ color: #2d5a27; margin-bottom: 15px; font-size: 1.3em; }}
        .btn {{ display: inline-block; background: #2d5a27; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-top: 10px; }}
        .btn:hover {{ background: #3d6b3d; }}
        footer {{ background: #1e3d1a; color: white; text-align: center; padding: 30px; margin-top: 60px; }}
        .updated {{ color: #666; font-size: 0.9em; margin-top: 10px; }}
    </style>
</head>
<body>
    <header>
        <h1>🌾 UK Farm Blog</h1>
        <p>Daily updates for British farmers</p>
    </header>
    <nav>
        <a href="/">Home</a>
        <a href="/daily-brief/">Daily Brief</a>
        <a href="/weather/">Weather</a>
        <a href="/grants/">Grants</a>
        <a href="/markets/">Markets</a>
        <a href="/equipment/">Equipment</a>
        <a href="/livestock/">Livestock</a>
        <a href="/crops/">Crops</a>
        <a href="/tools/">Tools</a>
    </nav>
    <main>
        <div class="hero">
            <h2>🗞 Today's Farm Brief</h2>
            <p>{brief_excerpt}</p>
            <a href="/daily-brief/" class="btn">Read Full Brief →</a>
        </div>
        <h2 style="margin-bottom: 20px; color: #2d5a27;">Explore Our Sections</h2>
        <div class="sections-grid">
            {sections_html}
        </div>
    </main>
    <footer>
        <p>UK Farm Blog - Updated daily with the latest farming news, weather, grants, and market prices.</p>
        <p class="updated">Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}</p>
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
    
    # Create section pages
    for section_id, title, _ in SECTIONS:
        section_dir = OUTPUT_DIR / section_id
        section_dir.mkdir(exist_ok=True)
        content = get_content(f"content/{section_id}/latest.md") if isinstance(_, str) and "latest" in _ else get_content(f"content/{section_id}.md")
        
        section_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - UK Farm Blog</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f0; color: #333; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        header {{ background: #2d5a27; color: white; padding: 30px 20px; margin: -20px -20px 30px; text-align: center; border-radius: 8px 8px 0 0; }}
        h1 {{ color: white; }}
        a {{ color: #2d5a27; }}
        footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }}
    </style>
</head>
<body>
    <header>
        <h1>{title}</h1>
        <p><a href="/" style="color: white;">← Back to Home</a></p>
    </header>
    <main>
        {content}
    </main>
    <footer>
        <p><a href="/">← Back to UK Farm Blog Home</a></p>
    </footer>
</body>
</html>"""
        (section_dir / "index.html").write_text(section_html)
    
    print(f"✅ Built site with {len(SECTIONS)} sections")
    print(f"📁 Output: {OUTPUT_DIR}")
    print("📦 Ready for git commit and push")

if __name__ == "__main__":
    main()