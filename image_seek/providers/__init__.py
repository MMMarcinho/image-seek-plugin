import os

from .base import BaseProvider


def _get(key: str, config: dict, default: str = "") -> str:
    """Config value from env var first, then config file, then default."""
    env_key = f"IMAGE_SEEK_{key.upper()}"
    return os.environ.get(env_key) or config.get(key, default)


def create_provider(config: dict) -> BaseProvider:
    provider_config = config.get('provider', {})
    provider_type = _get('provider', provider_config, 'openai')

    endpoint = _get('endpoint', provider_config, 'https://api.openai.com/v1')
    api_key = _get('api_key', provider_config)
    model = _get('model', provider_config, 'gpt-4o')

    if provider_type == 'openai':
        from .openai import OpenAIProvider
        return OpenAIProvider(endpoint=endpoint, api_key=api_key, model=model)
    elif provider_type == 'anthropic':
        from .anthropic import AnthropicProvider
        return AnthropicProvider(endpoint=endpoint, api_key=api_key, model=model)
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
