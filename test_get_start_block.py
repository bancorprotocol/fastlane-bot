from fastlane_bot.events.utils import get_start_block as new_get_start_block

def old_get_start_block(
    alchemy_max_block_fetch: int,
    last_block: int,
    mgr: any,
    reorg_delay: int,
    replay_from_block: int,
) -> (int, int or None):
    if replay_from_block:
        return (
            replay_from_block - 1
            if last_block != 0
            else replay_from_block - reorg_delay - alchemy_max_block_fetch
        ), replay_from_block
    elif mgr.tenderly_fork_id:
        from_block = mgr.w3_tenderly.eth.block_number
        return (
            max(block["last_updated_block"] for block in mgr.pool_data) - reorg_delay
            if last_block != 0
            else from_block - reorg_delay - alchemy_max_block_fetch
        ), from_block
    else:
        current_block = mgr.web3.eth.block_number
        return (
            (
                max(block["last_updated_block"] for block in mgr.pool_data)
                - reorg_delay
                if last_block != 0
                else current_block - reorg_delay - alchemy_max_block_fetch
            ),
            None
        )

class ETH:
    def __init__(self, block_number: int):
        self.block_number = block_number

class Web3:
    def __init__(self, block_number: int):
        self.eth = ETH(block_number)

class MGR:
    def __init__(self, tenderly_fork_id: bool, w3_tenderly_block_number: int, web3_block_number: int, pool_block_numbers: list[int or float]):
        self.tenderly_fork_id = tenderly_fork_id
        self.w3_tenderly = Web3(w3_tenderly_block_number)
        self.web3 = Web3(web3_block_number)
        self.pool_data = [{"last_updated_block": pool_block_number} for pool_block_number in pool_block_numbers]

for alchemy_max_block_fetch in range(10):
    for last_block in [0, 1]:
        for reorg_delay in range(10):
            for replay_from_block in range(10):
                for tenderly_fork_id in [False, True]:
                    for w3_tenderly_block_number in range(10):
                        for web3_block_number in range(10):
                            for pool_block_numbers in [[1, 2], [1, 2.0], [1.0, 2], [1.0, 2.0]]:
                                print(
                                    f"alchemy_max_block_fetch  = {alchemy_max_block_fetch }\n" +
                                    f"last_block               = {last_block              }\n" +
                                    f"reorg_delay              = {reorg_delay             }\n" +
                                    f"replay_from_block        = {replay_from_block       }\n" +
                                    f"tenderly_fork_id         = {tenderly_fork_id        }\n" +
                                    f"web3_block_number        = {web3_block_number       }\n" +
                                    f"pool_block_numbers       = {pool_block_numbers      }\n"
                                )
                                mgr = MGR(tenderly_fork_id, w3_tenderly_block_number, web3_block_number, pool_block_numbers)
                                expected = old_get_start_block(alchemy_max_block_fetch, last_block, mgr, reorg_delay, replay_from_block)
                                actual   = new_get_start_block(alchemy_max_block_fetch, last_block, mgr, reorg_delay, replay_from_block)
                                for e, a in zip(expected, actual):
                                    if type(e) is float:
                                        assert type(a) is int and a == e, f"expected value {e} of type int, got value {a} of type {type(a)}"
                                    else:
                                        assert type(a) is type(e) and a == e, f"expected value {e} of type {type(e)}, got value {a} of type {type(a)}"
