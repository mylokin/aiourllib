def smart_bytes(s, encoding='latin-1', errors='strict'):
    if isinstance(s, str):
        return s.encode(encoding, errors)
    else:
        return s


def smart_text(s, encoding='latin-1', errors='strict'):
    if isinstance(s, str):
        return s
    else:
        return str(s, encoding, errors)
