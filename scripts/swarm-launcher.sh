#!/bin/bash
# swarm-launcher.sh - Orchestrate 9-agent content swarm

cd "$(dirname "$0")/.."
LOG_FILE="logs/swarm-$(date +%Y%m%d-%H%M).log"
mkdir -p logs

echo "🚀 UK Farm Content Swarm Launching..." | tee "$LOG_FILE"
echo "Time: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Function to spawn subagent
spawn_agent() {
    local agent_id="$1"
    local agent_name="$2"
    local task="$3"
    local model="$4"
    
    echo "🤖 Spawning: $agent_name" | tee -a "$LOG_FILE"
    
    # Create task file for OpenClaw
    cat > "logs/task-${agent_id}.json" << EOF
{
  "swarm_id": "uk-farm-$(date +%s)",
  "agent": "$agent_id",
  "name": "$agent_name",
  "task": "$task",
  "model": "$model",
  "spawned_at": "$(date -Iseconds)"
}
EOF

    echo "  ✅ $agent_name ready (task logged)" | tee -a "$LOG_FILE"
}

# ============ DAILY TEAM (6:00 AM) ============
echo "📅 DAILY TEAM (6:00 AM UTC)" | tee -a "$LOG_FILE"

spawn_agent "weather-scout" \
    "🌦 Weather Scout" \
    "Fetch Met Office weather data for UK farming regions. Check for frost warnings, heavy rain, high winds. Output: data/weather-risks.json with alerts by region." \
    "deepseek/deepseek-chat:free"

spawn_agent "grants-hunter" \
    "💰 Grants Hunter" \
    "Scrape gov.uk, DEFRA, RPA for new grant announcements and deadlines. Look for SIF, FIF, infrastructure grants. Output: data/grant-updates.json" \
    "deepseek/deepseek-chat:free"

spawn_agent "markets-watcher" \
    "📈 Market Watcher" \
    "Check AHDB for latest commodity prices (wheat, barley, rapeseed, milk, livestock). Note price trends. Output: data/market-data.json" \
    "deepseek/deepseek-chat:free"

spawn_agent "brief-compiler" \
    "📝 Daily Brief Writer" \
    "Compile weather, grants, and market data into Daily Farm Brief. Format: 3-minute read with emojis, bullet points. Output: content/posts/{date}-daily-brief.md" \
    "deepseek/deepseek-chat:free"

# ============ WEEKLY TEAM (Sunday 8:00 AM) ============
echo "" | tee -a "$LOG_FILE"
echo "📅 WEEKLY TEAM (Sunday 8:00 AM UTC)" | tee -a "$LOG_FILE"

spawn_agent "seo-researcher" \
    "🔍 SEO Researcher" \
    "Research trending UK farming keywords. Look for: seasonal topics (spring drilling, lambing), policy changes, equipment queries. Output: data/seo-keywords.json with top 10 topics" \
    "deepseek/deepseek-chat:free"

spawn_agent "article-writer" \
    "✍️ Long-Form Writer" \
    "Write 1500-word SEO article on top researched topic. Include: practical advice, UK-specific examples, CTA. Output: content/posts/{date}-{slug}.md" \
    "deepseek/deepseek-chat:free"

# ============ MONTHLY TEAM (1st of month) ============
echo "" | tee -a "$LOG_FILE"
echo "📅 MONTHLY TEAM (1st of month 9:00 AM UTC)" | tee -a "$LOG_FILE"

spawn_agent "seasonal-updater" \
    "🗓️ Seasonal Editor" \
    "Update monthly farming checklists based on current season. Include: crop tasks, livestock jobs, machinery prep, grant deadlines. Output: content/seasonal/{month}.md" \
    "deepseek/deepseek-chat:free"

spawn_agent "tool-maintainer" \
    "🛠️ Tool Developer" \
    "Update calculator prices, refresh grant database, check broken links. Output: tools/* updated" \
    "deepseek/deepseek-chat:free"

# ============ DEPLOYER ============
echo "" | tee -a "$LOG_FILE"
echo "🚀 DEPLOYER (On content changes)" | tee -a "$LOG_FILE"

spawn_agent "site-builder" \
    "🔨 Site Builder" \
    "Compile all content, build HTML, push to GitHub Pages. Steps: 1) python3 scripts/build-site.py 2) git commit 3) git push" \
    "deepseek/deepseek-chat:free"

# ============ ACTIVATION ============
echo "" | tee -a "$LOG_FILE"
echo "✅ SWARM CONFIGURATION COMPLETE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Next steps:" | tee -a "$LOG_FILE"
echo "1. Subagents will auto-spawn at scheduled times" | tee -a "$LOG_FILE"
echo "2. Dependencies: Brief Writer waits for Weather/Grants/Market" | tee -a "$LOG_FILE"
echo "3. Site Builder triggers on any content change" | tee -a "$LOG_FILE"
echo "4. Notifications sent to Telegram on completion" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "To add to OpenClaw cron:" | tee -a "$LOG_FILE"
echo '  ~/.openclaw/workspace/skills/uk-farm-blog/scripts/swarm-launcher.sh' | tee -a "$LOG_FILE"

echo ""
echo "🎯 Swarm Ready: 9 agents configured"
echo "💰 Daily cost: $0.00 (freeride mode)"
