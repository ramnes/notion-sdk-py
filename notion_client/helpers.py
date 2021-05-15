from typing import Any, Dict


def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    return {key: base[key] for key in keys if key in base}
