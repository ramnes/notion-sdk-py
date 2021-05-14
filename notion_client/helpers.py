def pick(base: dict, *keys) -> dict:
    return {key: base[key] for key in keys if key in base}
