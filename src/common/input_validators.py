always_true = lambda _: True

non_negative_integer_or_empty = (
    lambda text: (text.isnumeric() and int(text) >= 0) or text == ""
)
