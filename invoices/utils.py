from decimal import Decimal, ROUND_HALF_UP


def convert_decimal_to_string(data):
    """
    Recursively convert all Decimal objects to string in a dictionary or list.
    2 decimal places are retained for the converted string by rounding.
    """
    if isinstance(data, dict):
        return {k: convert_decimal_to_string(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_string(v) for v in data]
    elif isinstance(data, Decimal):
        rounded_data = data.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{rounded_data:.2f}"
    else:
        return data
