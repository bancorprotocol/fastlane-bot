from sys import argv
from decimal import Decimal
from factory.Host import Host
from factory.Main import poolNames
from factory.Main import createPool

if len(argv) > 1:
    Host.connect(argv[1])
else:
    exit('HTTP Provider URL Required')

for poolName in poolNames():
    print(f'{poolName}:')
    pool = createPool(poolName)
    for s, t in [(s, t) for s in pool.coins for t in pool.coins if s != t]:
        s_amount = int(Decimal('123.456') * 10 ** s.decimals)
        t_amount = pool.swap_calc(s.symbol, t.symbol, s_amount)
        r_amount = pool.swap_read(s.symbol, t.symbol, s_amount)
        s_output = f'{Decimal(s_amount) / 10 ** s.decimals} {s.symbol}'
        t_output = f'{Decimal(t_amount) / 10 ** t.decimals} {t.symbol}'
        t_offset = f'{Decimal(t_amount - r_amount) / 10 ** t.decimals}'
        print(f'- {s_output} --> {t_output} (deviation = {t_offset})')
