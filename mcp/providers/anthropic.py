import base64
import httpx
from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(self, endpoint: str, api_key: str, model: str):
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.model = model

    def describe_image(
        self, image_data: bytes, mime_type: str, prompt: str
    ) -> dict:
        b64 = base64.b64encode(image_data).decode()

        resp = httpx.post(
            f"{self.endpoint}/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image", "source": {
                            "type": "base64",
                            "media_type": mime_type,
                            "data": b64
                        }}
                    ]
                }]
            },
            timeout=60
        )

        if resp.status_code >= 400:
            raise RuntimeError(
                f"Anthropic API error {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        return {
            "description": data["content"][0]["text"],
            "model": self.model,
            "usage": data.get("usage", {})
        }
