# Open Issues

## Prioritized

1. Granular logging of update process to see where it hangs [DB2] -- CHECK
1. Carbon-only updater [DB6] 
1. Update scripts (ix and win), producing at least heartbeat output [DB3]
1. Event updater for mainnet [DB4]
1. Non-volatile CIDs [DB7]

## Laundry List

### Database

1. Missing decimals issue - DONE
2. Granular logging of update process to see where it hangs
3. Update scripts (ix and win), producing at least heartbeat output
4. Event updater for mainnet
5. Session persistance / session closure
6. Carbon-only updater
7. Non-volatile CIDs
8. Writing database tests

### Provider

1. Expiring filters
2. Brownie hanging issues

### Sundry testing

1. Instantiate unittest database bot and do stats on get_curves

### Methodology

1. Triangles methodology
2. Arbitrage protocol health dashboard

## Stragic roadmap

1. Make the bot running for pairs on mainnet and can be deployed
    1. Ensure database is working smoothly on mainnet (and ideally on tenderly)
    1. Ensure provider is working smoothly on mainnet (and ideally on tenderly)
    1. Verify that addressable arbitrage opportunities are found and closed
    1. Deploy bot on server or on some other connected machine
1. Make sure the bot installs and runs cleanly on a number of architectures
1. Review bot structure (do not start refactoring)
1. Add triangles methodology
1. Effectuate refactoring (possibly before triangles)
1. Review and complete tests