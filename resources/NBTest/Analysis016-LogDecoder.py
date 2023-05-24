# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

import re
import json
from dataclasses import dataclass
from datetime import datetime
import os

# # Log Decoder [Analysis016]

data = """
/root/flbtest
Using default database url, if you want to use a different database, set the backend_url found at the bottom of manager_base.py
Starting bot...
2023-05-24 19:48:44,936 [fastlane:INFO] - [2023-05-24T19:48:44::1684957724] |calculated_arb| == {'type': 'single', 'profit_bnt': 29.4095, 'profit_usd': 11.8129, 'flashloan': [{'token': 'ETH-EEeE', 'amount': 0.4555, 'profit': 0.0066}], 'trades': [{'trade_index': 0, 'exchange': 'carbon_v1', 'tkn_in': 'WETH-6Cc2', 'amount_in': 0.4555, 'tkn_out': 'USDC-eB48', 'amt_out': 829.9234, 'cid0': '8841057382'}, {'trade_index': 1, 'exchange': 'uniswap_v3', 'tkn_in': 'USDC-eB48', 'amount_in': 829.9234, 'tkn_out': 'WETH-6Cc2', 'amt_out': 0.462, 'cid0': 'b61bc3f2c4'}]}
2023-05-24 19:48:44,937 [fastlane:INFO] - Opportunity with profit: 29.4095 does not meet minimum profit: 1000, discarding.
"""


# +
# FNAME = "arbbot.log"
# FNAME = "mylog.log"
# FPATH = "../.."
# FFNAME = os.path.join(FPATH, FNAME)

# +
# with open(FFNAME, "r") as f:
#     data = f.read()
# data.splitlines()[-10:]
# -

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
        if m is None:
            return None
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
        ll = (LogLine.new(l) for l in lines)
        ll = (l for l in ll if not l is None)
        return list(ll)
        
    
    @property
    def time(self):
        """datetime object corresponding to time"""
        return datetime.fromtimestamp(self.time_ts)

ll = LogLine.parse(data)

[l.tag for l in ll]

ll[0].data

ll[-1].data




