# Image Describer Plugin

Adds image recognition capability to non-multimodal models in Claude Code.

## How it works

- MCP Server exposes `describe_image` tool
- Tool accepts file path, URL, or base64 image sources
- Calls a vision-capable API (OpenAI or Anthropic compatible) to describe the image
- Automatically disabled when using multimodal models (Claude, etc.)

## Setup

1. Install dependencies: `pip3 install -r mcp/requirements.txt`
2. Configure API in `config.yaml` or via environment variables
3. Add to Claude Code settings:

```json
{
  "mcpServers": {
    "image-describer": {
      "command": "python3",
      "args": ["/path/to/image-describer-plugin/mcp/server.py"],
      "env": {
        "IMAGE_DESCRIBER_API_KEY": "${IMAGE_DESCRIBER_API_KEY}",
        "IMAGE_DESCRIBER_CONFIG": "/path/to/config.yaml"
      }
    }
  }
}
```

4. Set env vars in `.claude/settings.json`:

```json
{
  "env": {
    "IMAGE_DESCRIBER_API_KEY": "sk-xxx",
    "IMAGE_DESCRIBER_PROVIDER": "openai",
    "IMAGE_DESCRIBER_MODEL": "gpt-4o",
    "IMAGE_DESCRIBER_ENDPOINT": "https://api.openai.com/v1"
  }
}
```

## Supported models (for vision API)

Any OpenAI-compatible or Anthropic-compatible endpoint. Tested with:
- GPT-4o / GPT-4V
- Claude Sonnet 4 / Opus 4
- Qwen-VL (via OpenAI-compatible endpoint)
