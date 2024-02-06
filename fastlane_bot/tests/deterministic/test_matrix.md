# Test Matrix Use
## Column Descriptions
1. Priority
    - HIGH - Carbon-centric and POL-centric tests representing the minimal requirement for a successful bot. Simplest of tests with lots of breadth.
    - MEDIUM - Nice to have but not essential for support of Carbon and POL. Could be Bancor v2.1 / v3 centric or higher complexity.
    - LOW - Support for ancillary capabilities that offer bot enhancement but not Bancor product family centric. Includes modes that dont depend on Carbon or Bancor, e.g. multi_pairwise_all.
1. Complexity
    - LOW - Simple tests running through minimum number of exchanges and only one Carbon order.
    - MEDIUM - Multiple exchanges or Carbon orders.
    - HIGH - Multiple considerations, exchanges, Carbon orders, wrapping. Should be have a dedicated testnet to avoid conflicts.
1. Test Batch - Name of file that contains that test, or MANUAL.
1. Test Number - Unique enumerated tests across all test batches.
1. Blockchain - The blockchain test to be run on.
1. Arb_Mode - The arb_mode the bot should run in.
1. Platform Count - Exchanges/Wrapping count.
1. Carbon Count - Number of Carbon orders created/routed through.
1. Exchanges - List exchanges included. E.g. [carbon_v1, uniswap_v2]
1. Tokens - List tokens included. E.g. [WETH, LINK].
1. Decimals - List decimals included. E.g. [8, 6, 18].
1. Fees - List fees included. Particularly relevant for Uniswap/Pancake v3 and Balancer, Carbon custom fees.
1. Wrapping - Wrapping included in the route - mark X.
1. Exchanges Explicit - All exchanges listed one per column and marked X if included.