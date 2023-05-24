# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.13.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

import re
import json
from dataclasses import dataclass
from datetime import datetime

# # Log Decoder [Analysis016]

data = """
2023-05-24 15:40:06,165 [fastlane:INFO] - [2023-05-24T15:40:06::1684932006] |calculated_arb| == {'FLT': 'ETH-EEeE', 'flash_amount': '0.4555', 'profit_native': '0.0013', 'profit_bnt': '4.8882', 'trades': [{'trade': 0, 'tkn_in': 'WETH-6Cc2', 'amount_in': '0.4555', 'tkn_out': 'USDC-eB48', 'amt_out': '829.9234', 'cid': '8841057382'}, {'trade': 1, 'tkn_in': 'USDC-eB48', 'amount_in': '829.9234', 'tkn_out': 'WETH-6Cc2', 'amt_out': '0.4567', 'cid': 'b61bc3f2c4'}]}

2023-05-24 15:40:06,165 [fastlane:INFO] - [2023-05-24T15:40:06::1684932006] |meh| == {'FLT': 'ETH-EEeE', 'flash_amount': '0.4555', 'profit_native': '0.0013', 'profit_bnt': '4.8882', 'trades': [{'trade': 0, 'tkn_in': 'WETH-6Cc2', 'amount_in': '0.4555', 'tkn_out': 'USDC-eB48', 'amt_out': '829.9234', 'cid': '8841057382'}, {'trade': 1, 'tkn_in': 'USDC-eB48', 'amount_in': '829.9234', 'tkn_out': 'WETH-6Cc2', 'amt_out': '0.4567', 'cid': 'b61bc3f2c4'}]}

2023-05-24 15:40:09,656 [fastlane:INFO] - [2023-05-24T15:40:09::1684932009] |arb_with_gas| == {'FLT': 'ETH-EEeE', 'flash_amount': '0.4555', 'profit_native': '0.0013', 'profit_bnt': '4.8882', 'trades': [{'trade': 0, 'tkn_in': 'WETH-6Cc2', 'amount_in': '0.4555', 'tkn_out': 'USDC-eB48', 'amt_out': '829.9234', 'cid': '8841057382'}, {'trade': 1, 'tkn_in': 'USDC-eB48', 'amount_in': '829.9234', 'tkn_out': 'WETH-6Cc2', 'amt_out': '0.4567', 'cid': 'b61bc3f2c4'}], 'block_number': 17329101, 'gas': 587111, 'base_fee': 40189088639, 'priority_fee': 109000000, 'max_gas_fee': 40298088639, 'gas_cost_bnt': '84.6551', 'gas_cost_eth': '0.0189', 'gas_cost_millieth': '18927.5609', 'gas_cost_usd': '$34.3880', 'uni_v3_trade_cost_eth': '0.0063', 'uni_v3_trade_cost_usd': '$11.5014'}


2023-05-24 16:39:31,176 [fastlane:INFO] - [2023-05-24T16:39:31::1684935571] |arb_with_gas| == {'flashloan': [{'token': 'ETH-EEeE', 'amount': 0.4555, 'profit': 0.0018}], 'profit_bnt': 6.798, 'trades': [{'trade_index': 0, 'tkn_in': 'WETH-6Cc2', 'amount_in': 0.4555, 'tkn_out': 'USDC-eB48', 'amt_out': 829.9234, 'cid0': '8841057382'}, {'trade_index': 1, 'tkn_in': 'USDC-eB48', 'amount_in': 829.9234, 'tkn_out': 'WETH-6Cc2', 'amt_out': 0.4572, 'cid0': 'b61bc3f2c4'}], 'block_number': 17329396, 'gas': 586996, 'base_fee_wei': 64373808618, 'priority_fee_wei': 109000000, 'max_gas_fee_wei': 64482808618, 'gas_cost_bnt': 135.4339, 'gas_cost_eth': 0.0303, 'gas_cost_usd': 55.0093, 'uni_v3_trade_cost_eth': 0.0101, 'uni_v3_trade_cost_usd': 18.3904}
"""


@dataclass
class LogLine():
    time_s: str
    time_ts: int
    tag: str
    data: any
        
    REGEX = r".*? - \[(.*?)::(.*?)].*?\|(.*?)\|.*?==.*?({.*})"
      
    @classmethod
    def new(cls, line):
        """
        reads a single line and instantiates a new object
        """
        m = re.match(cls.REGEX, line)
        return cls(
            time_s = m.group(1)+"Z",
            time_ts = int(m.group(2)),
            tag = m.group(3),
            data = json.loads(m.group(4).replace("'", '"'))
        )
    
    @classmethod
    def parse(cls, logfiletext):
        """
        parses the entire text of the logfile
        """
        lines = (l for l in data.splitlines() if l.strip())
        ll = list(LogLine.new(l) for l in lines)
        return ll
        
    
    @property
    def time(self):
        """datetime object corresponding to time"""
        return datetime.fromtimestamp(self.time_ts)

ll = LogLine.parse(data)

[l.tag for l in ll]

ll[0].data

ll[-1].data




