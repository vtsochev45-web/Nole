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

# Base path - defaults to /Nole for GitHub Pages; set SITE_BASE_PATH="" for Vercel
BASE_PATH = os.environ.get("SITE_BASE_PATH", "/Nole").rstrip("/")

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

GOOGLE_FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">'

# Subtle white cross-hatch pattern used as header overlay (3 % opacity)
_HEADER_PATTERN_SVG = (
    "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60'"
    " xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E"
    "%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2"
    "v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6z"
    "M6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")"
)

COMMON_CSS = """
:root {
  --navy: #0f2d5e;
  --navy-mid: #1a4080;
  --green: #1e6b3c;
  --green-light: #2a8f52;
  --gold: #e8a020;
  --gold-light: #f5c842;
  --bg: #f4f6f8;
  --surface: #ffffff;
  --text: #1a1a2e;
  --text-muted: #5a6474;
  --border: #e2e8f0;
  --radius: 12px;
  --shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
  --shadow: 0 4px 20px rgba(0,0,0,0.10);
  --shadow-lg: 0 8px 40px rgba(0,0,0,0.14);
}
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { font-family: 'Inter', 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.7; font-size: 16px; }

/* ── Top bar ── */
.topbar { background: var(--navy); color: rgba(255,255,255,0.75); font-size: 0.78rem; padding: 8px 24px; display: flex; justify-content: space-between; align-items: center; }
.topbar span { display: flex; align-items: center; gap: 6px; }

/* ── Header / branding ── */
header { background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 60%, #2358a8 100%); color: white; padding: 48px 24px 40px; text-align: center; position: relative; overflow: hidden; }
header::before { content: ''; position: absolute; inset: 0; background: __HEADER_PATTERN__; }
.site-logo { display: inline-flex; align-items: center; gap: 14px; margin-bottom: 16px; text-decoration: none; }
.logo-icon { width: 56px; height: 56px; background: linear-gradient(135deg, var(--green) 0%, var(--green-light) 100%); border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 1.8rem; box-shadow: 0 4px 16px rgba(0,0,0,0.25); }
.logo-text { text-align: left; }
.logo-text .brand { font-size: 1.6rem; font-weight: 800; color: white; letter-spacing: -0.5px; line-height: 1; }
.logo-text .tagline { font-size: 0.78rem; color: rgba(255,255,255,0.65); font-weight: 400; letter-spacing: 0.8px; text-transform: uppercase; margin-top: 2px; }
header p.strapline { font-size: 1.05rem; color: rgba(255,255,255,0.82); max-width: 520px; margin: 0 auto; font-weight: 400; }

/* ── Navigation ── */
nav { background: var(--surface); border-bottom: 1px solid var(--border); padding: 0 24px; position: sticky; top: 0; z-index: 200; box-shadow: var(--shadow-sm); }
.nav-inner { max-width: 1280px; margin: 0 auto; display: flex; align-items: center; gap: 2px; overflow-x: auto; -webkit-overflow-scrolling: touch; scrollbar-width: none; }
.nav-inner::-webkit-scrollbar { display: none; }
nav a { color: var(--text-muted); text-decoration: none; padding: 14px 14px; font-size: 0.84rem; font-weight: 500; white-space: nowrap; border-bottom: 3px solid transparent; transition: all 0.2s; display: inline-block; }
nav a:hover { color: var(--green); border-bottom-color: var(--green); }
nav a.home-link { color: var(--navy); font-weight: 700; border-bottom-color: var(--gold); }

/* ── Stats bar ── */
.stats-bar { background: var(--green); color: white; }
.stats-inner { max-width: 1280px; margin: 0 auto; display: grid; grid-template-columns: repeat(4, 1fr); text-align: center; }
.stat-item { padding: 18px 12px; border-right: 1px solid rgba(255,255,255,0.15); }
.stat-item:last-child { border-right: none; }
.stat-num { font-size: 1.5rem; font-weight: 800; line-height: 1; }
.stat-label { font-size: 0.75rem; opacity: 0.85; margin-top: 3px; font-weight: 500; letter-spacing: 0.3px; }

/* ── Main layout ── */
main { max-width: 1280px; margin: 0 auto; padding: 48px 24px 64px; }

/* ── Hero (homepage) ── */
.hero { background: linear-gradient(135deg, var(--green) 0%, var(--green-light) 100%); color: white; padding: 48px 48px 44px; border-radius: var(--radius); margin-bottom: 56px; position: relative; overflow: hidden; display: grid; grid-template-columns: 1fr auto; gap: 32px; align-items: start; }
.hero::after { content: '🌾'; position: absolute; right: -10px; bottom: -20px; font-size: 9rem; opacity: 0.08; line-height: 1; pointer-events: none; }
.hero h2 { font-size: 1.05rem; text-transform: uppercase; letter-spacing: 1.2px; font-weight: 600; opacity: 0.85; margin-bottom: 10px; }
.hero-content h3 { font-size: 1.75rem; font-weight: 800; line-height: 1.25; margin-bottom: 16px; }
.hero-content p { opacity: 0.9; font-size: 1.02rem; max-width: 580px; }
.hero-badge { background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.25); border-radius: 10px; padding: 20px 24px; text-align: center; backdrop-filter: blur(4px); min-width: 160px; flex-shrink: 0; }
.hero-badge .badge-num { font-size: 2rem; font-weight: 800; line-height: 1; }
.hero-badge .badge-label { font-size: 0.78rem; opacity: 0.85; margin-top: 4px; }
.btn { display: inline-block; background: var(--gold); color: var(--navy); padding: 13px 28px; text-decoration: none; border-radius: 8px; font-weight: 700; margin-top: 24px; font-size: 0.95rem; transition: all 0.2s; letter-spacing: 0.2px; }
.btn:hover { background: var(--gold-light); transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
.btn-outline { display: inline-block; border: 2px solid rgba(255,255,255,0.5); color: white; padding: 11px 26px; text-decoration: none; border-radius: 8px; font-weight: 600; margin-top: 12px; margin-left: 12px; font-size: 0.95rem; transition: all 0.2s; }
.btn-outline:hover { background: rgba(255,255,255,0.12); border-color: white; }

/* ── Section heading ── */
.section-heading { display: flex; align-items: center; gap: 12px; margin-bottom: 28px; }
.section-heading h2 { font-size: 1.3rem; font-weight: 700; color: var(--navy); }
.section-heading .line { flex: 1; height: 1px; background: var(--border); }

/* ── Cards grid ── */
.sections-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px; }
.section-card { background: var(--surface); border-radius: var(--radius); padding: 28px 24px; box-shadow: var(--shadow-sm); border: 1px solid var(--border); border-top: 4px solid var(--green); transition: all 0.25s; display: flex; flex-direction: column; }
.section-card:nth-child(2n) { border-top-color: var(--navy-mid); }
.section-card:nth-child(3n) { border-top-color: var(--gold); }
.section-card:hover { transform: translateY(-4px); box-shadow: var(--shadow); border-color: transparent; }
.card-icon { font-size: 2rem; margin-bottom: 12px; }
.section-card h3 { font-size: 1rem; font-weight: 700; color: var(--navy); margin-bottom: 8px; }
.section-card p { font-size: 0.88rem; color: var(--text-muted); flex: 1; margin-bottom: 20px; }
.card-btn { display: inline-flex; align-items: center; gap: 6px; background: var(--navy); color: white; padding: 9px 18px; text-decoration: none; border-radius: 7px; font-size: 0.84rem; font-weight: 600; align-self: flex-start; transition: background 0.2s; }
.card-btn:hover { background: var(--green); }
.card-btn::after { content: '→'; }

/* ── Content / article page ── */
.content-page { background: var(--surface); border-radius: 16px; padding: 56px; max-width: 900px; margin: 40px auto; box-shadow: var(--shadow); }
.content-page h1 { color: var(--navy); font-size: 2.2rem; font-weight: 800; margin-bottom: 8px; line-height: 1.25; }
.content-page .page-meta { color: var(--text-muted); font-size: 0.88rem; margin-bottom: 36px; padding-bottom: 28px; border-bottom: 2px solid var(--border); }
.content-page h2 { color: var(--navy); font-size: 1.35rem; font-weight: 700; margin: 40px 0 16px; padding-left: 16px; border-left: 4px solid var(--green); }
.content-page h3 { color: var(--green); font-size: 1.1rem; font-weight: 700; margin: 28px 0 10px; }
.content-page p { color: #2d3748; margin-bottom: 16px; }
.content-page ul, .content-page ol { padding-left: 24px; margin-bottom: 16px; }
.content-page li { margin-bottom: 6px; }
.content-page table { width: 100%; border-collapse: collapse; margin: 24px 0; font-size: 0.92rem; }
.content-page th { background: var(--navy); color: white; padding: 12px 16px; text-align: left; font-weight: 600; }
.content-page td { padding: 11px 16px; border-bottom: 1px solid var(--border); }
.content-page tr:hover td { background: #f8fafc; }
.content-page blockquote { background: #f0f7ff; border-left: 4px solid var(--navy-mid); padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 20px 0; font-style: italic; color: var(--text-muted); }
.back-btn { display: inline-flex; align-items: center; gap: 8px; background: var(--bg); color: var(--navy); padding: 11px 22px; text-decoration: none; border-radius: 8px; font-weight: 600; border: 1px solid var(--border); transition: all 0.2s; font-size: 0.9rem; }
.back-btn:hover { background: var(--navy); color: white; border-color: var(--navy); }

/* ── Footer ── */
footer { background: var(--navy); color: rgba(255,255,255,0.75); padding: 64px 24px 32px; margin-top: 0; }
.footer-inner { max-width: 1280px; margin: 0 auto; }
.footer-grid { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 48px; margin-bottom: 48px; }
.footer-brand .brand { font-size: 1.3rem; font-weight: 800; color: white; margin-bottom: 10px; }
.footer-brand p { font-size: 0.88rem; line-height: 1.7; }
.footer-col h4 { font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.5); margin-bottom: 16px; }
.footer-col a { display: block; color: rgba(255,255,255,0.7); text-decoration: none; font-size: 0.88rem; margin-bottom: 9px; transition: color 0.2s; }
.footer-col a:hover { color: var(--gold-light); }
.footer-bottom { padding-top: 28px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center; font-size: 0.82rem; }
.footer-badge { background: var(--green); color: white; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; }

/* ── Responsive ── */
@media (max-width: 1024px) {
  .footer-grid { grid-template-columns: 1fr 1fr; gap: 32px; }
  .stats-inner { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 768px) {
  header { padding: 36px 20px 28px; }
  .logo-text .brand { font-size: 1.3rem; }
  .hero { grid-template-columns: 1fr; padding: 32px 28px; }
  .hero-badge { display: none; }
  .hero-content h3 { font-size: 1.4rem; }
  .sections-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
  .content-page { padding: 32px 24px; }
  .footer-grid { grid-template-columns: 1fr; gap: 24px; }
  .footer-bottom { flex-direction: column; gap: 10px; text-align: center; }
  .stats-inner { grid-template-columns: repeat(2, 1fr); }
  .topbar { display: none; }
}
@media (max-width: 480px) {
  main { padding: 28px 16px 48px; }
  .sections-grid { grid-template-columns: 1fr; }
}
"""
COMMON_CSS = COMMON_CSS.replace("__HEADER_PATTERN__", _HEADER_PATTERN_SVG)

def build_nav(current_sid=None):
    home_class = ' class="home-link"' if current_sid is None else ''
    links = f'<a href="{BASE_PATH}/"{home_class}>🏠 Home</a>'
    for sid, stitle, _ in SECTIONS:
        label = stitle.split(" ", 1)[1]
        icon = stitle.split(" ", 1)[0]
        active = ' style="color:var(--green);border-bottom-color:var(--green)"' if sid == current_sid else ''
        links += f'<a href="{BASE_PATH}/{sid}/"{active}>{icon} {label}</a>'
    return f'<nav><div class="nav-inner">{links}</div></nav>'

def build_footer():
    quick_links = ''.join(f'<a href="{BASE_PATH}/{sid}/">{t.split(" ",1)[1]}</a>' for sid, t, _ in SECTIONS[:5])
    more_links  = ''.join(f'<a href="{BASE_PATH}/{sid}/">{t.split(" ",1)[1]}</a>' for sid, t, _ in SECTIONS[5:])
    year = datetime.now().year
    return f"""<footer>
  <div class="footer-inner">
    <div class="footer-grid">
      <div class="footer-brand">
        <div class="brand">🌾 UK Farm Blog</div>
        <p>Practical, daily farming updates for British farmers. Covering grants, markets, weather, equipment and more — updated every day.</p>
      </div>
      <div class="footer-col">
        <h4>Sections</h4>
        {quick_links}
      </div>
      <div class="footer-col">
        <h4>More</h4>
        {more_links}
      </div>
      <div class="footer-col">
        <h4>Resources</h4>
        <a href="https://www.gov.uk/farming-investment-fund" target="_blank" rel="noopener">Gov.uk Farming</a>
        <a href="https://ahdb.org.uk/" target="_blank" rel="noopener">AHDB</a>
        <a href="https://www.nfuonline.com/" target="_blank" rel="noopener">NFU Online</a>
        <a href="{BASE_PATH}/tools/">Calculators</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {year} UK Farm Blog · For information only · Always verify with official sources</span>
      <span class="footer-badge">Updated Daily</span>
    </div>
  </div>
</footer>"""

def build_homepage():
    brief_content = get_content("content/daily-brief.md")[:700]
    today = datetime.now().strftime('%d %B %Y')
    
    cards_html = ""
    for section_id, title, desc in SECTIONS:
        icon = title.split(" ", 1)[0]
        label = title.split(" ", 1)[1]
        cards_html += f'''<div class="section-card">
  <div class="card-icon">{icon}</div>
  <h3>{label}</h3>
  <p>{desc}</p>
  <a href="{BASE_PATH}/{section_id}/" class="card-btn">{label}</a>
</div>'''
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UK Farm Blog – Daily Updates for British Farmers</title>
    <meta name="description" content="Daily farming news, grants, market prices, weather alerts and practical guides for UK farmers. Updated every morning.">
    <meta property="og:title" content="UK Farm Blog – Daily Updates for British Farmers">
    <meta property="og:description" content="Practical daily farming updates covering grants, markets, weather and equipment.">
    <meta property="og:type" content="website">
    {GOOGLE_FONTS}
    <style>{COMMON_CSS}</style>
</head>
<body>
    <div class="topbar">
        <span>📅 {today}</span>
        <span>🇬🇧 Serving British farmers since 2025</span>
    </div>
    <header>
        <a href="{BASE_PATH}/" class="site-logo" style="text-decoration:none">
            <div class="logo-icon">🌾</div>
            <div class="logo-text">
                <div class="brand">UK Farm Blog</div>
                <div class="tagline">Your daily farming briefing</div>
            </div>
        </a>
        <p class="strapline" style="margin-top:10px">Practical grants, markets &amp; weather updates for British farmers — every morning</p>
    </header>
    {build_nav()}
    <div class="stats-bar">
        <div class="stats-inner">
            <div class="stat-item"><div class="stat-num">10</div><div class="stat-label">Sections</div></div>
            <div class="stat-item"><div class="stat-num">Daily</div><div class="stat-label">Updates</div></div>
            <div class="stat-item"><div class="stat-num">Free</div><div class="stat-label">Always</div></div>
            <div class="stat-item"><div class="stat-num">🇬🇧</div><div class="stat-label">UK Focused</div></div>
        </div>
    </div>
    <main>
        <div class="hero">
            <div class="hero-content">
                <h2>📰 Today's Farm Brief</h2>
                <h3>Your daily roundup — {today}</h3>
                {md_to_html(brief_content)}
                <a href="{BASE_PATH}/daily-brief/" class="btn">Read Full Brief</a>
                <a href="{BASE_PATH}/grants/" class="btn-outline">Grant Deadlines</a>
            </div>
            <div class="hero-badge">
                <div class="badge-num">🔔</div>
                <div class="badge-label" style="margin-top:8px">Updated<br><strong>Today</strong></div>
            </div>
        </div>
        <div class="section-heading">
            <h2>Browse All Sections</h2>
            <div class="line"></div>
        </div>
        <div class="sections-grid">
            {cards_html}
        </div>
    </main>
    {build_footer()}
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

    icon = title.split(" ", 1)[0]
    label = title.split(" ", 1)[1]
    today = datetime.now().strftime('%d %B %Y')
    
    html_content = md_to_html(content)
    html_content = html_content.replace('href="./', f'href="{BASE_PATH}/')
    html_content = html_content.replace("href='./", f"href='{BASE_PATH}/")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{label} – UK Farm Blog</title>
    <meta name="description" content="{desc} — practical daily updates for British farmers.">
    <meta property="og:title" content="{label} – UK Farm Blog">
    <meta property="og:description" content="{desc}">
    <meta property="og:type" content="website">
    {GOOGLE_FONTS}
    <style>{COMMON_CSS}</style>
</head>
<body>
    <div class="topbar">
        <span>📅 {today}</span>
        <span>🇬🇧 UK Farm Blog</span>
    </div>
    <header>
        <a href="{BASE_PATH}/" class="site-logo" style="text-decoration:none">
            <div class="logo-icon">🌾</div>
            <div class="logo-text">
                <div class="brand">UK Farm Blog</div>
                <div class="tagline">Your daily farming briefing</div>
            </div>
        </a>
        <p class="strapline" style="margin-top:8px">{icon} {label}</p>
    </header>
    {build_nav(section_id)}
    <main>
        <article class="content-page">
            <h1>{icon} {label}</h1>
            <p class="page-meta">Updated {today} &nbsp;·&nbsp; {desc}</p>
            {html_content}
            <p style="text-align: center; margin-top: 48px;">
                <a href="{BASE_PATH}/" class="back-btn">← Back to Home</a>
            </p>
        </article>
    </main>
    {build_footer()}
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