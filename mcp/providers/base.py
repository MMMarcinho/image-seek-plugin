from abc import ABC, abstractmethod


class BaseProvider(ABC):
    @abstractmethod
    def describe_image(
        self, image_data: bytes, mime_type: str, prompt: str
    ) -> dict:
        """Return {"description": "...", "model": "...", "usage": {...}}."""
        ...
