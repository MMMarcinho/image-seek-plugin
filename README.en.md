# image-seek-plugin

Adds image recognition capability to non-multimodal models in Claude Code.

## How It Works

- Starts an MCP server that exposes the `describe_image` tool
- Automatically enables when Claude Code uses a non-multimodal model (e.g., DeepSeek, Qwen, GLM)
- The tool accepts file paths, URLs, or base64-encoded images and calls a vision API for text descriptions
- Automatically disables when using multimodal models (Claude, etc.) to avoid unnecessary calls

```
User sends image → Claude Code detects image → calls describe_image tool
                                                    ↓
                                        image-seek MCP Server
                                                    ↓
                                        OpenAI / Anthropic Vision API
                                                    ↓
                                Returns text description → Claude Code continues
```

## Installation

```bash
pip3 install -r image_seek/requirements.txt
bash scripts/setup.sh
```

`setup.sh` automatically registers the MCP server in `.claude.json` and authorizes it in `.claude/settings.json`.

## Configuration

Two configuration methods — choose one.

### Method 1: Environment Variables (Recommended)

Set in `.claude/settings.json` under `env`:

```json
{
  "env": {
    "IMAGE_SEEK_API_KEY": "sk-your-api-key",
    "IMAGE_SEEK_PROVIDER": "openai",
    "IMAGE_SEEK_MODEL": "gpt-4o",
    "IMAGE_SEEK_ENDPOINT": "https://api.openai.com/v1"
  }
}
```

For Anthropic-compatible APIs:

```json
{
  "env": {
    "IMAGE_SEEK_API_KEY": "sk-ant-your-api-key",
    "IMAGE_SEEK_PROVIDER": "anthropic",
    "IMAGE_SEEK_MODEL": "claude-sonnet-4-6",
    "IMAGE_SEEK_ENDPOINT": "https://api.anthropic.com"
  }
}
```

### Method 2: config.yaml

Edit `config.yaml` in the plugin directory:

```yaml
provider:
  type: openai
  endpoint: https://api.openai.com/v1
  api_key: ${IMAGE_SEEK_API_KEY}
  model: gpt-4o
```

Environment variables take precedence over config.yaml values.

## Supported Vision APIs

| Provider | Example Models | Notes |
|---|---|---|
| OpenAI-compatible | GPT-4o, GPT-4V, Qwen-VL | Any endpoint compatible with OpenAI Chat Completions |
| Anthropic-compatible | Claude Sonnet 4, Opus 4 | Any endpoint compatible with Anthropic Messages |

## Supported Image Formats

- PNG
- JPEG / JPG
- GIF
- WebP

Maximum file size: 20MB.

## Usage

### Automatic Trigger

The plugin automatically decides whether to enable based on the current model. When a non-multimodal model (e.g., DeepSeek) encounters an image, Claude Code automatically invokes `describe_image`.

Configure non-multimodal model matching patterns in `config.yaml`:

```yaml
non_multimodal_models:
  - "deepseek-*"
  - "doubao-*"
  - "qwen-*"
  - "glm-*"
```

### Manual Invocation

You can also trigger the skill manually:

```
/image-seek
```

Or call the tool directly:

- **Local file**: `describe_image(source="/path/to/image.png")`
- **URL**: `describe_image(source="https://example.com/photo.jpg")`
- **Base64**: `describe_image(source="<base64 data>")`

Add a `prompt` parameter to guide the description:

```
describe_image(source="/path/to/screenshot.png", prompt="Identify any error messages in this screenshot")
```

## Project Structure

```
image-seek-plugin/
├── image_seek/           # Python package (MCP Server)
│   ├── server.py         # MCP server entry point
│   ├── config.py         # Config loading & model matching
│   └── providers/        # Vision API adapters
│       ├── base.py       # Base provider interface
│       ├── openai.py     # OpenAI-compatible provider
│       └── anthropic.py  # Anthropic-compatible provider
├── hooks/                # Claude Code lifecycle hooks
│   └── session-start.sh  # Session-start enable check
├── skills/               # Claude Code skill files
│   └── image-seek.md     # /image-seek manual trigger
├── scripts/
│   └── setup.sh          # One-click setup script
└── config.yaml           # Plugin configuration file
```

## FAQ

**Q: Why isn't the plugin working?**
A: Check if the current model is in the `non_multimodal_models` list. If the model natively supports multimodal, the plugin automatically disables itself.

**Q: API returns an error?**
A: Verify your API key is correct and the endpoint is reachable. HTTP proxy is supported — set `HTTP_PROXY` / `HTTPS_PROXY` environment variables.

**Q: How do I switch vision APIs?**
A: Change `IMAGE_SEEK_PROVIDER` to `openai` or `anthropic`, and update `IMAGE_SEEK_ENDPOINT` and `IMAGE_SEEK_MODEL` accordingly.
