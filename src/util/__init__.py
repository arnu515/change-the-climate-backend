import random
import string


def generate_string(length=16, has_digits=True) -> str:
    charset = string.ascii_letters
    if has_digits:
        charset += string.digits

    return "".join([random.choice(charset) for _ in range(length)])
