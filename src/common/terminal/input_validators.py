always_true = lambda _: True

non_negative_integer_or_empty = (
    lambda text: (text.isnumeric() and int(text) >= 0) or text == ""
)


def non_negative_integer_and_and_configured_negative_values_or_empty(
    allowed_negative_values: list[int],
):
    return lambda text: (
        (text.isnumeric() and int(text) >= 0)
        or text == ""
        or any(text == str(value) for value in allowed_negative_values)
    )
