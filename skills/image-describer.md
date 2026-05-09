---
name: image-describer
description: Manually describe an image using a vision-capable API. Use when you need image recognition and the main model cannot process images directly.
---

# Image Describer

Invoke the `describe_image` MCP tool to analyze an image.

## Usage

When the user provides an image (file path, URL, or base64), call the `describe_image` tool:

- **File**: `describe_image(source="/path/to/image.png")`
- **URL**: `describe_image(source="https://example.com/image.jpg")`
- **Base64**: `describe_image(source="<base64 data>")`

Add a `prompt` parameter to guide the description:

```
describe_image(source="/path/to/screenshot.png", prompt="识别图中的错误信息")
```

Response language follows the prompt language automatically.
