from sys import argv
from json import dumps
from factory import connect
from factory import forge_pool
from factory import pool_names

if len(argv) > 1:
    connect(argv[1])
else:
    exit('HTTP Provider URL Required')

def parse(obj: any) -> any:
    if type(obj) in [int, str, bool]:
        return obj
    if type(obj) is list:
        return [parse(val) for val in obj]
    if type(obj) is dict:
        return {key: parse(val) for key, val in obj.items() if key != 'contract'}
    return parse(vars(obj))

print(dumps({pool_name: parse(forge_pool(pool_name, connect=True, sync=True)) for pool_name in pool_names}, indent=4))