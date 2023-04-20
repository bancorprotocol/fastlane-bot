This README file provides information about the `carbon/data` directory and its importance during the initial setup of the SQL database.

`carbon/data` Directory
-----------------------

The `carbon/data` directory contains essential data files used during the initial setup of the SQL database. One of the key files in this directory is the `seed_token_pairs.csv` file.

### `seed_token_pairs.csv` File

The `seed_token_pairs.csv` file is a CSV file containing seed data about token pairs on various DeFi exchanges. This data is crucial for populating the SQL database with initial information about the token pairs available for trading on these exchanges. The file's structure consists of multiple rows, with each row representing a token pair and its associated data, such as the token symbols, contract addresses, and the name of the DeFi exchange.

During the initial setup of the SQL database, the `seed_token_pairs.csv` file is read, and its contents are used to populate the relevant tables in the database. This seed data serves as a starting point for the application and allows it to function properly with accurate information about the available token pairs on different DeFi exchanges.

Conclusion
----------

The `carbon/data` directory and the `seed_token_pairs.csv` file play an essential role in setting up the SQL database with accurate information about token pairs on various DeFi exchanges. Make sure that the `seed_token_pairs.csv` file is up-to-date and contains accurate data to ensure the correct functioning of the application.