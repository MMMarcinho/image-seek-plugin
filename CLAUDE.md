# Image Seek Plugin

Adds image recognition capability to non-multimodal models in Claude Code.

## How it works

- MCP Server exposes `describe_image` tool
- Tool accepts file path, URL, or base64 image sources
- Calls a vision-capable API (OpenAI or Anthropic compatible) to describe the image
- Automatically disabled when using multimodal models (Claude, etc.)

## Setup

```bash
pip3 install -r image_seek/requirements.txt
bash scripts/setup.sh
```

`setup.sh` auto-registers the MCP server in `.claude/settings.json`. MCP server inherits env vars from settings.json `env` - no need to duplicate.

Then configure your vision API in `.claude/settings.json`:

```json
{
  "env": {
    "IMAGE_SEEK_API_KEY": "sk-xxx",
    "IMAGE_SEEK_PROVIDER": "openai",
    "IMAGE_SEEK_MODEL": "gpt-4o",
    "IMAGE_SEEK_ENDPOINT": "https://api.openai.com/v1"
  }
}
```

Or use `config.yaml` in the plugin directory to set provider details directly.

## Supported models (for vision API)

Any OpenAI-compatible or Anthropic-compatible endpoint:
- GPT-4o / GPT-4V
- Claude Sonnet 4 / Opus 4
- Qwen-VL (via OpenAI-compatible endpoint)
