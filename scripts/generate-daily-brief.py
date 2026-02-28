#!/usr/bin/env python3
"""Generate daily-brief.md from fetched data files"""

import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_FILE = PROJECT_ROOT / "content" / "daily-brief.md"


def load_json(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def weather_section(weather):
    if not weather:
        return ""
    lines = ["## 🌦 Today's Weather Risks\n"]
    for region, info in weather.get("regions", {}).items():
        alerts = info.get("alerts", [])
        if alerts:
            for alert in alerts:
                level = alert.get("level", "").upper()
                msg = alert.get("message", "")
                impact = alert.get("farm_impact", "")
                lines.append(f"- **{region.replace('_', ' ').title()}** ({level}): {msg}. *{impact}*")
        else:
            temp = info.get("temp", "?")
            lines.append(f"- **{region.replace('_', ' ').title()}**: {temp}°C, no alerts")
    return "\n".join(lines)


def markets_section(market):
    if not market:
        return ""
    lines = ["## 📈 Market Prices\n"]
    commodities = market.get("commodities", {})
    if "wheat" in commodities:
        w = commodities["wheat"]
        change = w.get("feed_change", 0)
        arrow = "↑" if change > 0 else ("↓" if change < 0 else "→")
        lines.append(f"- **Feed Wheat**: £{w.get('feed_price', '?')}/t {arrow} ({change:+.1f})")
    if "barley" in commodities:
        b = commodities["barley"]
        change = b.get("feed_change", 0)
        arrow = "↑" if change > 0 else ("↓" if change < 0 else "→")
        lines.append(f"- **Feed Barley**: £{b.get('feed_price', '?')}/t {arrow} ({change:+.1f})")
    if "rapeseed" in commodities:
        r = commodities["rapeseed"]
        change = r.get("change", 0)
        arrow = "↑" if change > 0 else ("↓" if change < 0 else "→")
        lines.append(f"- **Rapeseed**: £{r.get('price', '?')}/t {arrow} ({change:+.1f})")
    if "milk" in commodities:
        m = commodities["milk"]
        lines.append(f"- **Milk**: {m.get('avg_price', '?')}p/L")
    return "\n".join(lines)


def grants_section(grants):
    if not grants:
        return ""
    lines = ["## 💰 Grant Updates\n"]
    for grant in grants.get("new_grants", [])[:3]:
        scheme = grant.get("scheme", "")
        update = grant.get("update", "")
        deadline = grant.get("deadline")
        amount = grant.get("amount", "")
        deadline_str = f" | **Deadline: {deadline}**" if deadline else ""
        lines.append(f"- **{scheme}** ({amount}): {update}{deadline_str}")
    return "\n".join(lines)


def main():
    today = datetime.now(timezone.utc)
    date_str = today.strftime("%d %B %Y").lstrip("0")
    iso_str = today.strftime("%Y-%m-%dT%H:%M:%SZ")

    weather = load_json(DATA_DIR / "weather-risks.json")
    market = load_json(DATA_DIR / "market-data.json")
    grants = load_json(DATA_DIR / "grant-updates.json")

    weather_md = weather_section(weather)
    market_md = markets_section(market)
    grants_md = grants_section(grants)

    content = f"""---
title: "Daily Farm Brief – {date_str}"
date: {iso_str}
description: "Daily UK farming update: weather risks, market prices, grant deadlines"
tags: ["daily-brief", "uk-farming", "weather", "markets", "grants"]
type: brief
---

# 📰 Daily Farm Brief – {date_str}

> Your 3-minute roundup of today's important farming updates.

---

{weather_md}

---

{market_md}

---

{grants_md}

---

*Updated automatically at 06:00 UTC. [Browse all sections →](/Nole/)*
"""

    OUTPUT_FILE.write_text(content)
    print(f"✅ Daily brief generated: {OUTPUT_FILE}")
    print(f"   Date: {date_str}")


if __name__ == "__main__":
    main()
