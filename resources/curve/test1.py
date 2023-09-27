from decimal import Decimal
from factory import forge_pool
from example import pool_params

for pool_name in pool_params:
    print(f'{pool_name}:')
    pool = forge_pool(pool_name, config_data=pool_params[pool_name])
    for s, t in [(s, t) for s in pool.coins for t in pool.coins if s != t]:
        s_amount = int(Decimal('123.456') * 10 ** s.decimals)
        t_amount = pool.swap_calc(s.symbol, t.symbol, s_amount)
        s_output = f'{Decimal(s_amount) / 10 ** s.decimals} {s.symbol}'
        t_output = f'{Decimal(t_amount) / 10 ** t.decimals} {t.symbol}'
        print(f'- {s_output} --> {t_output}')
