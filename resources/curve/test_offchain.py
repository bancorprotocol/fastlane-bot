from decimal import Decimal
from mock_pools import mock_pools
from factory.Main import createMockPool

for poolName, poolData in mock_pools.items():
    print(f'{poolName}:')
    pool = createMockPool(poolName, poolData)
    for s, t in [(s, t) for s in pool.coins for t in pool.coins if s != t]:
        s_amount = int(Decimal('123.456') * 10 ** s.decimals)
        t_amount = pool.swap_calc(s.symbol, t.symbol, s_amount)
        s_output = f'{Decimal(s_amount) / 10 ** s.decimals} {s.symbol}'
        t_output = f'{Decimal(t_amount) / 10 ** t.decimals} {t.symbol}'
        print(f'- {s_output} --> {t_output}')
