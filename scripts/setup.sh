#!/bin/bash
# Image Seek Plugin - Setup Script
# Registers MCP server in ~/.claude.json and authorizes in settings.json

set -e

PLUGIN_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_JSON="$HOME/.claude.json"
SETTINGS_FILE="$HOME/.claude/settings.json"

echo "Image Seek Plugin Setup"
echo "======================="
echo ""

SERVER_PATH="$PLUGIN_DIR/image_seek/server.py"

# 1. Register MCP server in ~/.claude.json
if [ -f "$CLAUDE_JSON" ]; then
    python3 -c "
import json
with open('$CLAUDE_JSON') as f:
    c = json.load(f)
if 'mcpServers' not in c:
    c['mcpServers'] = {}
c['mcpServers']['image-seek'] = {
    'command': 'python3',
    'args': ['$SERVER_PATH']
}
with open('$CLAUDE_JSON', 'w') as f:
    json.dump(c, f, indent=2)
    f.write('\n')
"
else
    python3 -c "
import json
c = {
    'mcpServers': {
        'image-seek': {
            'command': 'python3',
            'args': ['$SERVER_PATH']
        }
    }
}
with open('$CLAUDE_JSON', 'w') as f:
    json.dump(c, f, indent=2)
    f.write('\n')
"
fi
echo "MCP server registered in $CLAUDE_JSON"

# 2. Authorize in settings.json
if [ -f "$SETTINGS_FILE" ]; then
    python3 -c "
import json
with open('$SETTINGS_FILE') as f:
    s = json.load(f)
if 'enabledMcpjsonServers' not in s:
    s['enabledMcpjsonServers'] = []
if 'image-seek' not in s['enabledMcpjsonServers']:
    s['enabledMcpjsonServers'].append('image-seek')
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(s, f, indent=2)
    f.write('\n')
"
    echo "MCP server authorized in $SETTINGS_FILE"
fi

echo ""
echo "Setup complete. Configure your vision API in settings.json env:"
echo "  IMAGE_SEEK_API_KEY: your-api-key"
echo "  IMAGE_SEEK_PROVIDER: openai  (or anthropic)"
echo "  IMAGE_SEEK_MODEL: gpt-4o"
echo "  IMAGE_SEEK_ENDPOINT: https://api.openai.com/v1"
