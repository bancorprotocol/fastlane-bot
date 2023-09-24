from sys import argv
from decimal import Decimal
from factory import connect
from factory import forge_pool
from example import pool_params

if len(argv) > 1:
    connect(argv[1])
else:
    exit('HTTP Provider URL Required')

for pool_name in pool_params:
    print(f'{pool_name}:')
    data = {"coins": [{key: coin[key] for key in ["symbol", "decimals"]} for coin in pool_params[pool_name]["coins"]]}
    pool = forge_pool(pool_name, connect=True, data=data)
    for s, t in [(s, t) for s in pool.coins for t in pool.coins if s != t]:
        s_amount = int(Decimal('123.456') * 10 ** s.decimals)
        t_amount = pool.swap_read(s.symbol, t.symbol, s_amount)
        s_output = f'{Decimal(s_amount) / 10 ** s.decimals} {s.symbol}'
        t_output = f'{Decimal(t_amount) / 10 ** t.decimals} {t.symbol}'
        print(f'- {s_output} --> {t_output}')
