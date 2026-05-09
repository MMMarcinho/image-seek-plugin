"""Image Describer MCP Server.

Provides describe_image tool for non-multimodal models.
Conditionally enabled based on current model's capabilities.
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# The local 'mcp/' package shadows the installed 'mcp' SDK.
# Temporarily remove local paths so FastMCP loads from the installed SDK,
# then clear module cache and restore paths for local imports.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = str(Path(__file__).parent.absolute())
_PROJECT_DIR = str(Path(__file__).parent.parent.absolute())

_saved_path = list(sys.path)
sys.path = [
    p for p in sys.path
    if p != _SCRIPT_DIR and p != _PROJECT_DIR and p != ''
]

from mcp.server.fastmcp import FastMCP  # noqa: E402

# The FastMCP Settings class has a forward-reference to FastMCP itself in the
# 'lifespan' field. Pydantic cannot resolve this until FastMCP is fully defined.
# Rebuild the Settings model now that FastMCP has been imported.
from mcp.server.fastmcp.server import Settings  # noqa: E402
Settings.model_rebuild()

# Clear SDK modules so local 'from mcp.config import ...' resolves correctly
for _key in list(sys.modules):
    if _key == 'mcp' or _key.startswith('mcp.'):
        del sys.modules[_key]

sys.path = _saved_path
sys.path.insert(0, _PROJECT_DIR)
# ---------------------------------------------------------------------------

import base64
try:
    import imghdr
except ImportError:
    imghdr = None  # Removed in Python 3.13+
import os
from urllib.parse import urlparse

import httpx

from mcp.config import load_config, is_enabled
from mcp.providers import create_provider

config = load_config()

server = FastMCP(
    "image-describer",
    instructions="Image recognition service for non-multimodal models. "
    "Call describe_image when you need to understand the content of an image.",
)

SUPPORTED_TYPES = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "gif": "image/gif",
    "webp": "image/webp",
}


def detect_mime_type(data: bytes, hint: str = "") -> str:
    hint_lower = hint.lower()
    for ext, mime in SUPPORTED_TYPES.items():
        if hint_lower.endswith(f".{ext}"):
            return mime
    if imghdr is not None:
        detected = imghdr.what(None, h=data)
        if detected:
            return f"image/{detected}"
    # Fallback: inspect magic bytes
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    if data[:3] == b'\xff\xd8\xff':
        return "image/jpeg"
    if data[:6] in (b'GIF87a', b'GIF89a'):
        return "image/gif"
    if data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return "image/webp"
    return "image/png"


def infer_source_type(source: str) -> str:
    if source.startswith("http://") or source.startswith("https://"):
        return "url"
    if source.startswith("/") or source.startswith("./") or source.startswith("~/"):
        return "file"
    if len(source) > 2 and source[1] == ":" and ("\\" in source or "/" in source):
        return "file"
    return "base64"


def read_image(source: str) -> tuple[bytes, str]:
    st = infer_source_type(source)

    if st == "file":
        path = Path(os.path.expanduser(source)).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {source}")
        if path.stat().st_size > 20 * 1024 * 1024:
            raise ValueError(f"Image too large (>20MB): {source}")
        data = path.read_bytes()
        mime = detect_mime_type(data, path.name)
        return data, mime

    if st == "url":
        resp = httpx.get(source, follow_redirects=True, timeout=15)
        resp.raise_for_status()
        data = resp.content
        if len(data) > 20 * 1024 * 1024:
            raise ValueError(f"Image too large (>20MB) from URL")
        parsed = urlparse(source)
        mime = detect_mime_type(data, Path(parsed.path).name)
        return data, mime

    # base64
    try:
        raw = source
        # Handle data:image/...;base64,... format
        if source.startswith("data:"):
            header, b64 = source.split(",", 1)
            mime = header.split(";")[0].replace("data:", "")
            return base64.b64decode(b64), mime
        data = base64.b64decode(source)
        mime = detect_mime_type(data)
        return data, mime
    except Exception:
        raise ValueError(
            "Invalid base64 input. Provide raw base64 or "
            "data:image/...;base64,... format."
        )


# Only register tool if enabled for current model
if is_enabled(config):
    provider = create_provider(config)

    @server.tool()
    def describe_image(
        source: str,
        prompt: str = "请详细描述这张图片的内容"
    ) -> str:
        """Describe the content of an image. Use this tool when you see an image
        path, URL, or base64 data that you cannot directly process.

        Args:
            source: Image source - file path, HTTP(S) URL, or base64 string.
                    Type is auto-detected. Supports PNG, JPEG, GIF, WebP.
            prompt: Guidance for what to focus on in the description.
                    Language of response follows prompt language.
        """
        try:
            image_data, mime_type = read_image(source)
            if mime_type.split("/")[-1] not in ("png", "jpeg", "gif", "webp"):
                raise ValueError(
                    f"Unsupported image format: {mime_type}. "
                    "Supported: PNG, JPEG, GIF, WebP"
                )
            result = provider.describe_image(image_data, mime_type, prompt)
            return result["description"]
        except FileNotFoundError as e:
            return f"Error: {e}"
        except ValueError as e:
            return f"Error: {e}"
        except httpx.HTTPStatusError as e:
            return f"Error fetching URL (HTTP {e.response.status_code})"
        except httpx.RequestError as e:
            return f"Error fetching URL: {e}"
        except RuntimeError as e:
            return f"API error: {e}"
else:
    @server.tool()
    def describe_image(source: str, prompt: str = "") -> str:
        """This tool is disabled — current model supports multimodal input."""
        return "describe_image is not needed — this model can process images directly."


def main():
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
