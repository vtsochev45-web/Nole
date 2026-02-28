#!/usr/bin/env python3
"""Build UK Farm Blog with GitHub Pages compatible absolute links"""

import os
import re
import json
import shutil
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
# or when a custom domain is configured (detected via CNAME file in the project root).
_cname_file = PROJECT_ROOT / "CNAME"
_has_custom_domain = _cname_file.exists() and _cname_file.read_text().strip() != ""
_default_base = "" if _has_custom_domain else "/Nole"
BASE_PATH = os.environ.get("SITE_BASE_PATH", _default_base).rstrip("/")

# ── Site identity ─────────────────────────────────────────────────────────────
# Canonical domain – used in sitemap, robots.txt, and the privacy policy page.
SITE_URL = os.environ.get("SITE_URL", "https://britfarmers.com").rstrip("/")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "privacy@britfarmers.com")

# ── Monetisation ──────────────────────────────────────────────────────────────
# The publisher ID is read from the ADSENSE_PUB_ID environment variable (set as
# a GitHub/Vercel secret).  The real pub ID is used as the fallback so it is
# correct even when the secret is absent.  AdSense publisher IDs are inherently
# public — they appear verbatim in every page's HTML that is served to visitors.
ADSENSE_PUB_ID = os.environ.get("ADSENSE_PUB_ID", "ca-pub-9535677982209167")

# Ad slot IDs – replace with real slot IDs from your AdSense account, or set
# the corresponding environment variables.
ADSENSE_SLOT_HOME_TOP    = os.environ.get("ADSENSE_SLOT_HOME_TOP",    "0000000001")
ADSENSE_SLOT_HOME_MID    = os.environ.get("ADSENSE_SLOT_HOME_MID",    "0000000002")
ADSENSE_SLOT_SECTION_TOP = os.environ.get("ADSENSE_SLOT_SECTION_TOP", "0000000003")
ADSENSE_SLOT_ARTICLE_MID = os.environ.get("ADSENSE_SLOT_ARTICLE_MID", "0000000004")

ADSENSE_SCRIPT = f"""
    <!-- Google AdSense - site verification & auto ads -->
    <meta name="google-adsense-account" content="{ADSENSE_PUB_ID}">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB_ID}"
            crossorigin="anonymous"></script>"""

# AMP Auto Ads – script tag goes inside <head>; the <amp-auto-ads> element must
# be placed immediately after the opening <body> tag.
AMP_AUTO_ADS_SCRIPT = """    <script async custom-element="amp-auto-ads"
        src="https://cdn.ampproject.org/v0/amp-auto-ads-0.1.js">
    </script>"""

AMP_AUTO_ADS_TAG = f"""<amp-auto-ads type="adsense"
    data-ad-client="{ADSENSE_PUB_ID}">
</amp-auto-ads>"""

# Inline ad unit (responsive display ad)
def build_ad_unit(slot_id="0000000000", label="Advertisement"):
    return f"""<div class="ad-container" aria-label="{label}">
  <ins class="adsbygoogle"
       style="display:block"
       data-ad-client="{ADSENSE_PUB_ID}"
       data-ad-slot="{slot_id}"
       data-ad-format="auto"
       data-full-width-responsive="true"></ins>
  <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
</div>"""

# Affiliate partner links shown as a "Trusted Partners" strip.
# For Amazon Associates, set the AMAZON_AFFILIATE_TAG env var (e.g. "yoursite-21").
# For other partners, replace the URLs with your affiliate-tracked URLs.
_AMAZON_TAG = os.environ.get("AMAZON_AFFILIATE_TAG", "")
_AMAZON_URL = (
    f"https://www.amazon.co.uk/farm-supplies/?tag={_AMAZON_TAG}"
    if _AMAZON_TAG else
    "https://www.amazon.co.uk/farm-supplies/"
)

AFFILIATE_PARTNERS = [
    ("Farmers Weekly Shop",    "https://shop.fwi.co.uk/",                    "Books, guides & agronomy resources"),
    ("Amazon Farm Supplies",   _AMAZON_URL,                                  "Equipment, tools & PPE"),
    ("Farmers Guardian Store", "https://www.farmersguardian.com/",            "News, reports & industry data"),
    ("AHDB MarketPlace",       "https://ahdb.org.uk/",                        "Free market data & benchmarking"),
    ("NFU Mutual Insurance",   "https://www.nfumutual.co.uk/farm-insurance/", "Farm insurance & risk cover"),
]

def build_affiliate_strip():
    items = "".join(
        f'<a href="{url}" class="partner-item" target="_blank" rel="noopener sponsored">'
        f'<strong>{name}</strong><span>{desc}</span></a>'
        for name, url, desc in AFFILIATE_PARTNERS
    )
    return f"""<section class="partners-strip">
  <div class="partners-inner">
    <span class="partners-label">🤝 Trusted Partners</span>
    {items}
  </div>
</section>"""

def inject_adsense(html_content, label=""):
    """Inject ADSENSE_SCRIPT before </head> if not already present."""
    if ('pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' in html_content
            or 'google-adsense-account' in html_content):
        return html_content
    if '</head>' not in html_content:
        print(f"  ⚠️  No </head> tag found{' in ' + label if label else ''} — AdSense script not injected")
        return html_content
    return html_content.replace('</head>', f'{ADSENSE_SCRIPT}\n</head>', 1)


def build_amp_page(title, description, canonical_url, body_content):
    """Return a valid AMP HTML page with Auto Ads enabled.

    The amp-auto-ads <script> tag is placed inside <head> as required by the
    AMP spec, and the <amp-auto-ads> element is the first child of <body> so
    that Google can automatically place ads across the page.
    """
    return f"""<!DOCTYPE html>
<html \u26a1 lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,minimum-scale=1,initial-scale=1">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <link rel="canonical" href="{canonical_url}">
    {AMP_AUTO_ADS_SCRIPT}
    <script async src="https://cdn.ampproject.org/v0.js"></script>
    <style amp-boilerplate>body{{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}}@-webkit-keyframes -amp-start{{from{{visibility:hidden}}to{{visibility:visible}}}}</style><noscript><style amp-boilerplate>body{{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}}</style></noscript>
    <style amp-custom>
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 16px; color: #333; }}
        h1 {{ font-size: 1.6rem; margin-bottom: 0.5rem; }}
        h2 {{ font-size: 1.3rem; }}
        a {{ color: #2a5298; }}
        .back-link {{ display: inline-block; margin-top: 24px; }}
    </style>
</head>
<body>
    {AMP_AUTO_ADS_TAG}
    {body_content}
</body>
</html>"""


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

/* ── Ads ── */
.ad-container { margin: 32px auto; max-width: 970px; text-align: center; overflow: hidden; }
.ad-container::before { content: 'Advertisement'; display: block; font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 4px; }

/* ── Partners strip ── */
.partners-strip { background: #f8fafc; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); padding: 18px 24px; }
.partners-inner { max-width: 1280px; margin: 0 auto; display: flex; flex-wrap: wrap; align-items: center; gap: 12px; }
.partners-label { font-size: 0.78rem; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.8px; white-space: nowrap; flex-shrink: 0; }
.partner-item { display: flex; flex-direction: column; background: white; border: 1px solid var(--border); border-radius: 8px; padding: 8px 14px; text-decoration: none; color: var(--navy); font-size: 0.82rem; transition: box-shadow 0.2s, border-color 0.2s; line-height: 1.3; }
.partner-item:hover { border-color: var(--green); box-shadow: 0 2px 8px rgba(30,107,60,0.12); }
.partner-item strong { font-weight: 600; }
.partner-item span { font-size: 0.75rem; color: var(--text-muted); font-weight: 400; }

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
        <a href="mailto:advertise@ukfarmblog.co.uk" style="color:var(--gold-light);font-weight:600">📢 Advertise with Us</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© {year} UK Farm Blog · For information only · Always verify with official sources · <a href="{BASE_PATH}/privacy-policy/" style="color:rgba(255,255,255,0.6);text-decoration:underline">Privacy Policy</a></span>
      <span class="footer-badge">Updated Daily</span>
    </div>
  </div>
</footer>"""

def build_privacy_policy_page():
    today = datetime.now().strftime('%d %B %Y')
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Privacy Policy – UK Farm Blog</title>
    <meta name="description" content="Privacy policy for UK Farm Blog, explaining how we collect, use and protect your data.">
    {GOOGLE_FONTS}
    {ADSENSE_SCRIPT}
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
    </header>
    {build_nav()}
    <main>
        <article class="content-page">
            <h1>Privacy Policy</h1>
            <p class="page-meta">Last updated: {today}</p>

            <p>This Privacy Policy explains how UK Farm Blog ("<strong>we</strong>", "<strong>us</strong>", or "<strong>our</strong>") collects, uses, and shares information about you when you visit <a href="{SITE_URL}">{SITE_URL}</a>.</p>

            <h2>Information We Collect</h2>
            <p>We do not directly collect personal information. However, third-party services we use may collect data as described below.</p>

            <h2>Google AdSense &amp; Advertising</h2>
            <p>We use Google AdSense to display advertisements. Google may use cookies and similar tracking technologies to show you personalised ads based on your interests and browsing activity across sites. Google's use of advertising cookies enables it and its partners to serve ads based on your visit to this site and/or other sites on the Internet.</p>
            <p>You may opt out of personalised advertising by visiting <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">Google Ads Settings</a> or <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener">www.aboutads.info/choices</a>.</p>
            <p>For more information on how Google uses data, see <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">How Google uses data when you use our partners' sites or apps</a>.</p>

            <h2>Cookies</h2>
            <p>This site uses cookies placed by Google AdSense and Google Analytics (if enabled) to measure traffic and serve relevant advertisements. By continuing to use this site you consent to the placement of these cookies. You can control cookies through your browser settings.</p>

            <h2>Third-Party Links</h2>
            <p>This site contains links to external websites, including affiliate partner links. We are not responsible for the privacy practices of those sites and recommend you review their policies separately.</p>

            <h2>Affiliate Links</h2>
            <p>Some links on this site are affiliate links. If you click an affiliate link and make a purchase, we may earn a small commission at no additional cost to you. Affiliate relationships are disclosed with the "sponsored" link attribute.</p>

            <h2>Children's Privacy</h2>
            <p>This site is not directed at children under the age of 13. We do not knowingly collect personal information from children.</p>

            <h2>Changes to This Policy</h2>
            <p>We may update this Privacy Policy from time to time. Any changes will be posted on this page with an updated date.</p>

            <h2>Contact Us</h2>
            <p>If you have any questions about this Privacy Policy, please contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

            <p style="text-align: center; margin-top: 48px;">
                <a href="{BASE_PATH}/" class="back-btn">← Back to Home</a>
            </p>
        </article>
    </main>
    {build_footer()}
</body>
</html>"""

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
    {ADSENSE_SCRIPT}
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
    {build_ad_unit(ADSENSE_SLOT_HOME_TOP, "Top leaderboard ad")}
    {build_affiliate_strip()}
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
        {build_ad_unit(ADSENSE_SLOT_HOME_MID, "Mid-page ad")}
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
    {ADSENSE_SCRIPT}
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
    {build_ad_unit(ADSENSE_SLOT_SECTION_TOP, "Section page top ad")}
    <main>
        <article class="content-page">
            <h1>{icon} {label}</h1>
            <p class="page-meta">Updated {today} &nbsp;·&nbsp; {desc}</p>
            {html_content}
            {build_ad_unit(ADSENSE_SLOT_ARTICLE_MID, "In-article ad")}
            <p style="text-align: center; margin-top: 48px;">
                <a href="{BASE_PATH}/" class="back-btn">← Back to Home</a>
            </p>
        </article>
    </main>
    {build_affiliate_strip()}
    {build_footer()}
</body>
</html>"""

def main():
    print("🔨 Building UK Farm Blog v3.0...")
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Copy CNAME so GitHub Pages preserves the custom domain on every deployment
    if _cname_file.exists():
        shutil.copy(_cname_file, OUTPUT_DIR / "CNAME")
        print(f"✅ CNAME ({_cname_file.read_text().strip()})")

    # Generate ads.txt for AdSense publisher authorization.
    # f08c47fec0942fa0 is Google's AdSense certified ads seller (TAG-ID) required by the IAB ads.txt spec.
    ads_txt = f"google.com, {ADSENSE_PUB_ID}, DIRECT, f08c47fec0942fa0\n"
    (OUTPUT_DIR / "ads.txt").write_text(ads_txt)
    print(f"✅ ads.txt ({ADSENSE_PUB_ID})")

    # Generate robots.txt so search engine crawlers (including Googlebot) can
    # access all pages.  A missing robots.txt can prevent AdSense from verifying
    # site ownership because the crawler cannot confirm the meta-tag is present.
    robots_txt = (
        "User-agent: *\n"
        "Allow: /\n"
        f"\nSitemap: {SITE_URL}/sitemap.xml\n"
    )
    (OUTPUT_DIR / "robots.txt").write_text(robots_txt)
    print("✅ robots.txt")

    # Homepage
    (OUTPUT_DIR / "index.html").write_text(build_homepage())
    print("✅ Homepage")
    
    # Section pages
    for section_id, title, desc in SECTIONS:
        section_dir = OUTPUT_DIR / section_id
        section_dir.mkdir(exist_ok=True)
        (section_dir / "index.html").write_text(build_section_page(section_id, title, desc))
        print(f"  ✅ {title}")

    # Privacy Policy page (required by Google AdSense policy)
    privacy_dir = OUTPUT_DIR / "privacy-policy"
    privacy_dir.mkdir(exist_ok=True)
    (privacy_dir / "index.html").write_text(build_privacy_policy_page())
    print("✅ Privacy Policy page")

    # Generate sitemap.xml to help Google discover and index all pages
    today_iso = datetime.now().strftime('%Y-%m-%d')
    urls = [f"{SITE_URL}/"]
    urls += [f"{SITE_URL}/{sid}/" for sid, _, _ in SECTIONS]
    urls.append(f"{SITE_URL}/privacy-policy/")
    sitemap_entries = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{today_iso}</lastmod><changefreq>daily</changefreq></url>"
        for u in urls
    )
    sitemap_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_entries}\n"
        '</urlset>\n'
    )
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap_xml)
    print("✅ sitemap.xml")
    
    # Copy tools (update links, inject AdSense)
    tools_src = PROJECT_ROOT / "content" / "tools"
    if tools_src.exists():
        tools_dir = OUTPUT_DIR / "tools"
        tools_dir.mkdir(exist_ok=True)
        for html_file in tools_src.glob("*.html"):
            content = html_file.read_text()
            # Update any links to use BASE_PATH
            content = content.replace('href="/', f'href="{BASE_PATH}/')
            content = content.replace('href="./', f'href="{BASE_PATH}/')
            # Inject AdSense script into <head> if not already present
            content = inject_adsense(content, html_file.name)
            (tools_dir / html_file.name).write_text(content)
            print(f"  ✅ Tool: {html_file.name}")
    
    # Copy community (update links, inject AdSense)
    community_src = PROJECT_ROOT / "content" / "community"
    if community_src.exists():
        community_dir = OUTPUT_DIR / "community"
        community_dir.mkdir(exist_ok=True)
        for f in community_src.glob("*.html"):
            content = f.read_text()
            content = content.replace('href="/', f'href="{BASE_PATH}/')
            content = content.replace('href="./', f'href="{BASE_PATH}/')
            # Inject AdSense script into <head> if not already present
            content = inject_adsense(content, f.name)
            (community_dir / f.name).write_text(content)
            print(f"  ✅ Community: {f.name}")

    # AMP pages – homepage and each section get an AMP counterpart served from
    # /{section}/amp/index.html (canonical page links back to the regular URL).
    amp_dir = OUTPUT_DIR / "amp"
    amp_dir.mkdir(exist_ok=True)
    brief_content = get_content("content/daily-brief.md")[:700]
    today = datetime.now().strftime('%d %B %Y')
    home_body = f"""<h1>🌾 UK Farm Blog</h1>
    <p>Practical grants, markets &amp; weather updates for British farmers — every morning</p>
    <p><strong>📰 Today's Farm Brief – {today}</strong></p>
    {md_to_html(brief_content)}
    <p><a href="{SITE_URL}/">View full site</a></p>"""
    (amp_dir / "index.html").write_text(
        build_amp_page(
            title="UK Farm Blog – Daily Updates for British Farmers",
            description="Daily farming news, grants, market prices, weather alerts and practical guides for UK farmers.",
            canonical_url=f"{SITE_URL}/",
            body_content=home_body,
        )
    )
    print("✅ AMP Homepage")

    for section_id, title, desc in SECTIONS:
        content = ""
        for path in [f"content/{section_id}/latest.md", f"content/{section_id}/index.md", f"content/{section_id}.md"]:
            if (PROJECT_ROOT / path).exists():
                content = get_content(path)
                break
        icon = title.split(" ", 1)[0]
        label = title.split(" ", 1)[1]
        section_body = f"""<h1>{icon} {label}</h1>
    <p>{desc}</p>
    {md_to_html(content) if content else f"<p>{label} content coming soon!</p>"}
    <p><a class="back-link" href="{SITE_URL}/{section_id}/">View full {label} page</a></p>"""
        section_amp_dir = OUTPUT_DIR / section_id / "amp"
        section_amp_dir.mkdir(parents=True, exist_ok=True)
        (section_amp_dir / "index.html").write_text(
            build_amp_page(
                title=f"{label} – UK Farm Blog",
                description=f"{desc} — practical daily updates for British farmers.",
                canonical_url=f"{SITE_URL}/{section_id}/",
                body_content=section_body,
            )
        )
        print(f"  ✅ AMP {title}")

    print(f"\n📁 Built in {OUTPUT_DIR}")
    print(f"   Using base path: {BASE_PATH}")
    print("🚀 Ready to deploy!")

if __name__ == "__main__":
    main()