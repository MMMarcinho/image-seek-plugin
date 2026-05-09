import base64
import httpx
from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, endpoint: str, api_key: str, model: str):
        self.endpoint = endpoint.rstrip('/')
        self.api_key = api_key
        self.model = model

    def describe_image(
        self, image_data: bytes, mime_type: str, prompt: str
    ) -> dict:
        b64 = base64.b64encode(image_data).decode()
        data_url = f"data:{mime_type};base64,{b64}"

        resp = httpx.post(
            f"{self.endpoint}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": self.model,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }],
                "max_tokens": 1024
            },
            timeout=60
        )

        if resp.status_code >= 400:
            raise RuntimeError(
                f"OpenAI API error {resp.status_code}: {resp.text}"
            )

        data = resp.json()
        return {
            "description": data["choices"][0]["message"]["content"],
            "model": self.model,
            "usage": data.get("usage", {})
        }
