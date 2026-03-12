#!/usr/bin/env python3
"""
WordPress Migration Export Script
Reads all content from the Jekyll site and produces:
  1. wordpress-export.xml  – WXR file importable via WordPress Tools > Import
  2. wordpress-migration.zip – ZIP archive containing the WXR file + all built _site HTML files
"""

import os
import re
import zipfile
from datetime import datetime, timezone
from xml.sax.saxutils import escape

# ── Paths ────────────────────────────────────────────────────────────────────
REPO_ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR  = os.path.join(REPO_ROOT, "content")
SITE_DIR     = os.path.join(REPO_ROOT, "_site")
CONFIG_FILE  = os.path.join(REPO_ROOT, "_config.yml")
THEME_DIR    = os.path.join(REPO_ROOT, "wordpress-theme")
OUTPUT_XML   = os.path.join(REPO_ROOT, "wordpress-export.xml")
OUTPUT_ZIP   = os.path.join(REPO_ROOT, "wordpress-migration.zip")

SITE_URL    = "https://vtsochev45-web.github.io/Nole"
SITE_TITLE  = "UK Farm Blog"
SITE_DESC   = "Daily updates for British farmers"


# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_front_matter(text):
    """Return (metadata_dict, body_text) from a YAML-front-matter markdown file."""
    meta = {}
    body = text
    m = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', text, re.DOTALL)
    if m:
        front, body = m.group(1), m.group(2)
        for line in front.splitlines():
            kv = re.match(r'^(\w[\w-]*):\s*(.*)', line)
            if kv:
                meta[kv.group(1)] = kv.group(2).strip().strip('"').strip("'")
    return meta, body


def markdown_to_html(md):
    """Minimal markdown → HTML converter (headings, bold, links, paragraphs)."""
    lines = md.splitlines()
    html_lines = []
    in_list = False
    in_table = False

    for line in lines:
        stripped = line.rstrip()

        # Horizontal rule
        if re.match(r'^---+$', stripped):
            if in_list:
                html_lines.append("</ul>"); in_list = False
            if in_table:
                html_lines.append("</table>"); in_table = False
            html_lines.append("<hr>")
            continue

        # Table rows (very basic)
        if re.match(r'^\|', stripped):
            if not in_table:
                html_lines.append("<table>"); in_table = True
            if re.match(r'^\|[-| :]+\|', stripped):
                continue  # separator row
            cells = [c.strip() for c in stripped.strip('|').split('|')]
            html_lines.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in cells) + "</tr>")
            continue
        elif in_table:
            html_lines.append("</table>"); in_table = False

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', stripped)
        if m:
            if in_list:
                html_lines.append("</ul>"); in_list = False
            lvl = len(m.group(1))
            html_lines.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue

        # Blockquote
        if stripped.startswith('> '):
            if in_list:
                html_lines.append("</ul>"); in_list = False
            html_lines.append(f"<blockquote><p>{inline(stripped[2:])}</p></blockquote>")
            continue

        # Unordered list
        m = re.match(r'^[-*]\s+(.*)', stripped)
        if m:
            if not in_list:
                html_lines.append("<ul>"); in_list = True
            html_lines.append(f"<li>{inline(m.group(1))}</li>")
            continue
        elif in_list and stripped == '':
            html_lines.append("</ul>"); in_list = False

        # Ordered list
        m = re.match(r'^\d+\.\s+(.*)', stripped)
        if m:
            html_lines.append(f"<li>{inline(m.group(1))}</li>")
            continue

        # Blank line
        if stripped == '':
            html_lines.append('')
            continue

        # Normal paragraph line
        html_lines.append(f"<p>{inline(stripped)}</p>")

    if in_list:
        html_lines.append("</ul>")
    if in_table:
        html_lines.append("</table>")

    return '\n'.join(html_lines)


def inline(text):
    """Apply inline markdown transforms: bold, italic, code, links, images."""
    # Bold
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.*?)__', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    # Images (before links)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1">', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text


def fmt_pubdate(iso_str, source=''):
    """Convert ISO 8601 string to RFC 2822 format for RSS pubDate."""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    except Exception:
        print(f"  WARNING: Could not parse date {iso_str!r}{' in ' + source if source else ''}; using current time")
        dt = datetime.now(timezone.utc)
    return dt.strftime('%a, %d %b %Y %H:%M:%S +0000')


def fmt_wp_date(iso_str, source=''):
    """Convert ISO 8601 string to WordPress post_date format."""
    try:
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    except Exception:
        print(f"  WARNING: Could not parse date {iso_str!r}{' in ' + source if source else ''}; using current time")
        dt = datetime.now(timezone.utc)
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def slugify(text):
    """Convert arbitrary text to a clean URL slug."""
    # Normalize to ASCII where possible (replace common accented/special chars)
    text = text.lower().strip()
    text = re.sub(r'[àáâãäå]', 'a', text)
    text = re.sub(r'[èéêë]', 'e', text)
    text = re.sub(r'[ìíîï]', 'i', text)
    text = re.sub(r'[òóôõö]', 'o', text)
    text = re.sub(r'[ùúûü]', 'u', text)
    text = re.sub(r'[ýÿ]', 'y', text)
    text = re.sub(r'[ñ]', 'n', text)
    text = re.sub(r'[ç]', 'c', text)
    # Replace non-alphanumeric characters (including &, ', –, etc.) with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Strip leading/trailing hyphens and collapse multiples
    text = text.strip('-')
    return text


def slug_from_filename(fname):
    """Derive a URL slug from a filename."""
    name = os.path.splitext(os.path.basename(fname))[0]
    # Strip leading date prefix (e.g. 2026-02-26-)
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', name)
    return slugify(name)


# ── Content discovery ────────────────────────────────────────────────────────

def title_from_body(body, fallback):
    """Extract the first # heading from markdown body, or return fallback."""
    m = re.search(r'^#\s+(.*)', body, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def collect_posts():
    """Return a list of post dicts from content/posts/*.md."""
    posts = []
    posts_dir = os.path.join(CONTENT_DIR, "posts")
    if not os.path.isdir(posts_dir):
        return posts
    for fname in sorted(os.listdir(posts_dir)):
        if not fname.endswith('.md'):
            continue
        path = os.path.join(posts_dir, fname)
        with open(path, encoding='utf-8') as f:
            raw = f.read()
        meta, body = parse_front_matter(raw)
        title = meta.get('title') or title_from_body(body, fname)
        posts.append({
            'type':    'post',
            'title':   title,
            'date':    meta.get('date', '2026-02-26T00:00:00Z'),
            'author':  meta.get('author', 'admin'),
            'desc':    meta.get('description', ''),
            'tags':    meta.get('tags', ''),
            'slug':    slug_from_filename(fname),
            'content': markdown_to_html(body),
        })
    return posts


def collect_pages():
    """Return a list of page dicts from content/**/*.md (excluding posts/)."""
    pages = []
    for dirpath, _dirs, files in os.walk(CONTENT_DIR):
        # Skip posts dir (handled separately)
        if os.path.basename(dirpath) == 'posts':
            continue
        for fname in sorted(files):
            if not fname.endswith('.md'):
                continue
            path = os.path.join(dirpath, fname)
            with open(path, encoding='utf-8') as f:
                raw = f.read()
            meta, body = parse_front_matter(raw)
            title = meta.get('title') or title_from_body(body, fname)
            rel = os.path.relpath(path, CONTENT_DIR)
            slug = re.sub(r'\.md$', '', rel).replace(os.sep, '/')
            pages.append({
                'type':    'page',
                'title':   title,
                'date':    meta.get('date', '2026-02-26T00:00:00Z'),
                'author':  meta.get('author', 'admin'),
                'desc':    meta.get('description', ''),
                'slug':    slug,
                'content': markdown_to_html(body),
            })
    return pages


# ── WXR generation ───────────────────────────────────────────────────────────

ITEM_TEMPLATE = """
    <item>
      <title>{title}</title>
      <link>{site_url}/{slug}/</link>
      <pubDate>{pubdate}</pubDate>
      <dc:creator>{author}</dc:creator>
      <description>{desc}</description>
      <content:encoded><![CDATA[{content}]]></content:encoded>
      <wp:post_date>{wp_date}</wp:post_date>
      <wp:post_date_gmt>{wp_date}</wp:post_date_gmt>
      <wp:comment_status>open</wp:comment_status>
      <wp:ping_status>open</wp:ping_status>
      <wp:post_name>{slug_safe}</wp:post_name>
      <wp:status>publish</wp:status>
      <wp:post_parent>0</wp:post_parent>
      <wp:menu_order>0</wp:menu_order>
      <wp:post_type>{post_type}</wp:post_type>
      <wp:post_password></wp:post_password>
      <wp:is_sticky>0</wp:is_sticky>
    </item>"""


def build_wxr(posts, pages):
    now_rfc = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    items = []

    for p in posts + pages:
        slug_safe = slugify(p['slug'])
        items.append(ITEM_TEMPLATE.format(
            title     = escape(p['title']),
            site_url  = SITE_URL,
            slug      = p['slug'],
            pubdate   = fmt_pubdate(p['date'], p['slug']),
            author    = escape(p['author']),
            desc      = escape(p['desc']),
            content   = p['content'],
            wp_date   = fmt_wp_date(p['date'], p['slug']),
            slug_safe = slug_safe,
            post_type = p['type'],
        ))

    xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<!-- WordPress WXR export generated by wordpress-export.py -->
<rss version="2.0"
  xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/"
  xmlns:content="http://purl.org/rss/1.0/modules/content/"
  xmlns:wfw="http://wellformedweb.org/CommentAPI/"
  xmlns:dc="http://purl.org/dc/elements/1.1/"
  xmlns:wp="http://wordpress.org/export/1.2/">
  <channel>
    <title>{escape(SITE_TITLE)}</title>
    <link>{SITE_URL}</link>
    <description>{escape(SITE_DESC)}</description>
    <pubDate>{now_rfc}</pubDate>
    <language>en-GB</language>
    <wp:wxr_version>1.2</wp:wxr_version>
    <wp:base_site_url>{SITE_URL}</wp:base_site_url>
    <wp:base_blog_url>{SITE_URL}</wp:base_blog_url>
    <wp:author>
      <wp:author_login>admin</wp:author_login>
      <wp:author_display_name>Nole</wp:author_display_name>
    </wp:author>
{''.join(items)}
  </channel>
</rss>
"""
    return xml


# ── ZIP creation ─────────────────────────────────────────────────────────────

def build_zip(xml_path):
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        # Add the WXR import file
        zf.write(xml_path, arcname="wordpress-export.xml")

        # Add all built _site files
        for dirpath, _dirs, files in os.walk(SITE_DIR):
            for fname in files:
                full_path = os.path.join(dirpath, fname)
                rel = os.path.relpath(full_path, REPO_ROOT)
                zf.write(full_path, arcname=rel)

        # Add the WordPress theme files
        if os.path.isdir(THEME_DIR):
            for dirpath, _dirs, files in os.walk(THEME_DIR):
                for fname in files:
                    full_path = os.path.join(dirpath, fname)
                    rel = os.path.relpath(full_path, REPO_ROOT)
                    zf.write(full_path, arcname=rel)

        # Add README with import instructions
        readme = (
            "WordPress Migration Package\n"
            "===========================\n\n"
            "Files included:\n"
            "  wordpress-export.xml  – Import via WordPress Admin > Tools > Import > WordPress\n"
            "  wordpress-theme/      – Custom WordPress theme matching the original site design\n"
            "  _site/                – Pre-built HTML pages (can be used as static reference)\n\n"
            "Theme installation steps:\n"
            "  1. Copy the wordpress-theme/ folder to wp-content/themes/ on your server.\n"
            "  2. Rename the folder to 'uk-farm-blog'.\n"
            "  3. In Appearance > Themes, activate 'UK Farm Blog'.\n"
            "  4. In Appearance > Menus, create a menu and assign it to Primary Menu.\n\n"
            "Content import steps:\n"
            "  1. In your WordPress admin panel go to Tools > Import.\n"
            "  2. Choose 'WordPress' and click 'Install Now' if prompted.\n"
            "  3. Click 'Run Importer', upload wordpress-export.xml and click 'Upload file and import'.\n"
            "  4. Assign imported posts to an existing user (or create one).\n"
            "  5. Click 'Submit'.\n\n"
            f"Source site: {SITE_URL}\n"
            f"Generated:   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
        )
        zf.writestr("README.txt", readme)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Collecting content...")
    posts = collect_posts()
    pages = collect_pages()
    print(f"  Found {len(posts)} posts, {len(pages)} pages")

    print("Generating WordPress WXR export file...")
    xml = build_wxr(posts, pages)
    with open(OUTPUT_XML, 'w', encoding='utf-8') as f:
        f.write(xml)
    print(f"  Written: {OUTPUT_XML}")

    print("Creating ZIP archive...")
    build_zip(OUTPUT_XML)
    zip_size = os.path.getsize(OUTPUT_ZIP)
    print(f"  Written: {OUTPUT_ZIP}  ({zip_size:,} bytes)")

    # List ZIP contents
    with zipfile.ZipFile(OUTPUT_ZIP) as zf:
        names = zf.namelist()
    print(f"\nZIP contents ({len(names)} files):")
    for n in names:
        print(f"  {n}")

    print("\nDone. Upload wordpress-export.xml via WordPress Admin > Tools > Import.")


if __name__ == '__main__':
    main()
