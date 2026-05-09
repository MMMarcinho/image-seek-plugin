from .base import BaseProvider


def create_provider(config: dict) -> BaseProvider:
    provider_config = config.get('provider', {})
    provider_type = provider_config.get('type', 'openai')

    if provider_type == 'openai':
        from .openai import OpenAIProvider
        return OpenAIProvider(
            endpoint=provider_config['endpoint'],
            api_key=provider_config['api_key'],
            model=provider_config['model']
        )
    elif provider_type == 'anthropic':
        from .anthropic import AnthropicProvider
        return AnthropicProvider(
            endpoint=provider_config['endpoint'],
            api_key=provider_config['api_key'],
            model=provider_config['model']
        )
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")
