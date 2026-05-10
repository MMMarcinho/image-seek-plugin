#!/bin/bash
# SessionStart hook: write enabled flag for MCP server
MODEL="${ANTHROPIC_MODEL:-}"
CONFIG="${IMAGE_SEEK_CONFIG:-$HOME/.claude/plugins/data/image-seek/config.yaml}"

if [ -f "$CONFIG" ]; then
    # Delegate to Python for config parsing
    python3 -c "
import os, sys, fnmatch, yaml
model = '$MODEL'
with open('$CONFIG') as f:
    config = yaml.safe_load(f.read())
patterns = config.get('non_multimodal_models', [])
if not patterns or any(fnmatch.fnmatch(model, p) for p in patterns):
    print('enabled')
else:
    print('disabled')
" 2>/dev/null
fi
# Always succeed - MCP server does its own check too
exit 0
