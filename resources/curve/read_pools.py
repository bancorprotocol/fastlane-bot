from sys import argv
from json import dumps
from factory.Host import Host
from factory.Main import poolNames
from factory.Main import createPool

if len(argv) > 1:
    Host.connect(argv[1])
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

print(dumps({poolName: parse(createPool(poolName)) for poolName in poolNames()}, indent=4))