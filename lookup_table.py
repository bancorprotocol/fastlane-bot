from copy import copy
from dataclasses import field, dataclass
from typing import Dict, Any, List, Union
import pandas as pd

# import json
#
# json_path = "/Users/mikewcasale/Documents/GitHub/bancor/fastlane-bot/logs/20231220-110314/latest_pool_data.json"
#
# with open(json_path) as f:
#     json_data = json.load(f)
#
# type(json_data)


@dataclass
class LookupTable:
    """
    A dataclass to query the `json_data` dictionary. The data should be queryable using any of the following lookup keys [`address`, `tkn0_address`, `tkn1_address`, `cid`, `exchange_name`, `last_updated_block`].

    Args:
        json_data (List[Dict[str, Any]]): The list of dictionaries containing the data.
        df (pd.DataFrame): The DataFrame representation of the data.
        cid_dict (Dict[str, List[str]]): A dictionary mapping unique cids to lists of cids.
        address_dict (Dict[str, List[str]]): A dictionary mapping unique addresses to lists of cids.
        tkn0_address_dict (Dict[str, List[str]]): A dictionary mapping unique tkn0 addresses to lists of cids.
        tkn1_address_dict (Dict[str, List[str]]): A dictionary mapping unique tkn1 addresses to lists of cids.
        exchange_name_dict (Dict[str, List[str]]): A dictionary mapping unique exchange names to lists of cids.
        last_updated_block_dict (Dict[str, List[str]]): A dictionary mapping unique last updated blocks to lists of cids.
        keys (List[str]): The list of valid lookup keys.

    Methods:
        __post_init__(): Initializes the LookupTable instance.
        create_dict_from_column(column_name: str) -> Dict[str, List[str]]: Creates a dictionary mapping unique values in a column to lists of cids.
        get_cids(key: str, value: str) -> List[str]: Retrieves a list of cids based on a lookup key and value.
        get_records(key: str, value: str) -> List[Dict[str, Any]]: Retrieves a list of records based on a lookup key and value.
        delete_record(key: str, value: str) -> None: Deletes records based on a lookup key and value.
        add_record(new_record: Dict[str, Any]) -> None: Adds a new record to the LookupTable.
        update_record(updated_record: Dict[str, Any]) -> None: Updates an existing record in the LookupTable.
    """

    json_data: List[Dict[str, Any]] = field(default_factory=list)
    df: pd.DataFrame = field(default_factory=pd.DataFrame)
    cid_dict: Dict[str, List[str]] = field(default_factory=dict)
    address_dict: Dict[str, List[str]] = field(default_factory=dict)
    tkn0_address_dict: Dict[str, List[str]] = field(default_factory=dict)
    tkn1_address_dict: Dict[str, List[str]] = field(default_factory=dict)
    exchange_name_dict: Dict[str, List[str]] = field(default_factory=dict)
    last_updated_block_dict: Dict[str, List[str]] = field(default_factory=dict)
    numerical_index_dict: Dict[str, int] = field(default_factory=dict)
    keys: List[str] = field(default_factory=list)
    _all_keys: List[str] = field(default_factory=list)

    @property
    def all_keys(self):
        return self._all_keys

    @all_keys.setter
    def all_keys(self, value):
        self._all_keys = value

    def __post_init__(self):
        self.keys = [
            "address",
            "tkn0_address",
            "tkn1_address",
            "exchange_name",
            "last_updated_block",
            "numerical_index",
        ]

        self.df = pd.DataFrame(
            self.json_data,
            columns=[
                "cid",
                "last_updated",
                "last_updated_block",
                "descr",
                "pair_name",
                "exchange_name",
                "fee",
                "fee_float",
                "address",
                "tkn0_address",
                "tkn1_address",
                "tkn0_decimals",
                "tkn1_decimals",
                "exchange_id",
                "tkn0_symbol",
                "tkn1_symbol",
                "timestamp",
                "tkn0_balance",
                "tkn1_balance",
            ],
        )
        self.df["cid_index"] = self.df["cid"]
        self.df["last_updated_block_index"] = self.df["last_updated_block"].astype(int)
        self.df["address_index"] = self.df["address"]
        self.df["tkn0_address_index"] = self.df["tkn0_address"]
        self.df["tkn1_address_index"] = self.df["tkn1_address"]
        self.df["exchange_name_index"] = self.df["exchange_name"]

        self.df.set_index("cid_index", inplace=True)
        self.df["info"] = self.json_data

        self.numerical_index_dict = {self.df.index[i]: i for i in range(len(self.df))}
        self.df["numerical_index"] = self.df.index.map(self.numerical_index_dict)

        # Create a dictionary which reorganizes the json_data from a list of dictionaries to a dictionary of
        # dictionaries, where the key is the cid
        unique_cids = self.df["cid"].unique()
        self.cid_dict = {cid: [cid] for cid in unique_cids}

        # Create an `key_dict` which reorganizes the json_data from a list of dictionaries to a dictionary of
        # dictionaries, where the value is a list of `cid` values which can be used to lookup records in the
        # `cid_index` index of the dataframe
        for key in self.keys:
            self.__dict__[f"{key}_dict"] = self.create_dict_from_column(key)

        self.active_cids = set(self.df.index)  # Maintain a set of currently active cids

        all_keys = set()
        for pool in self.json_data:
            all_keys.update(pool.keys())
        self.all_keys = list(all_keys)

    def __getitem__(self, cids: List[str]):
        if not isinstance(cids, list):
            if isinstance(cids, int):
                cids = [self.json_data[cids]["cid"]]
            cids = [cids]
            raise ValueError(
                f"\nWarning: cids must be a list. Converting to list: {cids}\n"
            )

        new_instance = copy(self)
        try:
            new_instance.df = self.df.loc[cids]
            new_instance.active_cids = set(cids)
        except KeyError as e:
            print(f"KeyError: {e}")
        return new_instance

    def __and__(self, other):
        if not isinstance(other, LookupTable):
            raise ValueError(
                "Can only perform '&' operation with another LookupTable instance."
            )

        # Intersection of active cids
        common_cids = self.active_cids & other.active_cids

        # Convert the set to a list
        common_cids_list = list(common_cids)

        # Create a new LookupTable instance
        new_instance = LookupTable(self.json_data)

        # Filter the DataFrame for common cids
        new_instance.df = self.df.loc[common_cids_list]
        new_instance.active_cids = set(common_cids_list)

        return new_instance

    def create_dict_from_column(self, column_name: str) -> Dict[str, List[str]]:
        unique_values = self.df[column_name].unique()
        return {
            value: self.df[self.df[column_name] == value]["cid"].tolist()
            for value in unique_values
        }

    def get_cids(self, key: str, value: str) -> List[str]:
        try:
            return self.__dict__[f"{key}_dict"][value]
        except KeyError:
            return []

    def get_indices(self, cids: List[str]) -> List[int]:
        return self.df.loc[cids]["numerical_index"].tolist()

    def get_records(
        self, key: str, value: str, condition: str = None, in_chain: bool = False
    ) -> "LookupTable" or List[Dict[str, Any]]:

        if value != "":
            cids = self.get_cids(key, value)
        else:
            cids = self.df.index.tolist()

        if condition is None:
            return (
                self.__getitem__(cids)
                if in_chain
                else self.df.loc[cids]["info"].tolist()
            )

        elif condition is not None:
            try:
                # Extract the operator and the value from the condition
                operator, condition_value = condition.split(" ", 1)
                try:
                    condition_value = float(condition_value)
                except ValueError:
                    pass

                if operator == "<":
                    filtered_cids = self.df[
                        (self.df[key] < condition_value) & (self.df["cid"].isin(cids))
                    ].index.tolist()
                elif operator == ">":
                    filtered_cids = self.df[
                        (self.df[key] > condition_value) & (self.df["cid"].isin(cids))
                    ].index.tolist()
                elif operator == "=":
                    filtered_cids = self.df[
                        (self.df[key] == condition_value) & (self.df["cid"].isin(cids))
                    ].index.tolist()
                elif operator == "<=":
                    filtered_cids = self.df[
                        (self.df[key] <= condition_value) & (self.df["cid"].isin(cids))
                    ].index.tolist()
                elif operator == ">=":
                    filtered_cids = self.df[
                        (self.df[key] >= condition_value) & (self.df["cid"].isin(cids))
                    ].index.tolist()
                elif operator == "!=":
                    filtered_cids = self.df[
                        (self.df[key] != condition_value) & (self.df["cid"].isin(cids))
                    ].index.tolist()
                elif operator == "in":
                    condition_value = eval(condition_value)
                    filtered_cids = self.df[
                        (self.df[key].isin(condition_value))
                        & (self.df["cid"].isin(cids))
                    ].index.tolist()
                elif operator == "not in":
                    condition_value = eval(condition_value)
                    filtered_cids = self.df[
                        (~self.df[key].isin(condition_value))
                        & (self.df["cid"].isin(cids))
                    ].index.tolist()
                else:
                    raise ValueError(f"Invalid condition operator: {operator}")
            except ValueError as e:
                raise ValueError(f"Invalid condition value: {condition}") from e
        else:
            filtered_cids = cids

        return (
            self.__getitem__(filtered_cids)
            if in_chain
            else self.df.loc[cids]["info"].tolist()
        )

    def delete_record(self, key: str, value: str) -> None:
        """
        Deletes records based on a lookup key and value.

        Args:
            key (str): The lookup key.
            value (str): The value to lookup.

        Returns:
            None

        """

        cids = self.get_cids(key, value)

        # Directly drop the records from the DataFrame
        self.df.drop(cids, inplace=True)

        # Update json_data
        self.json_data = self.df["info"].tolist()

        # Efficiently update dictionaries
        for cid in cids:
            if cid in self.cid_dict:
                del self.cid_dict[cid]

            # Directly incorporate the logic of update_dict_for_key
            for key in self.keys:
                key_dict = getattr(self, f"{key}_dict")
                keys_to_delete = []
                for key, cid_list in key_dict.items():
                    if cid in cid_list:
                        cid_list.remove(cid)
                        if not cid_list:
                            keys_to_delete.append(key)
                for key in keys_to_delete:
                    del key_dict[key]

    def add_record(self, new_record: Dict[str, Any]) -> None:
        """
        Adds a new record to the LookupTable.

        Args:
            new_record (Dict[str, Any]): The new record to be added. Must be a dictionary.

        Returns:
            None

        Raises:
            ValueError: If the new record is not a dictionary.

        """

        if not isinstance(new_record, dict):
            raise ValueError(f"Invalid record: {new_record}. Must be a dictionary.")

        # Update json_data
        self.json_data.append(new_record)

        # Update DataFrame
        new_df = pd.DataFrame([new_record])
        new_df["cid_index"] = new_df["cid"]
        new_df.set_index("cid_index", inplace=True)
        new_df["info"] = [new_record]
        self.df = pd.concat([self.df, new_df])

        # Update dictionaries
        cid = new_record["cid"]
        self.cid_dict[cid] = [cid]
        for key in self.keys:
            value = new_record[key]
            if value not in self.__dict__[f"{key}_dict"]:
                self.__dict__[f"{key}_dict"][value] = []
            self.__dict__[f"{key}_dict"][value].append(cid)

    def update_record(self, updated_record: Dict[str, Any]) -> None:
        """
        Updates an existing record in the LookupTable.

        Args:
            updated_record (Dict[str, Any]): The updated record. Must be a dictionary.

        Returns:
            None

        Raises:
            ValueError: If the updated record is not a dictionary.

        """

        if not isinstance(updated_record, dict):
            raise ValueError(f"Invalid record: {updated_record}. Must be a dictionary.")

        cid = updated_record["cid"]

        # Update DataFrame directly
        self.df.at[cid, "info"] = updated_record

        # Update json_data
        self.json_data = self.df["info"].tolist()

        # Update dictionaries if necessary
        for key in self.keys:
            old_value = self.df.at[cid, key]
            new_value = updated_record[key]
            if old_value != new_value:
                try:
                    # Remove old entry
                    self.__dict__[f"{key}_dict"][old_value].remove(cid)
                    if not self.__dict__[f"{key}_dict"][old_value]:
                        del self.__dict__[f"{key}_dict"][old_value]
                except KeyError as e:
                    print(f"KeyError: key={key} old_value={old_value} cid={cid}")
                except ValueError as e:
                    print(f"ValueError: key={key} old_value={old_value} cid={cid}")

                # Add new entry
                if new_value not in self.__dict__[f"{key}_dict"]:
                    self.__dict__[f"{key}_dict"][new_value] = []
                self.__dict__[f"{key}_dict"][new_value].append(cid)

    def drop_duplicates(self, subset: List[str] = None) -> None:
        """
        Drops duplicate records from the LookupTable.

        Args:
            subset (List[str]): The list of columns to use to identify duplicates.

        Returns:
            None

        """

        if subset is None:
            subset = ["cid"]

        self.df.sort_values("last_updated_block").drop_duplicates(
            subset=subset, keep="last", inplace=True
        )
        self.json_data = self.df["info"].tolist()

        # Update dictionaries
        for key in self.keys:
            self.__dict__[f"{key}_dict"] = self.create_dict_from_column(key)


# lt = LookupTable(json_data)
#
# key1 = "exchange_name"
# value1 = "uniswap_v2"
# key2 = "tkn0_address"
# value2 = "0x1BBf25e71EC48B84d773809B4bA55B6F4bE946Fb"
# sample_lookup = lt[
#     lt.get_records(key=key1, value=value1, in_chain=True)
#     & lt.get_records(key=key2, value=value2, in_chain=True)
# ]
#
# sample_lookup
