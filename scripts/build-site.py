#!/usr/bin/env python3
"""Build UK Farm Blog – professional design, AdSense monetisation, policy pages."""

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
CONTENT_DIR  = PROJECT_ROOT / "content"
OUTPUT_DIR   = PROJECT_ROOT / "_site"
DATA_DIR     = PROJECT_ROOT / "data"

# ── Paths ─────────────────────────────────────────────────────────────────────
# Support a custom domain via CNAME file; fall back to /Nole subpath for
# GitHub Pages when no custom domain is configured.
_cname_file        = PROJECT_ROOT / "CNAME"
_custom_domain     = _cname_file.read_text().strip() if _cname_file.exists() else ""
_has_custom_domain = bool(_custom_domain)
_default_base      = "" if _has_custom_domain else "/Nole"
_default_site_url  = f"https://{_custom_domain}" if _has_custom_domain else "https://vtsochev45-web.github.io/Nole"
BASE_PATH = os.environ.get("SITE_BASE_PATH", _default_base).rstrip("/")

SITE_URL      = os.environ.get("SITE_URL",      _default_site_url).rstrip("/")
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "privacy@britfarmers.com")

# ── Monetisation ──────────────────────────────────────────────────────────────
# AdSense publisher ID – verified after merge 19.  The pub ID is inherently
# public (it appears verbatim in every served HTML page).
ADSENSE_PUB_ID           = os.environ.get("ADSENSE_PUB_ID",           "ca-pub-9535677982209167")
ADSENSE_SLOT_HOME_TOP    = os.environ.get("ADSENSE_SLOT_HOME_TOP",    "0000000001")
ADSENSE_SLOT_HOME_MID    = os.environ.get("ADSENSE_SLOT_HOME_MID",    "0000000002")
ADSENSE_SLOT_SECTION_TOP = os.environ.get("ADSENSE_SLOT_SECTION_TOP", "0000000003")
ADSENSE_SLOT_ARTICLE_MID = os.environ.get("ADSENSE_SLOT_ARTICLE_MID", "0000000004")

# AdSense <head> block – verification meta tag + async script (Auto Ads enabled)
ADSENSE_HEAD = f"""    <!-- Google AdSense – site verification & Auto Ads -->
    <meta name="google-adsense-account" content="{ADSENSE_PUB_ID}">
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_PUB_ID}"
            crossorigin="anonymous"></script>"""

# AMP Auto Ads
AMP_AUTO_ADS_SCRIPT = """    <script async custom-element="amp-auto-ads"
        src="https://cdn.ampproject.org/v0/amp-auto-ads-0.1.js">
    </script>"""
AMP_AUTO_ADS_TAG = f"""<amp-auto-ads type="adsense" data-ad-client="{ADSENSE_PUB_ID}"></amp-auto-ads>"""

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

# ── Affiliate partners ────────────────────────────────────────────────────────
_AMAZON_TAG = os.environ.get("AMAZON_AFFILIATE_TAG", "")
_AMAZON_URL = (
    f"https://www.amazon.co.uk/farm-supplies/?tag={_AMAZON_TAG}"
    if _AMAZON_TAG else "https://www.amazon.co.uk/farm-supplies/"
)
AFFILIATE_PARTNERS = [
    ("Farmers Weekly Shop",    "https://shop.fwi.co.uk/",                    "Books, guides & agronomy resources"),
    ("Amazon Farm Supplies",   _AMAZON_URL,                                  "Equipment, tools & PPE"),
    ("Farmers Guardian",       "https://www.farmersguardian.com/",            "News, reports & industry data"),
    ("AHDB MarketPlace",       "https://ahdb.org.uk/",                        "Free market data & benchmarking"),
    ("NFU Mutual Insurance",   "https://www.nfumutual.co.uk/farm-insurance/", "Farm insurance & risk cover"),
]

def build_affiliate_strip():
    items = "".join(
        f'<a href="{url}" class="partner-item" target="_blank" rel="noopener sponsored">'
        f'<strong>{name}</strong><span>{desc}</span></a>'
        for name, url, desc in AFFILIATE_PARTNERS
    )
    return f"""<section class="partners-strip" aria-label="Trusted Partners">
  <div class="partners-inner">
    <span class="partners-label">🤝 Trusted Partners</span>
    {items}
  </div>
</section>"""

# ── Sections ──────────────────────────────────────────────────────────────────
SECTIONS = [
    ("daily-brief", "🗞 Daily Farm Brief",  "Daily farming updates"),
    ("weather",     "🌦 Weather Alerts",     "Weather risks & forecasts"),
    ("grants",      "💰 Grants & Funding",   "Available grants & deadlines"),
    ("markets",     "📈 Market Prices",      "Livestock & commodity prices"),
    ("equipment",   "🚜 Equipment",          "Machinery & tech updates"),
    ("livestock",   "🐄 Livestock",          "Animal health & markets"),
    ("crops",       "🌾 Crops",             "Crop management & agronomy"),
    ("seasonal",    "📅 Seasonal Tasks",     "Monthly farming checklists"),
    ("tools",       "📊 Tools",             "Calculators & resources"),
    ("community",   "👥 Community",          "Ask questions, share stories"),
]

ICONS = {
    "daily-brief": "📰", "weather": "🌦", "grants": "💰", "markets": "📈",
    "equipment": "🚜", "livestock": "🐄", "crops": "🌾", "seasonal": "📅",
    "tools": "🧰", "community": "👥",
}

def get_icon(section_id):
    return ICONS.get(section_id, "📋")

# ── Helpers ───────────────────────────────────────────────────────────────────
def md_to_html(text):
    if MARKDOWN_AVAILABLE:
        md = markdown.Markdown(extensions=["tables", "fenced_code"])
        return md.convert(text)
    text = re.sub(r'^# (.+)$',    r'<h1>\1</h1>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',   r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$',  r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return text

def get_content(file_path):
    path = PROJECT_ROOT / file_path
    if path.exists():
        content = path.read_text()
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                return parts[2].strip()
        return content
    return ""

# ── Common CSS ────────────────────────────────────────────────────────────────
COMMON_CSS = """
/* Reset & base */
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
:root {
  --navy:    #1a2f5a;
  --blue:    #2a5298;
  --green:   #2d6a27;
  --gold:    #e8a800;
  --light:   #f4f6fb;
  --white:   #ffffff;
  --grey:    #6b7280;
  --border:  #e5e7eb;
  --shadow:  0 2px 12px rgba(0,0,0,.08);
  --radius:  12px;
  --max-w:   1280px;
  --font:    'Segoe UI', system-ui, -apple-system, sans-serif;
}
html { scroll-behavior: smooth; }
body { font-family: var(--font); background: var(--light); color: #1f2937; line-height: 1.75; min-height: 100vh; }

/* Skip link */
.skip-link { position: absolute; top: -40px; left: 0; background: var(--gold); color: var(--navy); padding: 8px 16px; font-weight: 700; z-index: 9999; border-radius: 0 0 8px 0; text-decoration: none; transition: top .2s; }
.skip-link:focus { top: 0; }

/* Top bar */
.top-bar { background: var(--navy); color: rgba(255,255,255,.75); font-size: .78rem; padding: 6px 20px; display: flex; justify-content: space-between; align-items: center; }
.top-bar a { color: rgba(255,255,255,.75); text-decoration: none; }
.top-bar a:hover { color: #fff; }

/* Header */
header { background: linear-gradient(135deg, var(--navy) 0%, var(--blue) 100%); color: #fff; padding: 48px 20px 40px; text-align: center; }
.site-brand { display: inline-flex; align-items: center; gap: 12px; text-decoration: none; color: inherit; }
.site-brand h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -.5px; }
.site-tagline { margin-top: 8px; font-size: 1rem; color: rgba(255,255,255,.8); }
.header-badge { display: inline-block; background: var(--gold); color: var(--navy); font-size: .72rem; font-weight: 700; padding: 2px 10px; border-radius: 20px; margin-top: 10px; letter-spacing: .5px; text-transform: uppercase; }

/* Navigation */
nav { background: var(--navy); border-top: 3px solid var(--gold); position: sticky; top: 0; z-index: 200; }
.nav-inner { max-width: var(--max-w); margin: 0 auto; display: flex; flex-wrap: wrap; align-items: center; padding: 0 16px; }
nav a { color: rgba(255,255,255,.85); text-decoration: none; font-size: .85rem; font-weight: 500; padding: 14px 12px; display: inline-block; border-bottom: 3px solid transparent; transition: all .2s; }
nav a:hover, nav a.active { color: #fff; border-bottom-color: var(--gold); }
nav a.home-link { font-weight: 700; }

/* Cookie banner */
#cookie-banner { position: fixed; bottom: 0; left: 0; right: 0; background: var(--navy); color: #fff; padding: 16px 24px; display: flex; flex-wrap: wrap; align-items: center; gap: 12px; z-index: 9998; font-size: .9rem; }
#cookie-banner p { flex: 1 1 300px; }
#cookie-banner a { color: var(--gold); }
.cookie-btn { background: var(--gold); color: var(--navy); border: none; padding: 10px 24px; border-radius: 8px; font-weight: 700; cursor: pointer; font-size: .9rem; }
.cookie-btn.secondary { background: transparent; border: 1px solid rgba(255,255,255,.4); color: #fff; }

/* Main layout */
main { max-width: var(--max-w); margin: 0 auto; padding: 40px 20px; }

/* Hero */
.hero { background: linear-gradient(135deg, var(--green) 0%, #4a7c43 100%); color: #fff; padding: 48px; border-radius: var(--radius); margin-bottom: 48px; box-shadow: var(--shadow); }
.hero h2 { font-size: .85rem; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,.7); margin-bottom: 8px; }
.hero-title { font-size: 1.9rem; font-weight: 800; margin-bottom: 16px; }
.hero p { color: rgba(255,255,255,.9); max-width: 700px; }
.btn { display: inline-block; background: var(--gold); color: var(--navy); padding: 13px 28px; text-decoration: none; border-radius: 30px; font-weight: 700; margin-top: 20px; font-size: .95rem; transition: transform .15s, box-shadow .15s; }
.btn:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,.15); }
.btn-outline { background: transparent; border: 2px solid #fff; color: #fff; }

/* Section grid */
.section-heading { font-size: 1.3rem; font-weight: 700; color: var(--navy); margin-bottom: 24px; display: flex; align-items: center; gap: 8px; }
.sections-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 20px; }
.section-card { background: var(--white); border-radius: var(--radius); padding: 24px; box-shadow: var(--shadow); border: 1px solid var(--border); transition: transform .2s, box-shadow .2s; }
.section-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }
.section-card .card-icon { font-size: 2rem; margin-bottom: 12px; }
.section-card h3 { font-size: 1rem; font-weight: 700; color: var(--navy); margin-bottom: 6px; }
.section-card p { font-size: .875rem; color: var(--grey); margin-bottom: 16px; }
.card-btn { display: inline-block; background: var(--navy); color: #fff; padding: 8px 18px; text-decoration: none; border-radius: 20px; font-size: .82rem; font-weight: 600; transition: background .2s; }
.card-btn:hover { background: var(--blue); }

/* Content page */
.content-wrap { background: var(--white); border-radius: var(--radius); padding: 48px; max-width: 860px; margin: 0 auto; box-shadow: var(--shadow); border: 1px solid var(--border); }
.content-wrap h1 { color: var(--navy); font-size: 2rem; font-weight: 800; margin-bottom: 24px; padding-bottom: 20px; border-bottom: 2px solid var(--border); }
.content-wrap h2 { color: var(--green); font-size: 1.3rem; font-weight: 700; margin: 36px 0 16px; padding-left: 14px; border-left: 4px solid var(--gold); }
.content-wrap h3 { color: var(--navy); font-size: 1.1rem; font-weight: 600; margin: 24px 0 10px; }
.content-wrap p { margin-bottom: 16px; }
.content-wrap ul, .content-wrap ol { margin: 12px 0 20px 24px; }
.content-wrap li { margin-bottom: 6px; }
.content-wrap table { width: 100%; border-collapse: collapse; margin: 20px 0; }
.content-wrap th { background: var(--navy); color: #fff; padding: 10px 14px; text-align: left; font-size: .88rem; }
.content-wrap td { padding: 10px 14px; border-bottom: 1px solid var(--border); font-size: .9rem; }
.content-wrap tr:nth-child(even) td { background: var(--light); }
.content-wrap blockquote { border-left: 4px solid var(--gold); background: #fef9e7; padding: 14px 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }
.content-wrap a { color: var(--blue); }
.content-wrap strong { color: var(--navy); }
.back-link-wrap { text-align: center; margin-top: 40px; }

/* Ad containers */
.ad-container { margin: 28px 0; overflow: hidden; }
.ad-label { font-size: .72rem; color: var(--grey); text-align: center; margin-bottom: 4px; letter-spacing: .5px; }

/* Partners strip */
.partners-strip { background: var(--navy); padding: 18px 20px; margin-top: 48px; border-radius: var(--radius); }
.partners-inner { max-width: var(--max-w); margin: 0 auto; display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
.partners-label { color: rgba(255,255,255,.6); font-size: .8rem; font-weight: 600; text-transform: uppercase; letter-spacing: .5px; }
.partner-item { display: flex; flex-direction: column; background: rgba(255,255,255,.08); border-radius: 8px; padding: 10px 16px; text-decoration: none; transition: background .2s; }
.partner-item:hover { background: rgba(255,255,255,.15); }
.partner-item strong { color: #fff; font-size: .85rem; }
.partner-item span { color: rgba(255,255,255,.6); font-size: .75rem; }

/* Footer */
footer { background: var(--navy); color: rgba(255,255,255,.75); padding: 60px 20px 32px; margin-top: 64px; }
.footer-inner { max-width: var(--max-w); margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 40px; }
.footer-col h4 { color: #fff; font-size: .9rem; font-weight: 700; text-transform: uppercase; letter-spacing: .5px; margin-bottom: 14px; }
.footer-col ul { list-style: none; }
.footer-col li { margin-bottom: 8px; }
.footer-col a { color: rgba(255,255,255,.65); text-decoration: none; font-size: .875rem; transition: color .2s; }
.footer-col a:hover { color: #fff; }
.footer-col p { font-size: .875rem; line-height: 1.6; }
.footer-bottom { max-width: var(--max-w); margin: 40px auto 0; padding-top: 24px; border-top: 1px solid rgba(255,255,255,.12); display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; font-size: .8rem; color: rgba(255,255,255,.5); }
.footer-bottom a { color: rgba(255,255,255,.5); text-decoration: none; margin-left: 16px; }
.footer-bottom a:hover { color: #fff; }

/* Policy pages */
.policy-page { background: var(--white); border-radius: var(--radius); padding: 48px; max-width: 860px; margin: 40px auto; box-shadow: var(--shadow); }
.policy-page h1 { color: var(--navy); font-size: 2rem; font-weight: 800; margin-bottom: 8px; }
.policy-page .policy-date { color: var(--grey); font-size: .875rem; margin-bottom: 32px; }
.policy-page h2 { color: var(--navy); font-size: 1.2rem; font-weight: 700; margin: 32px 0 12px; }
.policy-page p, .policy-page li { font-size: .95rem; line-height: 1.75; color: #374151; }
.policy-page ul { margin: 12px 0 16px 24px; }
.policy-page a { color: var(--blue); }

/* Responsive */
@media (max-width: 768px) {
  .hero { padding: 28px 20px; }
  .hero-title { font-size: 1.5rem; }
  .content-wrap { padding: 24px 16px; }
  .policy-page { padding: 24px 16px; }
  .footer-inner { grid-template-columns: 1fr 1fr; }
  nav a { padding: 11px 8px; font-size: .8rem; }
}
@media (max-width: 480px) {
  .site-brand h1 { font-size: 1.6rem; }
  .sections-grid { grid-template-columns: 1fr 1fr; }
  .footer-inner { grid-template-columns: 1fr; }
}
"""

COOKIE_BANNER_JS = """
<script>
(function(){
  if(localStorage.getItem('cookies_ok')) return;
  var b = document.getElementById('cookie-banner');
  if(b) b.style.display='flex';
  var ok = document.getElementById('cookie-accept');
  var no = document.getElementById('cookie-decline');
  function hide(){ if(b) b.style.display='none'; }
  if(ok) ok.addEventListener('click', function(){ localStorage.setItem('cookies_ok','1'); hide(); });
  if(no) no.addEventListener('click', function(){ hide(); });
})();
</script>
"""

COOKIE_BANNER_HTML = f"""<div id="cookie-banner" style="display:none" role="dialog" aria-live="polite" aria-label="Cookie consent">
  <p>🍪 We use cookies and show ads to keep this site free. By clicking <strong>Accept</strong> you consent to our use of cookies and advertising. Read our <a href="{BASE_PATH}/privacy-policy/">Privacy Policy</a> and <a href="{BASE_PATH}/cookie-policy/">Cookie Policy</a>.</p>
  <button class="cookie-btn" id="cookie-accept">Accept All</button>
  <button class="cookie-btn secondary" id="cookie-decline">Decline</button>
</div>"""

def build_nav(active_id=""):
    links = f'<a href="{BASE_PATH}/" class="home-link{"" if active_id else " active"}">🌾 Home</a>'
    for sid, stitle, _ in SECTIONS:
        label = stitle.split(" ", 1)[1]
        icon  = stitle.split(" ", 1)[0]
        active = ' class="active"' if sid == active_id else ""
        links += f'<a href="{BASE_PATH}/{sid}/"{active}>{icon} {label}</a>'
    return f'<nav aria-label="Main navigation"><div class="nav-inner">{links}</div></nav>'

def build_footer():
    section_links = "\n".join(
        f'<li><a href="{BASE_PATH}/{sid}/">{title.split(" ", 1)[1]}</a></li>'
        for sid, title, _ in SECTIONS[:5]
    )
    section_links2 = "\n".join(
        f'<li><a href="{BASE_PATH}/{sid}/">{title.split(" ", 1)[1]}</a></li>'
        for sid, title, _ in SECTIONS[5:]
    )
    _now  = datetime.now()
    today = _now.strftime('%d %B %Y')
    return f"""<footer>
  <div class="footer-inner">
    <div class="footer-col">
      <h4>🌾 UK Farm Blog</h4>
      <p>Daily news, grants, market prices and practical guides for British farmers. Updated every morning.</p>
    </div>
    <div class="footer-col">
      <h4>Sections</h4>
      <ul>{section_links}</ul>
    </div>
    <div class="footer-col">
      <h4>More</h4>
      <ul>{section_links2}</ul>
    </div>
    <div class="footer-col">
      <h4>Legal</h4>
      <ul>
        <li><a href="{BASE_PATH}/privacy-policy/">Privacy Policy</a></li>
        <li><a href="{BASE_PATH}/terms-of-use/">Terms of Use</a></li>
        <li><a href="{BASE_PATH}/cookie-policy/">Cookie Policy</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© {_now.year} UK Farm Blog · Updated {today}</span>
    <span>
      <a href="{BASE_PATH}/privacy-policy/">Privacy</a>
      <a href="{BASE_PATH}/terms-of-use/">Terms</a>
      <a href="{BASE_PATH}/cookie-policy/">Cookies</a>
    </span>
  </div>
</footer>"""

def build_head(title, description="Daily farming updates for British farmers", canonical=""):
    canon_tag = f'<link rel="canonical" href="{canonical}">' if canonical else ""
    return f"""<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{description}">
    {canon_tag}
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:type" content="website">
    <meta name="theme-color" content="#1a2f5a">
    {ADSENSE_HEAD}
    <style>{COMMON_CSS}</style>
</head>"""

def build_page(title, description, canonical, body_html, active_section=""):
    return f"""<!DOCTYPE html>
<html lang="en">
{build_head(title, description, canonical)}
<body>
<a href="#main-content" class="skip-link">Skip to main content</a>
<div class="top-bar">
  <span>🇬🇧 Practical advice for British farmers · Updated daily</span>
  <span><a href="{BASE_PATH}/privacy-policy/">Privacy</a> · <a href="{BASE_PATH}/cookie-policy/">Cookies</a></span>
</div>
<header>
  <a href="{BASE_PATH}/" class="site-brand">
    <h1>🌾 UK Farm Blog</h1>
  </a>
  <p class="site-tagline">Grants · Markets · Weather · Practical Guides</p>
  <span class="header-badge">Updated Daily</span>
</header>
{build_nav(active_section)}
{COOKIE_BANNER_HTML}
<main id="main-content">
{body_html}
</main>
{build_affiliate_strip()}
{build_footer()}
{COOKIE_BANNER_JS}
</body>
</html>"""

# ── Page builders ─────────────────────────────────────────────────────────────
def build_homepage():
    brief_content = get_content("content/daily-brief.md")[:700]

    cards_html = ""
    for section_id, title, desc in SECTIONS:
        icon  = title.split(" ", 1)[0]
        label = title.split(" ", 1)[1]
        cards_html += f"""<div class="section-card">
  <div class="card-icon">{icon}</div>
  <h3>{label}</h3>
  <p>{desc}</p>
  <a href="{BASE_PATH}/{section_id}/" class="card-btn">Explore →</a>
</div>"""

    body = f"""
{build_ad_unit(ADSENSE_SLOT_HOME_TOP, "Top advertisement")}
<div class="hero">
  <h2>📰 Today's Farm Brief</h2>
  <div class="hero-content">{md_to_html(brief_content)}</div>
  <a href="{BASE_PATH}/daily-brief/" class="btn">Read Full Brief →</a>
</div>
{build_ad_unit(ADSENSE_SLOT_HOME_MID, "Mid-page advertisement")}
<div class="section-heading">📂 Browse Sections</div>
<div class="sections-grid">
  {cards_html}
</div>"""

    return build_page(
        title="UK Farm Blog – Daily Farming Updates for British Farmers",
        description="Daily grants, market prices, weather alerts and practical guides for UK farmers. Updated every morning.",
        canonical=f"{SITE_URL}/",
        body_html=body,
        active_section="",
    )

def build_section_page(section_id, title, desc):
    content = ""
    for path in [f"content/{section_id}/latest.md", f"content/{section_id}/index.md", f"content/{section_id}.md"]:
        if (PROJECT_ROOT / path).exists():
            content = get_content(path)
            break

    if not content:
        content = f"<p>{title} content coming soon. Check back daily for updates.</p>"

    icon  = title.split(" ", 1)[0]
    label = title.split(" ", 1)[1]

    content_html = md_to_html(content)
    content_html = content_html.replace('href="./', f'href="{BASE_PATH}/')

    body = f"""
{build_ad_unit(ADSENSE_SLOT_SECTION_TOP, "Top advertisement")}
<div class="content-wrap">
  <h1>{icon} {label}</h1>
  {content_html}
  {build_ad_unit(ADSENSE_SLOT_ARTICLE_MID, "Mid-article advertisement")}
  <div class="back-link-wrap">
    <a href="{BASE_PATH}/" class="btn">← Back to Home</a>
  </div>
</div>"""

    return build_page(
        title=f"{label} – UK Farm Blog",
        description=f"{desc} — practical daily updates for British farmers.",
        canonical=f"{SITE_URL}/{section_id}/",
        body_html=body,
        active_section=section_id,
    )

def build_privacy_policy_page():
    today = datetime.now().strftime('%d %B %Y')
    body = f"""<div class="policy-page">
  <h1>Privacy Policy</h1>
  <p class="policy-date">Last updated: {today}</p>

  <h2>1. Who We Are</h2>
  <p>UK Farm Blog ("we", "us", "our") is operated at <strong>{SITE_URL}</strong>. We provide daily farming news, market data, grants information and practical guides for British farmers. You can contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

  <h2>2. Information We Collect</h2>
  <p>We do not require you to create an account or submit personal information to read our content. Information that may be collected includes:</p>
  <ul>
    <li><strong>Log data</strong> – your browser type, pages visited, time of visit, referring URL, and IP address (collected automatically by our hosting provider).</li>
    <li><strong>Cookies</strong> – small text files placed on your device by us or third parties (see Section 4).</li>
    <li><strong>Contact enquiries</strong> – if you contact us by email, we keep the correspondence.</li>
  </ul>

  <h2>3. How We Use Your Information</h2>
  <ul>
    <li>To deliver and improve our content and services.</li>
    <li>To display relevant advertising through Google AdSense (see Section 5).</li>
    <li>To understand how visitors use the site (analytics).</li>
    <li>To respond to contact enquiries.</li>
  </ul>

  <h2>4. Cookies</h2>
  <p>We use first-party and third-party cookies. Third-party services that may set cookies include:</p>
  <ul>
    <li><strong>Google AdSense</strong> – to serve relevant advertisements. Google may use cookies to personalise ads based on your interests. You can opt out via <a href="https://adssettings.google.com/" target="_blank" rel="noopener">Google Ad Settings</a>.</li>
    <li><strong>Google Analytics</strong> – to measure site traffic anonymously.</li>
  </ul>
  <p>You can manage or disable cookies in your browser settings. Some features may not function correctly if cookies are disabled. See our full <a href="{BASE_PATH}/cookie-policy/">Cookie Policy</a> for details.</p>

  <h2>5. Google AdSense & Advertising</h2>
  <p>This site uses Google AdSense (publisher ID: {ADSENSE_PUB_ID}) to display advertisements. Google uses cookies to serve ads based on your prior visits to this and other websites. You may opt out of personalised advertising at <a href="https://www.google.com/settings/ads" target="_blank" rel="noopener">www.google.com/settings/ads</a>.</p>
  <p>Advertisements are clearly labelled. We do not control the content of third-party advertisements.</p>

  <h2>6. Affiliate Links</h2>
  <p>Some links on this site are affiliate links. If you purchase through these links, we may earn a small commission at no extra cost to you. All affiliate links are marked <code>rel="sponsored"</code>.</p>

  <h2>7. Your Rights (UK GDPR)</h2>
  <p>Under UK GDPR you have the right to: access the personal data we hold about you; request correction or erasure; object to processing; restrict processing; and data portability. To exercise any right, email <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>. If you are unhappy with our handling of your data, you may complain to the <a href="https://ico.org.uk/" target="_blank" rel="noopener">Information Commissioner's Office</a>.</p>

  <h2>8. Data Retention</h2>
  <p>Server log files are retained for up to 90 days. Contact enquiries are retained for 2 years or until you request deletion.</p>

  <h2>9. Third-Party Links</h2>
  <p>Our site links to external websites. We are not responsible for the privacy practices or content of those sites. We encourage you to review their privacy policies.</p>

  <h2>10. Children's Privacy</h2>
  <p>Our service is not directed at children under 13. We do not knowingly collect personal information from children under 13.</p>

  <h2>11. Changes to This Policy</h2>
  <p>We may update this Privacy Policy. The "Last updated" date at the top of this page will reflect any changes. Continued use of the site after changes constitutes acceptance.</p>

  <h2>12. Contact</h2>
  <p>For any privacy queries, contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

  <div class="back-link-wrap" style="margin-top:40px">
    <a href="{BASE_PATH}/" class="btn">← Back to Home</a>
  </div>
</div>"""
    return build_page(
        title="Privacy Policy – UK Farm Blog",
        description="Privacy Policy for UK Farm Blog – how we collect, use and protect your data.",
        canonical=f"{SITE_URL}/privacy-policy/",
        body_html=body,
    )

def build_terms_page():
    today = datetime.now().strftime('%d %B %Y')
    body = f"""<div class="policy-page">
  <h1>Terms of Use</h1>
  <p class="policy-date">Last updated: {today}</p>

  <h2>1. Acceptance</h2>
  <p>By accessing UK Farm Blog at <strong>{SITE_URL}</strong> you agree to these Terms of Use. If you do not agree, please do not use the site.</p>

  <h2>2. Purpose of the Site</h2>
  <p>UK Farm Blog provides general information and commentary about farming in the United Kingdom, including market prices, grants, weather and practical guides. The content is for informational purposes only and does not constitute professional agricultural, legal, financial or veterinary advice. Always consult a qualified professional before acting on any information found on this site.</p>

  <h2>3. Intellectual Property</h2>
  <p>All original content on this site (text, graphics, layout) is the property of UK Farm Blog unless otherwise stated and is protected by copyright. You may share short excerpts with a clear attribution and a link back to the original article. You may not reproduce full articles or use content commercially without prior written permission.</p>

  <h2>4. Advertising & Affiliate Links</h2>
  <p>This site displays advertisements served by Google AdSense and may contain affiliate links. Clicking an affiliate link and making a purchase may earn us a small commission. This does not affect the price you pay and we only link to products and services we consider relevant to our readers.</p>

  <h2>5. Accuracy of Information</h2>
  <p>We strive to keep information accurate and up to date. Market prices and grant schemes change frequently; always verify critical information with official sources such as the Rural Payments Agency, AHDB, or your local farming advisor. UK Farm Blog accepts no liability for decisions made based on content published on this site.</p>

  <h2>6. External Links</h2>
  <p>We link to third-party websites for reference. We are not responsible for the content, accuracy or privacy practices of external sites.</p>

  <h2>7. Limitation of Liability</h2>
  <p>To the maximum extent permitted by law, UK Farm Blog shall not be liable for any direct, indirect, incidental or consequential loss or damage arising from the use of, or inability to use, this site or its content.</p>

  <h2>8. Changes to Terms</h2>
  <p>We reserve the right to update these Terms at any time. The "Last updated" date above will be revised accordingly. Continued use of the site after changes constitutes acceptance of the revised Terms.</p>

  <h2>9. Governing Law</h2>
  <p>These Terms are governed by the laws of England and Wales. Any disputes shall be subject to the exclusive jurisdiction of the courts of England and Wales.</p>

  <h2>10. Contact</h2>
  <p>For questions about these Terms, contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>.</p>

  <div class="back-link-wrap" style="margin-top:40px">
    <a href="{BASE_PATH}/" class="btn">← Back to Home</a>
  </div>
</div>"""
    return build_page(
        title="Terms of Use – UK Farm Blog",
        description="Terms of Use for UK Farm Blog.",
        canonical=f"{SITE_URL}/terms-of-use/",
        body_html=body,
    )

def build_cookie_policy_page():
    today = datetime.now().strftime('%d %B %Y')
    body = f"""<div class="policy-page">
  <h1>Cookie Policy</h1>
  <p class="policy-date">Last updated: {today}</p>

  <h2>What Are Cookies?</h2>
  <p>Cookies are small text files stored on your device when you visit a website. They are widely used to make websites work efficiently and to provide information to the website owner.</p>

  <h2>How We Use Cookies</h2>
  <p>UK Farm Blog uses cookies for the following purposes:</p>

  <h2>Essential Cookies</h2>
  <p>These cookies are necessary for the site to function and cannot be disabled.</p>
  <ul>
    <li><strong>cookies_ok</strong> – stores your cookie consent preference (first-party, session).</li>
  </ul>

  <h2>Advertising Cookies (Google AdSense)</h2>
  <p>We use Google AdSense (publisher ID: {ADSENSE_PUB_ID}) to display advertisements. Google and its partners may use cookies to serve ads based on your browsing behaviour.</p>
  <ul>
    <li><strong>DSID, IDE, NID</strong> – DoubleClick/Google advertising cookies used to serve relevant ads and measure ad performance.</li>
    <li><strong>__gads, __gpi</strong> – Google AdSense cookies used to measure engagement with advertisements.</li>
  </ul>
  <p>You can opt out of personalised advertising at <a href="https://adssettings.google.com/" target="_blank" rel="noopener">Google Ad Settings</a> or via the <a href="https://optout.networkadvertising.org/" target="_blank" rel="noopener">NAI opt-out tool</a>.</p>

  <h2>Analytics Cookies</h2>
  <p>If enabled, Google Analytics sets cookies (_ga, _gid) to collect anonymous usage statistics. These help us understand how visitors use the site so we can improve it.</p>

  <h2>Managing Cookies</h2>
  <p>You can control cookies through your browser settings:</p>
  <ul>
    <li><a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener">Chrome</a></li>
    <li><a href="https://support.mozilla.org/en-US/kb/cookies-information-websites-store-on-your-computer" target="_blank" rel="noopener">Firefox</a></li>
    <li><a href="https://support.apple.com/guide/safari/manage-cookies-sfri11471/" target="_blank" rel="noopener">Safari</a></li>
    <li><a href="https://support.microsoft.com/en-us/windows/manage-cookies-in-microsoft-edge" target="_blank" rel="noopener">Edge</a></li>
  </ul>
  <p>Disabling cookies may affect the functionality of some features on this site and the relevance of advertisements shown to you.</p>

  <h2>Contact</h2>
  <p>For questions about our use of cookies, contact us at <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a> or see our <a href="{BASE_PATH}/privacy-policy/">Privacy Policy</a>.</p>

  <div class="back-link-wrap" style="margin-top:40px">
    <a href="{BASE_PATH}/" class="btn">← Back to Home</a>
  </div>
</div>"""
    return build_page(
        title="Cookie Policy – UK Farm Blog",
        description="Cookie Policy for UK Farm Blog – what cookies we use and how to manage them.",
        canonical=f"{SITE_URL}/cookie-policy/",
        body_html=body,
    )

def build_amp_page(title, description, canonical_url, body_content):
    return f"""<!DOCTYPE html>
<html ⚡ lang="en">
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
        body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 0; padding: 16px; color: #1f2937; line-height: 1.7; max-width: 800px; margin: 0 auto; }}
        h1 {{ font-size: 1.6rem; color: #1a2f5a; margin-bottom: 8px; }}
        h2 {{ font-size: 1.25rem; color: #2d6a27; margin: 24px 0 10px; }}
        a {{ color: #2a5298; }}
        .back-link {{ display: inline-block; margin-top: 24px; background: #e8a800; color: #1a2f5a; padding: 10px 20px; text-decoration: none; border-radius: 20px; font-weight: 700; }}
    </style>
</head>
<body>
    {AMP_AUTO_ADS_TAG}
    {body_content}
</body>
</html>"""

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("🔨 Building UK Farm Blog (professional edition)…")
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Copy CNAME to _site so GitHub Pages preserves the custom domain
    if _has_custom_domain:
        import shutil
        shutil.copy(_cname_file, OUTPUT_DIR / "CNAME")
        print(f"✅ CNAME ({_custom_domain})")

    # Homepage
    (OUTPUT_DIR / "index.html").write_text(build_homepage())
    print("✅ Homepage")

    # Section pages
    for section_id, title, desc in SECTIONS:
        section_dir = OUTPUT_DIR / section_id
        section_dir.mkdir(exist_ok=True)
        (section_dir / "index.html").write_text(build_section_page(section_id, title, desc))
        print(f"  ✅ {title}")

    # Policy pages (required by Google AdSense)
    for slug, builder in [
        ("privacy-policy", build_privacy_policy_page),
        ("terms-of-use",   build_terms_page),
        ("cookie-policy",  build_cookie_policy_page),
    ]:
        d = OUTPUT_DIR / slug
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(builder())
        print(f"✅ {slug}")

    # Sitemap
    today_iso = datetime.now().strftime('%Y-%m-%d')
    urls  = [f"{SITE_URL}/"]
    urls += [f"{SITE_URL}/{sid}/" for sid, _, _ in SECTIONS]
    urls += [f"{SITE_URL}/privacy-policy/", f"{SITE_URL}/terms-of-use/", f"{SITE_URL}/cookie-policy/"]
    entries = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{today_iso}</lastmod><changefreq>daily</changefreq></url>"
        for u in urls
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n</urlset>\n"
    )
    (OUTPUT_DIR / "sitemap.xml").write_text(sitemap)
    print("✅ sitemap.xml")

    # robots.txt
    robots = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    (OUTPUT_DIR / "robots.txt").write_text(robots)
    print("✅ robots.txt")

    # Tools (copy with updated links)
    tools_src = PROJECT_ROOT / "content" / "tools"
    if tools_src.exists():
        tools_dir = OUTPUT_DIR / "tools"
        tools_dir.mkdir(exist_ok=True)
        for html_file in tools_src.glob("*.html"):
            content = html_file.read_text()
            content = content.replace('href="/', f'href="{BASE_PATH}/')
            content = content.replace('href="./', f'href="{BASE_PATH}/')
            (tools_dir / html_file.name).write_text(content)
            print(f"  ✅ Tool: {html_file.name}")

    # Community (copy with updated links)
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

    # AMP pages (homepage + each section)
    amp_dir = OUTPUT_DIR / "amp"
    amp_dir.mkdir(exist_ok=True)
    brief_content = get_content("content/daily-brief.md")[:700]
    today = datetime.now().strftime('%d %B %Y')
    home_body = f"""<h1>🌾 UK Farm Blog</h1>
    <p>Practical grants, markets &amp; weather updates for British farmers — every morning</p>
    <p><strong>📰 Today's Farm Brief – {today}</strong></p>
    {md_to_html(brief_content)}
    <p><a class="back-link" href="{SITE_URL}/">View full site</a></p>"""
    (amp_dir / "index.html").write_text(build_amp_page(
        title="UK Farm Blog – Daily Updates for British Farmers",
        description="Daily farming news, grants, market prices, weather alerts and practical guides for UK farmers.",
        canonical_url=f"{SITE_URL}/",
        body_content=home_body,
    ))
    print("✅ AMP Homepage")

    for section_id, title, desc in SECTIONS:
        content = ""
        for path in [f"content/{section_id}/latest.md", f"content/{section_id}/index.md", f"content/{section_id}.md"]:
            if (PROJECT_ROOT / path).exists():
                content = get_content(path)
                break
        icon  = title.split(" ", 1)[0]
        label = title.split(" ", 1)[1]
        section_body = f"""<h1>{icon} {label}</h1>
    <p>{desc}</p>
    {md_to_html(content) if content else f"<p>{label} content coming soon!</p>"}
    <p><a class="back-link" href="{SITE_URL}/{section_id}/">View full {label} page</a></p>"""
        section_amp_dir = OUTPUT_DIR / section_id / "amp"
        section_amp_dir.mkdir(parents=True, exist_ok=True)
        (section_amp_dir / "index.html").write_text(build_amp_page(
            title=f"{label} – UK Farm Blog",
            description=f"{desc} — practical daily updates for British farmers.",
            canonical_url=f"{SITE_URL}/{section_id}/",
            body_content=section_body,
        ))
        print(f"  ✅ AMP {title}")

    print(f"\n📁 Built in {OUTPUT_DIR}")
    print(f"   Base path: {BASE_PATH}")
    print(f"   Site URL:  {SITE_URL}")
    print(f"   AdSense:   {ADSENSE_PUB_ID}")
    print("🚀 Ready to deploy!")

if __name__ == "__main__":
    main()