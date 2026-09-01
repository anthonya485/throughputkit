"""Locale-aware decimal number parsing shared by the size and duration parsers."""


def parse_localized_number(text):
    """Parse a decimal number written with either '.' or ',' as the decimal
    point, e.g. "1234.56" (US), "1234,56" (EU), "1,234.56" (US with grouping),
    or "1.234,56" (EU with grouping). Grouping digits must come in threes.
    """
    has_comma = "," in text
    has_dot = "." in text

    if has_comma and has_dot:
        if text.rindex(",") > text.rindex("."):
            decimal_sep, group_sep = ",", "."
        else:
            decimal_sep, group_sep = ".", ","
    elif has_comma:
        decimal_sep, group_sep = (",", None) if text.count(",") == 1 else (None, ",")
    elif has_dot:
        decimal_sep, group_sep = (".", None) if text.count(".") == 1 else (None, ".")
    else:
        return float(text)

    if group_sep is not None:
        _check_grouping(text, group_sep, decimal_sep)
        text = text.replace(group_sep, "")
    if decimal_sep is not None and decimal_sep != ".":
        text = text.replace(decimal_sep, ".")

    return float(text)


def _check_grouping(text, group_sep, decimal_sep):
    integer_part = text.rsplit(decimal_sep, 1)[0] if decimal_sep else text
    groups = integer_part.split(group_sep)
    if not groups[0].isdigit() or len(groups[0]) > 3:
        raise ValueError(f"not a number: {text!r}")
    if any(len(group) != 3 or not group.isdigit() for group in groups[1:]):
        raise ValueError(f"not a number: {text!r}")
