# Databricks notebook source
__SCRIPT_VERSION__ = "3.4"
__SCRIPT_DATE__ = "23/May/2023"

# COMMAND ----------

from fastlane_bot.bot import CarbonBot as Bot
from fastlane_bot.tools.cpc import ConstantProductCurve as CPC, CPCContainer, T, Pair
from fastlane_bot.tools.analyzer import CPCAnalyzer
from fastlane_bot.tools.cryptocompare import CryptoCompare
import requests
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(Bot))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPC))
print("{0.__name__} v{0.__VERSION__} ({0.__DATE__})".format(CPCAnalyzer))
import pandas as pd
import datetime
import time
import json
from hashlib import md5

logging_path = "/dbfs/FileStore/tables/carbonbot/logs/"
from fastlane_bot import __VERSION__

# COMMAND ----------

# MAGIC %md
# MAGIC # Mainnet Arbitrage Monitoring Bot [A015]

# COMMAND ----------

cid = lambda pair: md5(pair.encode()).hexdigest()
cid("WETH-6Cc2/USDC-eB48")

# COMMAND ----------

bot     = Bot()
CCm     = bot.get_curves()
fn = f"{logging_path}A014-{int(time.time())}.csv.gz"
print (f"Saving curve data as {fn}")
CCm.asdf().to_csv(fn, compression = "gzip")

# COMMAND ----------

class TokenAddress():
    def __init__(self, db):
        self._db = db
        
    def addr_from_ticker(self, ticker):
        return self._db.get_token(key=ticker).address
    a = addr_from_ticker
    
    def ticker_from_addr(self, addr):
        raise NotImplemented()
TA = TokenAddress(bot.db)      
TA.a("WETH-6Cc2")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Header and metadata

# COMMAND ----------

now = datetime.datetime.now()
print("\n\n")
print("*"*100)
print("*"*100)
print(f"ARBITRAGE ANALYSIS RUN @ {now.isoformat().split('.')[0]}Z [{int(now.timestamp())}]")
print("*"*100)
print("*"*100)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Read curves

# COMMAND ----------

# MAGIC %md
# MAGIC ### Read Carbon curves

# COMMAND ----------

#CCm     = CPCContainer.from_df(pd.read_csv("../data/A014-1684148163.csv.gz"))
CCc1_noexcl  = CCm.byparams(exchange="carbon_v1")              # all Carbon positions
CCnc1        = CCm.byparams(exchange="carbon_v1", _inv=True)   # all non-Carbon positions

# COMMAND ----------

# MAGIC %md
# MAGIC #### Remove curves

# COMMAND ----------

c = CCc1_noexcl.bycid0("749015-0")[0]
1/c.p_min, 1/c.p_max
c

# COMMAND ----------

c.cid

# COMMAND ----------

seven_days_from_now = int(now.timestamp())+60*60*24*7
seven_days_from_now

# COMMAND ----------

exclusions0 = {
    '1701411834604692317316873037158841057386-1': 1685428434, # very wide USDC-ETH curve; 23/May
    '4423670769972200025023869896612986749015-0': 1685082834, # vBNT
}

# COMMAND ----------

exclusions = {cid for cid, ts in exclusions0.items() if now.timestamp() < ts}

# COMMAND ----------

CCc1 = CCc1_noexcl.bycids(exclude=exclusions)
len(CCc1_noexcl), len(CCc1)

# COMMAND ----------

print("\n\n"+"="*100)
print("REMOVED CURVES")
print("="*100)
for cid_ in exclusions:
    print(f"{cid_} [for {(exclusions0[cid_]-now.timestamp())/(60*60*24):3.1f} days more]")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Create analyzer and pairs

# COMMAND ----------

CAc1 = CPCAnalyzer(CCc1)
pairs  = CAc1.pairsc()

# COMMAND ----------

# MAGIC %md
# MAGIC ### Read prices and create proxy curves

# COMMAND ----------

# MAGIC %md
# MAGIC #### Preparations

# COMMAND ----------

tokens0 = CAc1.tokens()
tokens0

# COMMAND ----------

print("\n\n"+"="*100)
print("REMOVED TOKENS")
print("="*100)

# COMMAND ----------

REMOVED_TOKENS = {"0x0-1AD5", "LBR-aCcA"}
print(REMOVED_TOKENS)

# COMMAND ----------

tokens = tokens0 - REMOVED_TOKENS
pairs  = CAc1.CC.filter_pairs(bothin=tokens)
tokens_addr = {tkn: TA.a(tkn) for tkn in tokens}
tokens_addrr = {v.lower():k for k,v in tokens_addr.items()}
print("\n\n"+"="*100)
print("TOKEN ADDRESSES")
print("="*100)
for k,v in tokens_addr.items():
    print(f"{k:20} {v}")
tokens_addr, tokens_addrr

# COMMAND ----------

# MAGIC %md
# MAGIC #### CryptoCompare

# COMMAND ----------

tokens_cc = [Pair.n(x) for x in tokens]
tokens_cc

# COMMAND ----------

token_prices_usd_cc = CryptoCompare(apikey=True, verbose=False).query_tokens(tokens_cc)
token_prices_usd_cc

# COMMAND ----------

missing_cc = set(tokens_cc) - set(token_prices_usd_cc)
missing_cc

# COMMAND ----------

token_prices_usd = token_prices_usd_cc
P0 = lambda tknb,tknq: token_prices_usd[tknb.upper()]/token_prices_usd[tknq.upper()]
def P(pair):
    try: 
        return P0(*Pair.n(pair).split("/"))
    except KeyError:
        return None

prices_by_pair = {pair: P(pair) for pair in pairs}
prices_n_by_pair = {Pair.n(pair): p for pair, p in prices_by_pair.items()}
print("\n\n"+"="*100)
print("PRICES BY PAIR (CRYPTOCOMPARE)")
print("="*100)
for k,v in prices_n_by_pair.items():
    if not v is None:
        print(f"{k:20} {v:20,.6f}")
    else:
        print(f"{k:20}                  ---")

# COMMAND ----------

proxy_curves_cc = [
    CPC.from_pk(p=price, pair=pair, k=1000, cid=cid(pair+"CG"), params=dict(exchange="ccomp")) 
    for pair, price in prices_by_pair.items() if not price is None
]
#proxy_curves_cc

# COMMAND ----------

cid

# COMMAND ----------

# MAGIC %md
# MAGIC #### CoinGecko

# COMMAND ----------

addr_s = ",".join(x for x in tokens_addr.values())
url = "https://api.coingecko.com/api/v3/simple/token_price/ethereum"
params = dict(contract_addresses=addr_s, vs_currencies="usd")
r = requests.get(url, params=params)
token_prices_usd_cg_raw = {tokens_addrr[k]: v["usd"] for k,v in r.json().items()}
token_prices_usd_cg = {Pair.n(tokens_addrr[k]).upper(): v["usd"] for k,v in r.json().items()}
token_prices_usd_cg_raw

# COMMAND ----------

missing_cg = set(tokens_addr) - set(token_prices_usd_cg_raw)
missing_cg

# COMMAND ----------

token_prices_usd = token_prices_usd_cg
P0 = lambda tknb,tknq: token_prices_usd[tknb.upper()]/token_prices_usd[tknq.upper()]
def P(pair):
    try: 
        return P0(*Pair.n(pair).split("/"))
    except KeyError:
        return None

prices_by_pair = {pair: P(pair) for pair in pairs}
prices_n_by_pair = {Pair.n(pair): p for pair, p in prices_by_pair.items()}
print("\n\n"+"="*100)
print("PRICES BY PAIR (COINGECKO)")
print("="*100)
for k,v in prices_n_by_pair.items():
    if not v is None:
        print(f"{k:20} {v:20,.6f}")
    else:
        print(f"{k:20}                  ---")

# COMMAND ----------

proxy_curves_cg = [
    CPC.from_pk(p=price, pair=pair, k=1000, cid=cid(pair+"CG"), params=dict(exchange="cgecko")) 
    for pair, price in prices_by_pair.items() if not price is None
]
#proxy_curves_cg

# COMMAND ----------

# MAGIC %md
# MAGIC #### Assembly

# COMMAND ----------

# CCother = CCu3.bypairs(CCc1.pairs())
CCcg = CPCContainer(proxy_curves_cg)
CCcc = CPCContainer(proxy_curves_cc)
CCfull = CCc1.copy().add(CCcg).add(CCcc)
#CAother = CPCAnalyzer(CCother)
CAfull = CPCAnalyzer(CCfull)
CAnc1  = CPCAnalyzer(CCnc1)
print(f"CAfull: {len(CAfull.CC):4} entries")
print(f"CAnc1:  {len(CAnc1.CC):4} entries")

# COMMAND ----------

# MAGIC %md
# MAGIC ## By-pair data for Carbon

# COMMAND ----------

# MAGIC %md
# MAGIC ### Count by pairs

# COMMAND ----------

dfc1 = CAc1.count_by_pairs().rename(columns=dict(count="carbon")).astype(str)
dfnc1 = CAnc1.count_by_pairs().rename(columns=dict(count="other")).astype(str)
print("\n\n"+"="*100)
print("AVAILABLE PAIRS (CARBON AND OTHER)")
print("="*100)
df = pd.concat([dfc1, dfnc1], axis=1).fillna("").sort_index()
print(df)
pairs_df = df
#df

# COMMAND ----------

dfc1 = CAc1.count_by_pairs().rename(columns=dict(count="carbon")).astype(str)
dfnc1 = CAnc1.count_by_pairs().rename(columns=dict(count="other")).astype(str)
print("\n\n"+"="*100)
print("CARBON PAIRS NOT MATCHED")
print("="*100)
print(df[df["other"]==""])

# COMMAND ----------

dfc1 = CAc1.count_by_pairs().rename(columns=dict(count="carbon")).astype(str)
dfnc1 = CAnc1.count_by_pairs().rename(columns=dict(count="other")).astype(str)
print("\n\n"+"="*100)
print("OTHER PAIRS WITH NO CARBON")
print("="*100)
print(df[df["carbon"]==""])

# COMMAND ----------

print("\n\n                    CARBON     CGECKO   CCOMP")
print(f"Pairs:                {len(pairs):4}    {len(CCcg.pairs()):7} {len(CCcc.pairs()):7}")
print(f"Tokens:               {len(tokens):4}    {len(CCcg.tokens()):7} {len(CCcc.tokens()):7}")
print(f"Curves:               {len(CAc1.CC):4}    {len(CCcg):7} {len(CCcc):7}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### Calculate by-pair statistics

# COMMAND ----------

print("\n\n")
print("*"*100)
print(f"BY-PAIR DATA")
print("*"*100)

# COMMAND ----------

pasdf    = CAfull.pool_arbitrage_statistics()
pasnc1df = CAnc1.pool_arbitrage_statistics(only_pairs_with_carbon=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Print by-pair statistics

# COMMAND ----------

def prints(*x):
    global s
    s += " ".join([str(x_) for x_ in x])
    s += "\n"
out_by_pair = dict()
carbon_by_pair = dict()
other_by_pair = dict()

for pair in list(pairs):
    s = ""
    prints("\n\n"+"="*100)
    prints(f"Pair = {pair}")
    prints("="*100)
    df = pasdf.loc[Pair.n(pair)]
    try:
        nc1df = pasnc1df.loc[Pair.n(pair)]
    except:
        nc1df = pd.DataFrame()
    hasproxydata = len(df.reset_index()[df.reset_index()["exchange"]=="cgecko"])>0
    if hasproxydata:
        prints("\n--- ALL CARBON AND REFERENCE POSITIONS ---")
        prints(df.to_string())
        carbon_by_pair[pair] = [[k,v] for k,v in df.to_dict(orient="index").items()]
        prints("\n--- IN-THE-MONEY POSITIONS ---")
        dfitm = df[df["itm"]=="x"]
        if len(dfitm) > 0:
            prints(dfitm.to_string())
        else:
            prints("-None-")
        prints("\n--- ALL NON-CARBON POSITIONS ---")
        if len(nc1df) > 0:
            prints(nc1df.to_string())
        else:
            prints("-None-")
        other_by_pair[pair] = [[k,v] for k,v in nc1df.to_dict(orient="index").items()]
        
    else:
        prints("\n--- NO PRICE DATA AVAILABLE ---")
    
    out_by_pair[pair] = s
    print(s)


# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary data

# COMMAND ----------

print("\n\n")
print("*"*100)
print(f"SUMMARY DATA")
print("*"*100)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create summary data

# COMMAND ----------

itmcarbdf = pasdf.query("exchange == 'carbon_v1'").query("itm == 'x'")

# COMMAND ----------

itmcarb_pairs = sorted({x[0] for x in tuple(itmcarbdf.index)})
itmcarb_pairs

# COMMAND ----------

itmcarb_pos = itmcarbdf.reset_index().to_dict(orient="records")
itmcarb_pos[:2]

# COMMAND ----------

itmcarb_pos_bypair = {
    pair: [x for x in itmcarb_pos if x["pair"] == pair]
    for pair in itmcarb_pairs
}
#itmcarb_pos_bypair

# COMMAND ----------

missing_pairs = [pair for pair, price in prices_by_pair.items() if price is None]
missing_pairs

# COMMAND ----------

# MAGIC %md
# MAGIC ### Convert summary data to Telegram

# COMMAND ----------

telegram_data = dict(
    script_version = __SCRIPT_VERSION__,         # version number of the script producing this record
    script_version_dt = __SCRIPT_DATE__,         # ditto date
    time_ts = int(now.timestamp()),              # timestamp (epoch)
    time_iso = now.isoformat().split('.')[0],    # timestap (iso format)
    prices_usd = token_prices_usd,               # token prices (usd)
    pairs0 = pairs_df.to_dict(orient="index"),   # carbon pairs and other pairs count       
    pairs = list(pairs),                         # all carbon pairs
    pairs_n = len(pairs),                        # ...number
    curves_n = len(CCc1),                        # number of Carbon curves
    itm_pairs = itmcarb_pairs,                   # pairs that have curves in the money (list)
    itm_pairs_n = len(itmcarb_pairs),            # ...number
    itm_pos = itmcarb_pos,                       # carbon and reference positions that are in the money (list)
    itm_pos_n = len(itmcarb_pos),                # ...number
    all_pos_bp = carbon_by_pair,                 # all carbon and reference positions by pair (dict->list)
    all_pos_bp_n = len(carbon_by_pair),          # ...number
    other_pos_bp = other_by_pair,                # all other positions (dict->list)
    other_pos_bp_n = len(other_by_pair),         # ...number
    itm_pos_bypair = itmcarb_pos_bypair,         # ditto, but dict[pair] -> list
    missing_pairs = missing_pairs,               # missing pairs
    missing_pairs_n = len(missing_pairs),        # ...number
    removed_curves = list(exclusions),           # curves that have been explicitly removed
    removed_curves_n = len(exclusions),          # ...number
    removed_tokens = list(REMOVED_TOKENS),       # removed tokens
    removed_tokens_n = len(REMOVED_TOKENS),      # ...number
    out_by_pair = out_by_pair                    # output by pair
)

# COMMAND ----------

td = telegram_data
summary_data = dict()
s = ""
s += f"="*47
s += f"\nARBITRAGE RUN @ {td['time_iso']}Z\n"
s += f"="*47+"\n"
s += f"Removed tokens:          {td['removed_tokens_n']:3}\n"
s += f"Total pairs:             {td['pairs_n']:3}\n"
s += f"Missing pairs:           {td['missing_pairs_n']:3}\n"
s += f"Removed curves:          {td['removed_curves_n']:3}\n"
s += f"In-the-money pairs:      {td['itm_pairs_n']:3}\n"
s += f"Total curves:            {td['curves_n']:3}\n"
s += f"In-the-money curves:     {td['itm_pos_n']:3}\n"
total_vl_usd = 0
total_arbval = 0
s += "-----------------------------------------------\n"
s += "PAIR         CID          VLOCK    ARBPC    VAL\n"
s += "-----------------------------------------------\n"
for p in td['itm_pos']:
    price_pair = prices_n_by_pair[p['pair']] or 0
    price_pc0 = abs(price_pair/p['price']-1)
    price_pc = f"{price_pc0*100:8.1f}%"
    vl_token = p['pair'].split('/')[0].split("-")[0]
    vl_token_price = token_prices_usd.get(vl_token.upper())
    if not vl_token_price:
        continue
    vl_usd = p['vl']*vl_token_price
    total_vl_usd += vl_usd
    arbval = vl_usd * abs(price_pair/p['price']-1)
    if price_pc.endswith("100.0%"): 
        price_pc = "         "
        arbval = 0
    total_arbval += arbval
    d = dict(
        pair = p['pair'],
        cid0 = p["cid0"],
        vl_usd = vl_usd,
        price_pc = price_pc0,
        arbval = arbval,
        price = price_pair,
    )
    summary_data[p["cid0"]] = d
    #print(d)
    s += f"{p['pair']:12} "
    s += f"{p['cid0'][-8:]:8} "
    s += f"{vl_usd:9,.0f}"
    s += f"{price_pc} "
    s += f"{arbval:6,.0f}"
    #s += f"[{p['bsv']}; p={price_pair:,.2f}]"
    #s += f"\n{p}"
    s += "\n"
s += "-----------------------------------------------\n"
s += f"TOTAL {total_vl_usd:25,.0f}   {100*total_arbval/total_vl_usd:5.1f}% {total_arbval:6,.0F}\n"
s += "===============================================\n"
s += """
All numbers in USDC. Figures above are upper
bounds, not estimates. False positives are to
be expected, but not false negatives.\n
"""[1:]

telegram_data["summary_text"] = s
telegram_data["summary_data"] = summary_data
print()
print(s)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Notifications

# COMMAND ----------



# COMMAND ----------

# data frame with arbitrage opportunities...
arbdf = pd.DataFrame.from_dict(summary_data.values())[["cid0", "arbval"]].set_index("cid0")
#arbdf

# COMMAND ----------

# ...and data frame of all tracked positions, arb or not...
ciddf = pd.DataFrame([[c.cid0 for c in CCc1],[0]*len(CCc1)], index="cid0,arbval".split(",")).T.set_index("cid0")
#ciddf

# COMMAND ----------

# ...combined into one dataframe (arb first)
notifdf = arbdf.combine_first(ciddf)
#notifdf

# COMMAND ----------

# read the dataframe of previous arb notification levels...
try:
    notifcdf0 = pd.read_csv("Analysis_015.notifdf.csv").set_index("cid0")
except:
    notifcdf0 = ciddf
notifcdf = notifcdf0.copy()

# COMMAND ----------

# ...and augment it with current arb levels
notifcdf["arbval1"] = notifdf["arbval"]
#notifcdf

# COMMAND ----------

# notification is due where level goes from < 50 to > 50
notifbreachdf = notifcdf.query("arbval1>=50 and arbval<50")
notifbreachdf = notifbreachdf.drop("arbval", axis=1).rename(columns={"arbval1": "arbval"})
notifbreachdf

# COMMAND ----------

# update the previous notifications df with the current notifications
notifndf = notifbreachdf.combine_first(notifcdf0)
notifndf.to_csv(f"{logging_path}Analysis_015.notifdf.csv")

# COMMAND ----------

# create all new notifications
notif_str = "\n".join([
    "[{td[time_iso]}::{td[time_ts]}] |new| == {d}\n".format(
        cid0=cid0, 
        td=td, 
        d = json.dumps(dict(
            pair = summary_data[cid0]["pair"],
            cid0=cid0,
            arbval = x["arbval"],
            vl_usd = summary_data[cid0]["vl_usd"],
            price = summary_data[cid0]["price"],
            #sd = summary_data[cid0],
        ))
    )
    for cid0, x in notifbreachdf.to_dict(orient="index").items()
])
notif_str

# COMMAND ----------

# print notifications (if any)
if notif_str:
    s0 = f"="*47
    s0 += f"\nNOTICATIONS\n"
    s0 += f"="*47
    print(s)
    print(notif_str)

# COMMAND ----------

#notifcdf.to_csv("Analysis_015.notifdf.csv")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Save some files

# COMMAND ----------

with open(f"{logging_path}Analysis_015.notifications", "w") as f:
    f.write(notif_str)

# COMMAND ----------

with open(f"{logging_path}Analysis_015.latest.out", "w") as f:
    f.write(telegram_data["summary_text"])

# COMMAND ----------

with open(f"{logging_path}Analysis_015.latest.json", "w") as f:
    f.write(json.dumps(telegram_data))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Telegram Notifications

# COMMAND ----------

# import json
# import requests
# import os

# TOKEN = os.environ['TOKEN']
# GROUP_ID = os.environ['GROUP_ID']
# last_line = notif_str.split('\n\n')[-1].strip().split('==')[-1]  # this would come from somewhere in your script

# # path to the file where last message is stored
# last_line_file_path = '/dbfs/FileStore/tables/carbonbot/logs/last_line.txt'

# try:
#     with open(last_line_file_path, 'r') as file:
#         previous_last_line = file.read().strip()
# except FileNotFoundError:
#     previous_last_line = None

# # If last_line is different from previous_last_line, send a new message.
# if last_line != previous_last_line:
#     url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
#     headers = {'Content-Type': 'application/json'}
#     data = json.dumps({'chat_id': GROUP_ID, 'text': last_line})

#     response = requests.post(url, headers=headers, data=data)

#     if response.status_code == 200:
#         print("Message sent successfully.")
#         # If message is sent successfully, update the last_line in the file
#         with open(last_line_file_path, 'w') as file:
#             file.write(last_line)
#     else:
#         print("Failed to send message.")
# else:
#     print('last line did not change...')

