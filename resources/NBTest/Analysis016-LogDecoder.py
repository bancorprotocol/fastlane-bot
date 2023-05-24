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
import os

# # Log Decoder [Analysis016]

# ## Read the logfile

# ### Static data for testing

testdata = """
/root/flbtest
Using default database url, if you want to use a different database, set the backend_url found at the bottom of manager_base.py
Starting bot...
2023-05-24 19:48:44,936 [fastlane:INFO] - [2023-05-24T19:48:44::1684957724] |calculated_arb| == {'type': 'single', 'profit_bnt': 29.4095, 'profit_usd': 11.8129, 'flashloan': [{'token': 'ETH-EEeE', 'amount': 0.4555, 'profit': 0.0066}], 'trades': [{'trade_index': 0, 'exchange': 'carbon_v1', 'tkn_in': 'WETH-6Cc2', 'amount_in': 0.4555, 'tkn_out': 'USDC-eB48', 'amt_out': 829.9234, 'cid0': '8841057382'}, {'trade_index': 1, 'exchange': 'uniswap_v3', 'tkn_in': 'USDC-eB48', 'amount_in': 829.9234, 'tkn_out': 'WETH-6Cc2', 'amt_out': 0.462, 'cid0': 'b61bc3f2c4'}]}
2023-05-24 19:48:44,937 [fastlane:INFO] - Opportunity with profit: 29.4095 does not meet minimum profit: 1000, discarding.
"""

# ### Read the logfile

# FNAME = "arbbot.log"
# FNAME = "mylog.log"
# FPATH = "../.."
# FFNAME = os.path.join(FPATH, FNAME)
FFNAME = "Analysis016_example.log"


# +
# with open(FFNAME, "r") as f:
#     data = f.read()
# data.splitlines()[-1:]
# -

# ## Analysing data logs

# ### Analysis code

@dataclass
class DataLogEntry():
    time_s: str
    time_ts: int
    tag: str
    data: any
        
    REGEX = r".*? - \[(.*?)::(.*?)].*?\|(.*?)\|.*?==.*?({.*})"
        # 2023-05-24 19:48:44,936 [fastlane:INFO] - [2023-05-24T19:48:44::1684957724] |calculated_arb| == {'type': 'single'} 
        # see https://regex101.com/

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
    def parseall(cls, *, logdata=None, logfn=None):
        """
        parses the entire text of the logfile
        
        :logfn:     log file name
        :logdata:   entire logfile text (alternative to logfn)
        :returns:   list of DataLogLine objects
        """
        if not logdata is None and not logfn is None:
            raise ValueError("Either logdata or logfn must be None")
        if logdata is None and logfn is None:
            raise ValueError("Logdata and logfn must not both be None")
        if not logdata is None:
            lines = (l for l in logdata.splitlines() if l.strip())
            ll = (cls.new(l) for l in lines)
            ll = (l for l in ll if not l is None)
        else:
            with open(logfn, "r") as f:
                lines = (l for l in f)
                ll = (cls.new(l) for l in lines)
                ll = list(l for l in ll if not l is None)
        return list(ll)
    
    @property
    def time(self):
        """datetime object corresponding to time"""
        return datetime.fromtimestamp(self.time_ts)


# ### Parsing test data

ll = DataLogEntry.parseall(logdata=testdata)

[l.tag for l in ll]

# +
# ll[0].data

# +
# ll[-1].data
# -

# ### Parsing file data

ll = DataLogEntry.parseall(logfn=FFNAME)

len(ll)

set([l.tag for l in ll])

ll[-1].data


# ## Analysing full logs

# ### Analysis code

@dataclass
class LogEntry():
    time_s: str
    logentity: str
    loglevel: str
    loglevel_i: int
    msg: str
        
    REGEX = r"(.*?)\[(.*?):(.*?)](.*)"
        # 2023-05-24 19:48:44,936 [fastlane:INFO] - this is the log text
        # see https://regex101.com/
    
    LOGLEVEL = dict(
        DEBUG = 0,
        INFO = 1,
        WARNING = 2,
        ERROR = 3,
    )
    @classmethod
    def new(cls, line):
        """
        reads a single line and instantiates a new object
        """
        m = re.match(cls.REGEX, line)
        if m is None:
            return None
        msg = m.group(4).strip()
        loglevel = m.group(3).upper()
        loglevel_i = cls.LOGLEVEL.get(loglevel, 9)
        if msg[0] == "-":
            msg = msg[1:].strip()
        return cls(
            time_s = m.group(1),
            logentity = m.group(2),
            loglevel = loglevel,
            loglevel_i = loglevel_i,
            msg = msg,
        )
    
    @classmethod
    def parseall(cls, loglevel=None, *, logfn=None):
        """
        parses the entire text of the logfile
        
        :loglevel:  minimum loglevel to parse ()
        :logfn:     log file name
        :returns:   list of DataLogLine objects
        """
#         if not logdata is None and not logfn is None:
#             raise ValueError("Either logdata or logfn must be None")
#         if logdata is None and logfn is None:
#             raise ValueError("Logdata and logfn must not both be None")
#         if not logdata is None:
#             lines = (l for l in logdata.splitlines() if l.strip())
#             ll = (cls.new(l) for l in lines)
#             ll = (l for l in ll if not l is None)
#         else:
        if loglevel is None:
            loglevel = "INFO"
        loglevel = loglevel.upper()
        if not loglevel in cls.LOGLEVEL.keys():
            raise ValueError(f"Loglevel must be one of {list(cls.LOGLEVEL.keys())}; it is '{loglevel}'")
        lli = cls.LOGLEVEL[loglevel]
        with open(logfn, "r") as f:
            lines = (l for l in f)
            ll = (cls.new(l) for l in lines)
            ll = (l for l in ll if not l is None)
            ll = (l for l in ll if l.loglevel_i >= lli)
            ll = list(ll)
        return ll
        


# ### Parsing file data

# #### ERROR only

ll = LogEntry.parseall("ERROR", logfn=FFNAME)
print(f"ERROR entries: {len(ll)}")

ll[0]

# #### ERROR and WARNING

ll = LogEntry.parseall("WARNING", logfn=FFNAME)
print(f"ERROR and WARNING entries: {len(ll)}")

# #### ERROR, WARNING and INFO

ll = LogEntry.parseall("INFO", logfn=FFNAME)
print(f"ERROR, WARNING and INFO entries: {len(ll)}")

# #### ERROR, WARNING, INFO and DEBUG

ll = LogEntry.parseall("DEBUG", logfn=FFNAME)
print(f"ERROR, WARNING, INFO and DEBUG entries: {len(ll)}")


