def deep_merge(base: dict, override: dict) -> dict:
    """
    Recursively merge two dictionaries.
    override wins over base.
    """
    result = dict(base)

    for key, value in (override or {}).items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value

    return result