import json


def parse_concatenated(s: str) -> list[dict]:
    decoder = json.JSONDecoder()
    out, i = [], 0
    try:
        while (s := s[i:].strip()):
            obj, i = decoder.raw_decode(s)
            if isinstance(obj, list):
                out.extend(obj)
            else:
                out.append(obj)
    except Exception:
        return []
    return out
