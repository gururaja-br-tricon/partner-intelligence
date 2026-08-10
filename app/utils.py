import json


def parse_concatenated(s: str) -> list[dict]:                                                                                                                     
    decoder = json.JSONDecoder()
    out, i = [], 0
    try:
        while (s := s[i:].strip()):
            obj, i = decoder.raw_decode(s)
            out.append(obj)
    except Exception:
        return []
    else:
        return out
