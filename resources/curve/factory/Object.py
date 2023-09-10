class Object:
    def __init__(self, data: dict):
        for key, val in data.items():
            setattr(self, key, get(val))

def get(val: any) -> any:
    if type(val) is dict:
       return Object(val)
    if type(val) is list:
       return [get(v) for v in val]
    return val
