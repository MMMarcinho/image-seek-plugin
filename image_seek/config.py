import os
import re
from pathlib import Path
import yaml


def resolve_env(value: str) -> str:
    """Resolve ${ENV_VAR} references in a string."""
    return re.sub(
        r'\$\{(\w+)\}',
        lambda m: os.environ.get(m.group(1), ''),
        value
    )


def load_config() -> dict:
    config_path = os.environ.get(
        'IMAGE_SEEK_CONFIG',
        Path(__file__).parent.parent / 'config.yaml'
    )
    with open(config_path) as f:
        raw = f.read()
    resolved = resolve_env(raw)
    return yaml.safe_load(resolved)


def is_enabled(config: dict) -> bool:
    """Check if image seek should be enabled for current model."""
    model = os.environ.get('ANTHROPIC_MODEL', '')
    if not model:
        return True

    patterns = config.get('non_multimodal_models', [])
    if not patterns:
        return True

    import fnmatch
    return any(fnmatch.fnmatch(model, p) for p in patterns)
