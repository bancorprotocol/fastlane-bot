# DataFetcher

DataFetcher is a Python module that helps fetch, store, and update data about liquidity pools from various exchanges such as Uniswap and Sushiswap.

## Dependencies

- Python 3.9 (ideally)
- pandas
- joblib
- web3
- eth-brownie
- click
- python-dotenv
- logging

To install all dependencies at once, you can use the requirements.txt file included with the package:

```
pip install -r requirements.txt
```

## Usage

The main script is meant to be run from the command line, and accepts several options:

- `n_jobs`: The number of parallel jobs to run. Default is -1, which means using all processors.
- `external_exchanges`: Comma-separated external exchanges. Default is "uniswap_v3".
- `polling_interval`: Polling interval in seconds. Default is 12.

You can run the main script with these options like so:

```
python main.py --n_jobs=4 --external_exchanges="uniswap_v3,sushiswap_v2" --polling_interval=15
```

This will start the script with 4 parallel jobs, fetching data from Uniswap V3 and Sushiswap V2 pools every 15 seconds.

## Adding New Pool Types

To add support for new types of liquidity pools, you need to create a new Pool class and register it with the PoolFactory. Please see the relevant sections of the documentation for more details.

## Environment Variables

This script uses the python-dotenv package to load environment variables from a .env file. You should create this file in the same directory as your script and add the following variables:

- `WEB3_ALCHEMY_PROJECT_ID`: Your Alchemy project ID for connecting to the Ethereum network.

# Extending the Python Package to Support a New Decentralized Exchange

The given Python package is well-structured and modular, making it relatively straightforward to extend it to support additional decentralized exchanges. Here is a step-by-step guide for adding a new exchange, using Balancer as an example:

## Step 1: Prepare the ABI for the new Exchange

- You will first need to obtain the Application Binary Interface (ABI) for the Balancer exchange. The ABI is a JSON description of the smart contract's methods and how to call them. You can usually find this in the project's documentation or GitHub repository.

- Add this ABI into the `abi.py` file in the same format as the existing ABIs. For instance:

    ```python
    BALANCER_POOL_ABI = [
        # ABI content here
    ]
    ```

## Step 2: Create a New Exchange Class

- Create a new dataclass for Balancer that inherits from the `Exchange` abstract base class. In this class, you will implement the methods defined in `Exchange`.

    ```python
    @dataclass
    class Balancer(Exchange):
        exchange_name: str = "balancer"

        def get_abi(self):
            return BALANCER_POOL_ABI

        def get_events(self, contract: Contract) -> List[Type[Contract]]:
            # Implement this method to return a list of event types for the Balancer exchange
            # e.g., return [contract.events.Swap]

        def get_fee(self, address: str, contract: Contract) -> Tuple[str, float]:
            # Implement this method to return the trading fee for the Balancer pool
    ```

   - `get_abi`: This method returns the ABI for the exchange, which you added to the `abi.py` file.
   - `get_events`: This method should return a list of event types that the exchange emits. For Balancer, this might include the 'Swap' event. Note that you need to get these events from the Balancer documentation or source code.
   - `get_fee`: This method should return the trading fee for a given pool on the exchange. You will need to call the appropriate method on the contract to get this information.

## Step 3: Register the New Exchange with the Factory

- Finally, you need to register your new Balancer exchange with the `ExchangeFactory`.

    ```python
    exchange_factory.register_exchange("balancer", Balancer)
    ```
  
## Step 4: Create a New Pool Class

- Create a new dataclass for the Balancer pool that inherits from the `Pool` abstract base class. You will need to implement any methods defined in `Pool`.

```python
@dataclass
class BalancerPool(Pool):
    exchange_name: str = "balancer"

    @staticmethod
    def add_event_args(event_args: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement this method to add relevant event arguments to the data dictionary

    def update_from_contract(self, contract) -> Dict[str, Any]:
        # Implement this method to update the pool's state with data fetched from the smart contract
```

- `add_event_args`: This method should add relevant event arguments to the data dictionary. The exact implementation will depend on the specifics of the Balancer pool and the events it emits.
- `update_from_contract`: This method should update the pool's state with data fetched from the smart contract. You will need to call the appropriate methods on the contract to get this data.

## Step 5: Register the New Pool with the Factory

- After creating the new pool class, you need to register it with the `PoolFactory` so it can be created when needed.

```python
pool_factory.register_format("balancer", BalancerPool)
```

And there you go! You've extended the Python package to support Balancer pools. This process can be repeated for other pool types as needed.

Note: As part of these steps, you may need to extend or modify the ABIs and/or event handling logic to accommodate the specifics of the new pool type. Ensure you have a good understanding of the smart contracts and events related to your new pool type to correctly implement these details.

## Additional Considerations:

In addition to the steps above, there may be other aspects you might need to consider based on the specific requirements of the new pool or exchange. Some potential considerations may include:

- Handling of specific events: If the new pool or exchange emits specific events that are not currently handled in the system, you might need to add handlers for these events.

- Different contract interactions: If the new pool or exchange's contracts require interactions that are different from the current implementation, you might need to extend or modify the interaction methods.

- Additional data in the pool state: If the new pool or exchange requires tracking additional data in the pool state, you might need to add these data fields in your new pool class.

And that's it! You've now extended the Python package to support the Balancer exchange. You can use similar steps to add support for other exchanges such as PancakeSwap.


## Development

...

## License

This project is licensed under the MIT License - see the LICENSE file for details.
