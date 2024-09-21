from decimal import Decimal


def convert_decimal_to_string(data):
    """
    Recursively convert all Decimal objects to string in a dictionary or list.
    """
    if isinstance(data, dict):
        return {k: convert_decimal_to_string(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_string(v) for v in data]
    elif isinstance(data, Decimal):
        return f"{data:.2f}"
    else:
        return data
