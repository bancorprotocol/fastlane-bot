"""
Mock database objects for testing the Fastlane project.

(c) Copyright Bprotocol foundation 2023.
Licensed under MIT
"""
import csv
import os
from _decimal import Decimal
from typing import List, Optional
from collections import namedtuple
from fastlane_bot.db.model_managers import TokenManager, PairManager, PoolManager

PROJECT_PATH = os.path.normpath(f"{os.getcwd()}")


def load_csv_data(filename: str):
    """
    Load data from a CSV file.

    Parameters
    ----------
    filename
        The name of the CSV file to load.

    Returns
    -------
    data
        The data from the CSV file.

    """
    file_path = os.path.normpath(f"{PROJECT_PATH}/fastlane_bot/data/{filename}")
    data = []

    with open(file_path, mode="r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)

    return data


class MockTokenManager(TokenManager):
    """
    A mock TokenManager class.
    """
    tokens = load_csv_data("tokens.csv")

    def get_token(self, **kwargs) -> Optional[namedtuple]:
        for token in self.tokens:
            if all(token[key] == str(value) for key, value in kwargs.items()):
                return namedtuple("Token", token.keys())(*token.values())
        return None

    def get_tokens(self) -> List[namedtuple]:
        return [namedtuple("Token", token.keys())(*token.values()) for token in self.tokens]


class MockPairManager(PairManager):
    """
    A mock PairManager class.
    """
    pairs = load_csv_data("pairs.csv")

    def get_pair(self, **kwargs) -> Optional[namedtuple]:
        for pair in self.pairs:
            if all(pair[key] == str(value) for key, value in kwargs.items()):
                return namedtuple("Pair", pair.keys())(*pair.values())
        return None

    def get_pairs(self) -> List[namedtuple]:
        return [namedtuple("Pair", pair.keys())(*pair.values()) for pair in self.pairs]


class MockPoolManager(PoolManager):
    """
    A mock PoolManager class.
    """
    pools = load_csv_data("pools.csv")

    def get_pool(self, **kwargs) -> Optional[namedtuple]:
        for pool in self.pools:
            if all(pool[key] == str(value) for key, value in kwargs.items()):
                return namedtuple("Pool", pool.keys())(*pool.values())
        return None

    def get_pools(self) -> List[namedtuple]:
        return [namedtuple("Pool", pool.keys())(*pool.values()) for pool in self.pools]


class MockDatabaseManager(MockTokenManager, MockPairManager, MockPoolManager):
    """
    A mock DatabaseManager class.
    """
    __name__ = "MockDatabaseManager"
    __DATE__ = "04-30-2023"
    __VERSION__ = "3.0.1"

    def __post_init__(self, backend_url=None):
        self.bnt_price_map = {'UOS': 0.6256369626308176, 'GRT': 0.2833668586139438, 'EDEN': 0.13514190920020222,
                                'wNXM': 53.93005448231183, 'DIP': 0.03353407973355594, 'RARI': 3.1436321270707084,
                                'NMR': 34.79236097393122, 'MFG': 0.00431129075766619, 'INDEX': 4.52420449404313,
                                'RPL': 96.46138359009646, 'IDLE': 0.5421651882129399, 'AMP': 0.007583813060642498,
                                'stETH': 3866.8954476557046, 'RNB': 9.4610604911228, 'MONA': 810.0931878866402,
                                'LRC': 0.708679002427231, 'SATA': 0.02534009176521233, 'USDT': 2.1339825529338525,
                                'OCEAN': 0.7570115971689264, 'ACRE': 0.0024548191486639774, 'MANA': 1.1454939749787296,
                                'wstETH': 4331.696462825136, 'REN': 3.836251726313277, 'APW': 0.7410427861629725,
                                'KTN': 0.637212732488991, 'BORING': 71.54944947206438, 'YFI': 16672.423240354008,
                                'COMP': 11.150696438812954, 'AAVE': 146.43458970585098, 'XCHF': 2.3907358983937246,
                                'ICHI': 6.574958799771157, 'QNT': 234.30612214402058, 'PHTR': 0.056303266734567946,
                                'UMA': 3.9282580523952766, 'ARB': 2.7968743328066954, 'LINK': 14.985750728473993,
                                'vBNT': 0.8148613910429406, 'DAPP': 0.45590530502789484, 'BBS': 0.03851912351278174,
                                'SHIBGF': 1.3060974750289913e-09, 'TRAC': 0.7731811484336629, 'TEMP': 2.139791146133641,
                                'BAT': 0.5162199800080309, 'WBTC': 58339.58057013244, 'MPH': 4.784637894759327,
                                'WETH': 3877.129504639202, 'ETH': 3877.129504639202, 'AUC': 11.753170572972417,
                                'ANKR': 0.06512778805945298, 'OPIUM': 0.2747906167289076, 'USDC': 2.1327554987768647,
                                'ARCONA': 0.14009956660997672, 'LPL': 0.433175927842421, 'ROOK': 107.14026604756764,
                                'CHZ': 0.2676996154716128, 'HEGIC': 0.02963796241568922, 'eRSDL': 0.004955503922610322,
                                'ARMOR': 0.010331829896907216, 'REQ': 0.19061856241709776, 'MATIC': 2.030382186928921,
                                'NDX': 0.004772396826005944, 'UNI': 11.171802711080979, 'RLC': 3.155367749583193,
                                'BNT': 1.0, 'MKR': 1430.3316868725847, 'SNX': 4.988445566252526, 'ENS': 24.83330775396054,
                                'ZCN': 0.28406817363438597, 'WOO': 0.5298205695245156, 'xSUSHI': 2.940161325373592,
                                'ALPHA': 0.21392443359283453, 'SHEESHA': 16.852771545874266, 'DAI': 2.130615236455679,
                                'CROWN': 0.2788955753117568, 'ENJ': 0.8115114291681408, 'HOT': 0.003927933610948908,
                                'DARK': 0.05767934684277185, 'SCRY': 0.2460601100537108, 'TUSD': 2.05486919650752,
                                'SHIB': 2.1460287152221954e-05, 'TEDDY': 5.798198813611982e-09,
                                'eXRD': 0.21281477244200453, 'BDOG': 4.4990625237970775e-09, 'BZR': 0.07345918953355056,
                                'UwU': 36.330851582810666, 'DHDAO': 0.0, 'EBO': 1.5660554142685046e-08,
                                'FOLD': 48.14533383579105, 'IMX': 1.996678144538812, 'FIND': 0.004843987799930392,
                                'UMIIE': 0.0, 'rETH2': 3839.242865822889, 'TRU': 2.05486919650752, 'G333': 0.0,
                                'PROS': 0.9985314139414748, 'RCK': 0.0004905691475663147, 'NEWO': 0.06699341221644516,
                                '⚗️': 0.0, 'ShibDoge': 1.5400160265983853e-10, 'ULS': 0.5002585384645494, 'BUGZ': 0.0,
                                'NO': 0.815284970891067, 'PUNK': 0.06391650218191258, 'UMIIE2': 0.0,
                                'BLOCKS': 0.6763937533478924, 'OCC': 0.4131760224588481, 'MOVIE': 0.0067524873288963,
                                'AMD': 0.11729343149361827, 'HDRN': 4.721201700457276e-06, 'KOO': 1.7437160858306807e-09,
                                'SHIBAGOLD': 0.0, 'ETHM': 7.306478314562034e-11, 'M2': 13203.194741952842,
                                'WRLD': 0.07364626178532918, 'FLOKI': 7.670271150994413e-05, 'NMSBY': 0.0,
                                'RNG': 4.331173933757789, 'ILSI': 97.71832455765856, 'carbon': 2.107820591880972,
                                '$PZLR': 0.0, 'SPAY': 7.88619462237419e-05, 'UKAN': 0.0, 'DFI': 0.9634309305903266,
                                'WVRH': 0.0, 'FXM': 0.0, 'KOGI': 0.0, 'SPELL': 0.0, 'KDOE': 0.0, 'BURNLY': 0.0,
                                'BHNY': 0.0, 'AMPL': 0.0, 'Dione': 0.0, 'WDOGE': 0.0, 'FTH': 0.0,
                                'UFO': 2.78395862418827e-06, 'FOX': 0.0, 'ELONINDEX': 0.0, 'LDR': 0.0, 'ANT': 0.0,
                                'BDDN1': 0.0, 'SPU+': 0.0, 'DEE': 0.0, 'TRG': 0.0, 'TTT': 0.0, 'BEND': 0.0, 'BTT': 0.0,
                                'EDOG': 5.689076807688186e-09, 'USDD': 0.0, 'META': 0.0, 'AUDIO': 0.0, 'BAND': 0.0,
                                'VRH': 0.0, 'NMS': 0.0, 'PREMIA': 1.4970195352823972, '0x0XFIND': 0.0, 'TSUKA': 0.0,
                                'sETH2': 0.0, 'POWER': 0.0, 'sUSD': 0.0, 'SCLM': 0.0, 'NU': 0.0, 'RND': 0.0, 'STRP': 0.0,
                                'XET': 0.0, 'KOCHI': 0.0, 'CVX': 0.0, 'GOJ': 0.0, 'MIM': 0.0, 'STARL': 0.0,
                                'RektDoge': 0.0, 'DEGENS': 0.0, 'VOW': 0.0, 'TOS': 0.0, 'GODS': 0.0, 'DOGEGF': 0.0,
                                'O': 0.0, 'YGG': 0.48949314035384156, 'XUSD': 0.0, 'KAP': 0.0, 'MIA': 0.0, 'JPEG': 0.0,
                                'GALGO': 0.0, 'ICE': 0.0, 'SAN': 0.0, 'DOGE': 0.0, 'XFI': 0.0, 'BLUEDOGE': 0.0,
                                'KITTY': 0.00024234394253475153, 'WTON': 0.0, 'MRT': 0.0057454042659292335, 'CLNR': 0.0,
                                'LFT': 0.001902214565813632, 'VOLT': 2.1636591804059023e-06, 'BLUR': 1.2827478770469678,
                                'BULL': 0.0055254102481682036, 'RAI': 0.7650541031757957, 'QD': 0.14385403869225843,
                                'REYA': 0.0, 'MAC': 0.13163235064090428, 'ERN': 11.340552044077906,
                                'BONE': 2.2187050418940086, 'MDOGE': 0.0, 'PAT': 0.015378018259802914,
                                'BSD': 0.0004871573227957521, 'CAW': 2.317500108052038e-07, 'USE': 0.15029848010921965,
                                'SUPER': 0.24040318761196797, 'FEI': 2.139493316914764, 'vUSD': 1.9943248741835315,
                                'TCR': 0.020957953499482117, 'DOLE': 0.0, 'DWYN': 0.0, 'Burnt Hair': 0.0,
                                'MULTI': 79.40283140283141, 'USD': 2.061184862131236, 'testv3': 0.0,
                                'DG': 2.0632397393975834, 'DMDHRT20': 0.0, 'OGER': 0.0, 'DJ15': 0.0, 'CULT': 0.0,
                                'MLD': 0.0, 'XFIT': 0.0, 'JEJUDOGE': 0.0, 'CBBGSBF': 0.0, 'DELTA': 0.0, 'BLUE': 0.0,
                                'CHWE': 0.0, 'THOR': 0.0, 'ASTRA': 0.0, 'HARAMBE': 0.0, 'GROGU': 0.0, 'LUSD': 0.0,
                                'PNK': 0.0, 'HEZ': 0.0, 'HVC': 0.0, 'GEAG': 0.0, 'DICC': 0.0, 'SDL': 0.020043947987330456,
                                'ZKM': 0.0, 'ASTO': 0.0, 'UST': 0.0, 'SHARE': 0.0, 'OCT': 0.0, 'TRIBE': 0.0, 'NEBTC': 0.0,
                                'MVRS': 0.0, 'FAITH': 0.0, 'RADAR': 0.0, 'QUACK': 2.2738085675623906e-09, 'WISE': 0.0,
                                'ARTS': 0.0, 'ALCX': 0.0, 'GF': 0.0, 'RK:ETH': 0.0, 'UETH': 0.0, 'CRAWLZ': 0.0,
                                'WILD': 0.0, 'DXN': 0.0, 'UKR': 0.0, 'Metti': 0.0, 'MC': 0.0, 'TBT': 0.0, 'LORB': 0.0,
                                'STARS': 0.0, 'XXi': 0.0, 'FNK': 0.0, 'IGLD': 0.0, 'FAMILY': 0.0, 'MILADY': 0.0,
                                'PAXG': 0.0, 'IMS': 0.0, 'STFMG': 0.0, 'XEN': 0.0, 'MYC': 0.0, 'ASCX': 0.0, 'wPE': 0.0,
                                'FRAX': 0.0, 'CIV': 0.0, 'BADGER': 0.0, 'MASATO': 0.0, 'SWFL': 0.0, 'oneGIV': 0.0,
                                'FAKE': 0.0, 'USH': 0.0, 'xPIL': 0.0, 'DD': 0.0, 'IGNANT': 0.0, 'ROOT': 0.0, 'ADOGE': 0.0,
                                'BRO': 0.0, 'GOLD': 0.0, 'SNEK': 0.0, 'T': 0.0, 'Murakami': 0.0, 'PEPA': 0.0, 'BTC': 0.0,
                                'PKC': 0.0, 'SHIR': 0.0, 'scUSD': 0.0, 'BIT': 0.0, 'PIL': 0.0, 'CRNK': 0.0, 'GILD': 0.0,
                                'ELNX': 0.0, 'IQ': 0.0, 'LDO': 0.0, 'ZRX': 0.0, 'BOTTO': 0.0, 'e85': 0.0, 'GRAY': 0.0,
                                'IYKYK': 0.0, 'SOS': 0.0, 'MingBi': 0.0, 'LON': 0.0, 'bLUSD': 0.0, 'TOWER': 0.0,
                                'DAPE': 0.0, 'ELIRA': 0.0, 'PEPE': 0.0, 'QUARTZ': 0.0, 'KNX': 0.0, 'yvBOOST': 0.0,
                                'SHI': 0.0, 'HOPR': 0.0, 'NEXTSHIB': 0.0, 'JVT': 0.0, 'PAW': 0.0, 'SWIFT': 0.0,
                                'CAGE': 0.0, '100MD': 0.0, 'WOJAK': 0.0, 'SMUD': 0.0, 'WAXE': 0.0, 'XYO': 0.0,
                                'SAITAMA': 0.0, 'LUNA': 0.0, 'FREN': 0.0, 'DETS': 0.0, 'HVE2': 0.0, 'SPS': 0.0, 'I': 0.0,
                                'MCALF': 0.0, 'DOG': 0.0, 'POLS': 0.0, 'KEEP': 0.0, 'KISHU': 0.0, 'DBL': 0.0, 'X2Y2': 0.0,
                                'DC': 0.0, 'GAS': 0.0, 'ELON': 0.0, 'CRETH2': 0.0, 'MILAREPA': 0.0, 'AKITA': 0.0,
                                'INU': 0.0, 'ETH2POS': 0.0, 'FXS': 0.0, '0NE': 0.0, 'SUSHI': 0.0, 'SFTX': 0.0,
                                'TOWELIE': 0.0, 'ULCK': 0.0, 'RAD': 0.0, 'HANU': 0.0, 'HMB': 0.0, 'MOME': 0.0,
                                'SHIK': 0.0, 'HEX': 0.0, 'BigSB': 0.0, 'EVN': 0.0, 'TOKE': 0.0, 'VINU': 0.0,
                                'CLEANER': 0.0, 'TURTLE': 0.0, 'ID': 0.0, 'SYN': 0.0, 'PapaB': 0.0, 'USDP': 0.0,
                                'FHD': 0.0, 'WGMI': 0.0, 'BabyDoge': 0.0, 'DIM': 0.0, 'ARTSTIC': 0.0, 'GND': 0.0,
                                'FLUT': 0.0, 'COVID': 0.0, 'ILV': 0.0, 'KUMA': 0.0, 'ZERO': 0.0, 'DEXT': 0.0,
                                'DIVER': 0.0, 'QOM': 0.0, 'XLON': 0.0, 'SOV': 0.0, 'imgnAI': 0.0, 'CRV': 0.0,
                                'BITEYX': 0.0, 'CBBG': 0.0, 'DJT': 0.0, 'MASK': 0.0}

    def _get_bnt_price_from_tokens(self, price, tkn) -> Decimal:
        """
        Gets the price of a token

        Parameters
        ----------
        tkn0 : str
            The token address
        tkn1 : str
            The token address

        Returns
        -------
        Optional[Decimal]
            The price
        """

        if tkn == 'BNT-FF1C':
            return Decimal(price)

        bnt_price_map_symbols = {token.split('-')[0]: self.bnt_price_map[token] for token in self.bnt_price_map}

        tkn_bnt_price = bnt_price_map_symbols.get(tkn.split('-')[0])

        if tkn_bnt_price is None:
            raise ValueError(f"Missing TKN/BNT price for {tkn}")

        return Decimal(price) * Decimal(tkn_bnt_price)
    