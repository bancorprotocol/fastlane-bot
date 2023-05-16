"""
Carbon helper module - retrieve data from CryptoCompare
"""
__VERSION__ = "2.1"
__DATE__ = "16/May/2023"

import os as _os
import pandas as _pd
import hashlib as _hashlib
import requests as _requests
import pickle as _pickle
from collections import namedtuple as _namedtuple


pair_t = _namedtuple("pair", "tknb,tknq")

class CryptoCompare():
    """
    simple class formalizing interaction with the crypto compare API 
    
    :apikeyname:    the OS environment variable holding the API key
                    only used if no `apikey`; default is class.APIKEYNAME
    :apikey:        the API key; if True use without API key
    :datapath:      the path where all data is written (and read from)
    :raiseonerror:  if True, errors usually lead to an exception, otherwise to a None return
    """
    __VERSION__ = __VERSION__
    __DATE__ = __DATE__

    BASEURL = "https://min-api.cryptocompare.com" # must NOT end with /
    APIKEYNAME = "CCAPIKEY" # the name of the environment variable containing the API key
    RAISEONERROR = True
    DATAPATH = "cryptocompare"
    
    DEFAULT_TSYM = "usd"
    DEFAULT_LIMIT = 2000
    
    def __init__(self, *, apikeyname=None, apikey=None, raiseonerror=None, verbose=False):
        if raiseonerror is None:
            raiseonerror = self.RAISEONERROR
        self.raiseonerror = raiseonerror  
        if not (isinstance(apikey, str) or apikey is None or apikey is True):
            raise ValueError("apikey must be a string, None, or True", apikey)  
        if apikey is None:
            if apikeyname is None:
                apikeyname = self.APIKEYNAME
            apikey = _os.getenv(apikeyname)
            if apikey is None:
                print(f"Can't find API key {apikeyname} in environment variables.")
                print(f"Use `export {apikeyname}=<value>` to set it BEFORE you launch Jupyter")
                raise RuntimeError(f"API key not present. Use `export {apikeyname}=<value>` to set it before launching Jupyter.")
        self.apikey = apikey
        self.verbose = verbose
    
    def url(self, endpoint):
        """
        returns the URL of a given endpoint
        """
        return f"{self.BASEURL}{endpoint}"
    
    @property
    def keydigest(self):
        """returns signature (=SHA1 hash) of the API key, or 0000... if anonymous"""
        if self.apikey is True:
            return "0"*40
        return _hashlib.sha1(self.apikey.encode()).hexdigest()
    
    def datafn(self, fn):
        """returns the full data file name, including path"""
        return _os.path.join(self.DATAPATH, fn)

    def cache(self, item):
        """
        reads a data item from the data cache
        """
        try:
            with open(self.datafn(f"{item}.pickle"), "rb") as f:
                result = _pickle.load(f)
        except:
            if not self.raiseonerror:
                return None
            raise
        return result
    
    def write_cache(self, item, data):
        """
        writes `data` to the cache under the name `item`
        
        :returns:    `item` on success, None (or raises) on failure
        """
        try:
            with open(self.datafn(f"{item}.pickle"), "wb") as f:
                _pickle.dump(data, f)
        except:
            if not self.raiseonerror:
                return None
            raise           
        return item
    
    QUERY_GET = "GET"
    QUERY_POST = "POST"
    def query(self, endpoint, params=None, method=None):
        """
        generic API query
        
        :endpoint:  the API endpoint to call, eg "/all/exchanges"
        :params:    the API parameters (parameters with value None will be removed)
        :method:    http method; default is QUERY_GET
        """
        if method is None:
            method = self.QUERY_GET
        if params is None:
            params = dict()
        url = self.url(endpoint)
        paramsq = {k:v for k,v in params.items() if not v is None}
        if self.verbose:
            print("[query]", url, paramsq, f"[{str(self.keydigest)[:4]}]")
        if not self.apikey is True:
            paramsq["api_key"] = self.apikey
        
        if method == self.QUERY_GET:
            r = _requests.get(url, params=paramsq)
        elif method == self.QUERY_POST:
            raise ValueError("Method QUERY_POST has not been implemented yet.")
        else:
            raise ValueError("Unknown method. Use QUERY_XXX constants", method)
        
        if not r:
            if self.raiseonerror:
                raise RuntimeError(f"API query not successful (status={r.status})", r)
            else:
                return None
        return r
    
    def query_allexchanges(self):
        """
        endpoint = /data/v4/all/exchanges
        
        https://min-api.cryptocompare.com/documentation?key=Other&cat=allExchangesV4Endpoint
        """
        r = self.query(
            endpoint="/data/v4/all/exchanges"
        )
        if r is None: return r
        return r.json().get("Data")

    
    def _cache_xxx(self, item, updatemethod, readonfail=True, updateonfail=False):
        """
        generic cached access
        
        :item:           the name of the item in the cache
        :updatemethod:   the method to call for updating it
        :readonfail:     if True, on cache miss updatemethod is called
        :updateonfail:   it True, on cache miss, updatemethod is called an item is 
                         written to cache
        """
        if updateonfail:
            readonfail = True
        try:
            return self.cache(item)
        except:
            print(f"[_cache_xxx] cache miss for item {item}")
            if readonfail:
                print(f"[_cache_xxx] reading {item} from API")
                data = updatemethod()
                if updateonfail:
                    print(f"[_cache_xxx] updating cache for {item} from API")
                    self.write_cache(item, data)
                return data
            else:
                if self.raiseonerror:
                    raise
                else:
                    return None
        
    def cache_allexchanges(self, readonfail=True, updateonfail=False):
        """cached access to query_allexchanges"""
        return self._cache_xxx(
            item="query_allexchanges", 
            updatemethod=self.query_allexchanges
        )
    
    def query_ratelimit(self):
        """
        endpoint = /stats/rate/limit
        
        https://min-api.cryptocompare.com/documentation?key=Other&cat=rateLimitEndpoint
        """
        r = self.query(
            endpoint="/stats/rate/limit"
        )
        if r is None: return r
        return r.json().get("Data")
        
    def query_coinlist(self):
        """
        endpoint = /data/all/coinlist
        
        https://min-api.cryptocompare.com/documentation?key=Other&cat=allCoinsWithContentEndpoint
        """
        r = self.query(
            endpoint="/data/all/coinlist"
        )
        if r is None: return r
        return r.json().get("Data")
    
    def cache_coinlist(self, readonfail=True, updateonfail=False):
        """cached access to query_coinlist"""
        return self._cache_xxx(
            item="query_coinlist", 
            updatemethod=self.query_coinlist
        )
        
    def query_indexlist(self):
        """
        endpoint = /data/index/list
        
        https://min-api.cryptocompare.com/documentation?key=Index&cat=listOfIndices
        """
        r = self.query(
            endpoint="/data/index/list"
        )
        if r is None: return r
        return r.json().get("Data")
    
    def cache_indexlist(self, readonfail=True, updateonfail=False):
        """cached access to query_indexlist"""
        return self._cache_xxx(
            item="query_indexlist", 
            updatemethod=self.query_indexlist
        )
    
    @staticmethod
    def ts_tocc(ts):
        """
        convert timestamp into format needed by CryptoCompare
        
        :ts:     the timestamp in any format that works for pd.Timestamp(ts)
        """
        return int(_pd.Timestamp(ts).timestamp())
    
    @staticmethod
    def ts_fromcc(ts):
        """
        convert timestamp from CryptoCompare format into pd.Timestamp format
        """
        return _pd.to_datetime(ts, unit='s', origin='unix') 
    
    FREQ_DAILY = "day"
    FD = FREQ_DAILY
    FREQ_HOURLY = "hour"
    FH = FREQ_HOURLY
    FREQ_MINUTELY = "minute"
    FM = FREQ_MINUTELY
    FREQS = (FREQ_DAILY, FREQ_HOURLY, FREQ_MINUTELY)
    def query_freqlypair(self, freq, fsym=None, tsym=None, e=None, limit=False, toTs=None, aspandas=True):
        """
        endpoints = /data/v2/histoday, /data/v2/histohour, /data/v2/histominute
        
        :freq:     FREQ_DAILY/FD, FREQ_HOURLY/FH, or FREQ_MINUTELY/FM
        :fsym:     cryptocurrency symbol of interest
        :tsym:     currency symbol to convert into
        :e:        exchange to obtain data from
        :limit:    number of data points to return (max: 2000; False defaults to that number)
        :toTs:     returns historical data BEFORE that timestamp
                   timestamp format either 1452680400 or pd.Timestamp compatible string 
        
        https://min-api.cryptocompare.com/documentation?key=Historical&cat=dataHistoday
        https://min-api.cryptocompare.com/documentation?key=Historical&cat=dataHistohour
        https://min-api.cryptocompare.com/documentation?key=Historical&cat=dataHistominute
        """
        if not freq in self.FREQS:
            raise ValueError("Unknow frequency {}. Use the FREQ_XXX constants provided.")
        endpoint = f"/data/v2/histo{freq}"
        params = {
                "fsym":     fsym,
                "tsym":     tsym if not tsym is None else self.DEFAULT_TSYM,
                "e":        e,
                "limit":    limit if not limit is False else self.DEFAULT_LIMIT,
                "toTs":     toTs,
        }
        r = self.query(endpoint=endpoint, params=params)
        if r is None: return r
        r_json = r.json()
        if r_json.get("Response") == "Error":
            if self.raiseonerror:
                raise RuntimeError("Query not successful", r, r_json, endpoint, params)
            else:
                return None
        if not aspandas:
            return r_json().get("Data")
        try:   
            # print("[query_freqlypair]", endpoint, params, r)
            # print("[query_freqlypair] r", r_json())
            
            df = _pd.DataFrame.from_records(r_json["Data"]["Data"])
            df["datetime"] = [self.ts_fromcc(ts) for ts in df["time"]]
            df = df.set_index("datetime")
            del df["conversionType"]
            del df["conversionSymbol"]
            del df["time"]
            df = df[['open', 'close', 'high', 'low', 'volumefrom', 'volumeto']]
            return df
        except RuntimeError as e:
            if self.raiseonerror: 
                raise RuntimeError("Error {e}", endpoint, params, r)
            return None
    
    def query_dailypair(self, *args, **kwargs):
        """alias for query_freqlypair(FREQ_DAILY, ...)"""
        return self.query_freqlypair(self.FREQ_DAILY, *args, **kwargs)
    
    def query_hourlypair(self, *args, **kwargs):
        """alias for query_freqlypair(FREQ_HOURLY, ...)"""
        return self.query_freqlypair(self.FREQ_HOURLY, *args, **kwargs)

    def query_minutelypair(self, *args, **kwargs):
        """alias for query_freqlypair(FREQ_MINUTELY, ...)"""
        return self.query_freqlypair(self.FREQ_MINUTELY, *args, **kwargs)

    def query_tokens(self, fsyms, tsym=None, aspandas=False):
        """
        endpoint = /data/pricemulti?fsyms=BTC,ETH&tsyms=USD,EUR
        
        :fsyms:     list of cryptocurrency symbols of interest
        :tsym:      currency symbol to convert into
        :aspandas:  if True, returns result as pandas data frame
        
        https://min-api.cryptocompare.com/documentation?key=Price&cat=multipleSymbolsPriceEndpoint
        """
        endpoint = f"/data/pricemulti"
        params = {
                "fsyms":     fsyms,
                "tsyms":     tsym if not tsym is None else self.DEFAULT_TSYM,
        }
        r = self.query(endpoint=endpoint, params=params)
        if r is None: return r
        r_json = r.json()
        if r_json.get("Response") == "Error":
            if self.raiseonerror:
                raise RuntimeError("Query not successful", r, r_json, endpoint, params)
            else:
                return None
        df = _pd.DataFrame(r.json()).T
        if aspandas:
            return df
        dct = dict(df[df.columns[0]])
        return dct
        
        
        
    def ccycodes(self, symonly=True, fn=None):
        """
        returns information on currency codes
        
        :symonly:   if True (default) only return list of ccy symbold
        :fn:        the filename of the currency code file
        """
        if symonly:
            return self.join( self.unjoin(self.CCYCODES) )
        if fn is None:
            fn = _os.path.join(self.DATAPATH, "isoccy.csv")
        df = _pd.read_csv(fn, index_col=False)
        if symonly:
            symbols = list(set(df["Symbol"]))
            symbols.sort()
            return tuple(symbols)
        return df
    
    CCYCODES = """
    AED,AFN,ALL,AMD,ANG,AOA,ARS,AUD,AWG,AZN,BAM,BBD,BDT,BGN,BHD,BIF,BMD,
    BND,BOB,BOV,BRL,BSD,BTN,BWP,BYN,BZD,CAD,CDF,CHE,CHF,CHW,CLF,CLP,CNY,
    COP,COU,CRC,CUC,CUP,CVE,CZK,DJF,DKK,DOP,DZD,EGP,ERN,ETB,EUR,FJD,FKP,
    GBP,GEL,GHS,GIP,GMD,GNF,GTQ,GYD,HKD,HNL,HRK,HTG,HUF,IDR,ILS,INR,IQD,
    IRR,ISK,JMD,JOD,JPY,KES,KGS,KHR,KMF,KPW,KRW,KWD,KYD,KZT,LAK,LBP,LKR,
    LRD,LSL,LYD,MAD,MDL,MGA,MKD,MMK,MNT,MOP,MRU,MUR,MVR,MWK,MXN,MXV,MYR,
    MZN,NAD,NGN,NIO,NOK,NPR,NZD,OMR,PAB,PEN,PGK,PHP,PKR,PLN,PYG,QAR,RON,
    RSD,RUB,RWF,SAR,SBD,SCR,SDG,SEK,SGD,SHP,SLL,SOS,SRD,SSP,STN,SVC,SYP,
    SZL,THB,TJS,TMT,TND,TOP,TRY,TTD,TWD,TZS,UAH,UGX,USD,USN,UYI,UYU,UYW,
    UZS,VES,VND,VUV,WST,XAF,XAG,XAU,XCD,XDR,XOF,XPD,XPF,XPT,XSU,XUA,YER,
    ZAR,ZMW,ZWL
    """.strip()

    @staticmethod
    def join(tpl, sep=None):
        """join the tpl into comma separated strings"""
        if sep is None: sep = ", "
        return sep.join(str(s) for s in tpl)
        
    @staticmethod
    def unjoin(jstr, filter=None, sep=None):
        """
        unjoin the join string, stripping the result
        
        :jstr:      a (typically comma) separated string
        :filter:    filter to be applied (default: str)
        :sep:       the separator (default: comma)
        :returns:   tuple
        """
        if sep is None: sep = ","
        result = jstr.split(sep)
        if filter is None:
            filter = str
        result = ( filter(c.strip()) for c in result)
        return tuple(result)

    def aggr_query(self, 
            pairs, 
            fields=None, 
            incl_raw=True, 
            incl_raw_aggr=True, 
            incl_grand_aggr=True, 
            freq=None, **kwargs):
        """
        gets the data for pairs from the API and converts it into tables 
        
        :pairs:             the pairs to download, either comma separeted "ETH/USD, BTC/GBP, ..." 
                            or as tuple of tuples (("ETH", "USD"), ...)
        :fields:            the fields for which to create aggredate data frames, either comma separated
                            or as tuple/list; use FREQ_CLOSE and other FIELD_XXX constants here
        :incl_raw:          whether to include the individual raw data frames
        :incl_raw_aggr:     whether to include the aggregate raw data frame
        :incl_grand_aggr:   whether to include a grand aggregate (with double col name)
        :freq:              the data frequency [FREQ_DAILY (default), FREQ_HOURLY, FREQ_MINUTELY] 
        :kwargs:            passed through to `query_freqlypair` (eg `e`, `limit`, `toTs`)
        :returns:           dict with the results
        
        dict structure
        
        -gaggr
            - [data]
        -aggr
            -open
                - [data]
            -close
                - [data]
            ...
        -rawaggr
            - [data]
        -raw
            - "ETH/USD"
                - [data]
            ...
        """
        if fields is None:
            fields = self.FIELD_DEFAULT
        if isinstance(fields, str):
            fields = self.unjoin(fields)
        print("[aggr_query] fields", fields)
            
        if isinstance(pairs, str):
            pairs = tuple( self.pt_from_pair(p) for p in self.unjoin(pairs) )
        print("[aggr_query] pairs", pairs)
        
        if freq is None:
            freq = self.FREQ_DAILY
            
        result = {
            "gaggr": None,
            "aggr": None,
            "rawaggr": None,
            "raw": None,
        }
            
        print("[aggr_query] Querying for raw table", len(pairs))
        raw_tables = {
            (fsym, tsym): self.query_freqlypair(freq, fsym=fsym, tsym=tsym)
            for fsym, tsym in pairs
        }
        df_raw = _pd.concat(raw_tables, axis=1)
        result_raw = {self.pair_from_pt(p):v for p, v in raw_tables.items()}
        if incl_raw:
            result["raw"] = result_raw
        if incl_raw_aggr:
            result["rawaggr"] = _pd.concat(result_raw, axis=1)
        
        print("[aggr_query] Creating aggregate table")
        result["aggr"] = {
            field: self.reformat_raw_df(df_raw, field=field, dblcolnm=incl_grand_aggr) 
            for field in fields
        }
        if incl_grand_aggr:
            result["gaggr"] = _pd.concat(result["aggr"].values(), axis=1)
        return result
    
    @staticmethod
    def pairs_fields_from_df(df):
        """
        pairs and fields present in the dataframe
        
        :df:        data frame with index = (base token, quote token, field)
        :returns:   dict pairs: tuple( (tknp1, tnkq1), ...), fields: (field1, ...)
        """
        pairs  = ((tknb, tknq) for tknb, tknq, field in df.columns)
        pairs  = tuple(set(pairs))
        fields = (field for tknb, tknq, field in df.columns)
        fields = tuple(set(fields))
        return {"pairs": pairs, "fields": fields}

    FIELD_CLOSE = "close"
    FIELD_OPEN = "open"
    FIELD_HIGH = "high"
    FIELD_LOW = "low"
    FIELD_DEFAULT = FIELD_CLOSE
    @classmethod
    def reformat_raw_df(cls, df, field=None, dblcolnm=False):
        """
        reformats a raw df
        
        :df:        the raw df, as returned by a concatenation eg of daily_pair calls
        :field:     the name of the price field to use for the price
                    use FIELD_OPEN, FIELD_CLOSE etc; default: FIELD_DEFAULT
        :dblcolnm:  if True, the colname is (field, pair) instead of pair
        :returns:   the reformatted data frame
        """
        if field is None:
            field = cls.FIELD_DEFAULT

        if dblcolnm:
            result = (
                df[(*pair, field)].rename((field, f"{pair[0]}/{pair[1]}"), inplace=True)
                for pair in cls.pairs_fields_from_df(df)["pairs"]
            )
        else:
            result = (
                df[(*pair, field)].rename(f"{pair[0]}/{pair[1]}", inplace=True)
                for pair in cls.pairs_fields_from_df(df)["pairs"]
            )

        return _pd.concat(list(result), axis=1)

    @staticmethod
    def pt_from_pair(pair):
        """
        creates a pair tuple (tknb, tknq) from a pair 'TKNB/TKNQ'
        """
        return pair_t(*pair.split("/"))
    
    @staticmethod
    def pair_from_pt(pair_t):
        """
        creates a pair 'TKNB/TKNQ' from a pair tuple (tknb, tknq)
        """
        return "/".join(pair_t)

    @classmethod
    def coinlist(cls, coins, sep=",", aspt=False):
        """
        creates a coin list from separated string (does not touch lists)

        :coins:    either a string or a list/tuple
        :sep:      the separator of the string
        :aspt:     if True, result returned as pair tuple (using `pt_from_pair`)
        :returns:  original if not str; otherwise tuple of string or pr
        """
        f = cls.pt_from_pair if aspt else lambda x: x
        if isinstance(coins, str):
            return tuple(f(c.strip()) for c in coins.split(sep))
        else:
            return coins

    @classmethod
    def create_pairs(cls, coins, quotecoins=None):
        """
        create pair tuples from all possible combinations of coins and quotecoins
        
        :coins:        a list of coins, either ("tkn1", "tkn2") or "tkn1, tkn2"
        :quotecoins:   a list of quote coins; if None set equal to coins
        :returns:      all combinations as tuples (c, qc) with c!=qc
        """
        coins = cls.coinlist(coins)
        if quotecoins is None:
            quotecoins = coins
        else:
            quotecoins = cls.coinlist(quotecoins)
        result = ( (c,q) for q in quotecoins for c in coins)
        result = ( pair_t(c,q) for c,q in result if c != q)
        return tuple (result)

      