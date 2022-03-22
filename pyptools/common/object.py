import os
from datetime import datetime, date, time
from typing import List, Dict
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from functools import wraps

from .constant import *

"""
Ticker, Product  没有重复实例

对于Ticker和Product，不使用 枚举类Exchange，而是用简单的 string表示，降低复杂度，
因为交易所/合约/品种可能随时增减，不能使用枚举类来使之被限制，
而且此处的exchange没有实质的作用，仅需要用string表示。
对于Ticker和Product，它们的Exchange的定义是： s.split(".")[-1]，没有其他更多的含义


ProductInfo, TradingSession
使用不可修改的单例模式（目前不觉得存在一个域内需要多套参数的情况,使用单例可以做到完全统一）,

ProductInfoFile, TradingSessionFile 功能实现

"""


class Singleton:
    def __new__(cls, *args, **kwargs):
        if not getattr(cls, '_singleton', None):
            cls._singleton = super().__new__(cls, *args, **kwargs)
        return cls._singleton


class UnsetDict(dict):
    def __setitem__(self, key, value):
        print(f'{self.__class__.__name__} 不能直接修改键值，请使用 .set()')

    def set(self, key, value):
        super(UnsetDict, self).__setitem__(key, value)


class Ticker:
    """
    标的
    """
    _instances = {}
    count = 0

    def __new__(cls, symbol: str, exchange: str):
        if (symbol, exchange) in cls._instances.keys():
            pass
        else:
            _instance = super().__new__(cls)
            cls._instances[(symbol, exchange)] = _instance
            cls.count += 1
        return cls._instances[(symbol, exchange)]

    def __init__(self, symbol: str, exchange):
        self.symbol = symbol
        self.exchange = exchange
        self.product_name = self._product_name()
        self.product = Product(symbol=self.product_name, exchange=self.exchange)
        self.name = f'{self.symbol}.{self.exchange.value}'

    def __repr__(self):
        return f'Ticker: {self.name}'

    @classmethod
    def from_name(cls, name: str):
        if '.' in name:
            exchange = name.split('.')[-1]
            symbol = '.'.join(name.split('.')[:-1])
        else:
            exchange = ''
            symbol = name
        return cls(symbol=symbol, exchange=exchange)

    def _product_name(self) -> str:
        # if self.exchange.value in ['DCE', 'CZCE', 'SHFE', 'INE']:
        product_name = ''
        for s in self.symbol:
            if str(s).isdigit():
                break
            else:
                product_name += s
        return product_name

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def __gt__(self, other):
        return bool(1 - self.__lt__(other))


class Product:
    """
    品种
    eg:
        symbol=AP
        exchange=CZCE
        name=AP.CZCE
        InternalProduct=ZZAP

        symbol=ES
        exchange=CME
        name=ES.CME
        InternalProduct=ES

    """
    _instances = {}
    count = 0

    def __new__(cls, symbol: str, exchange: str):
        if (symbol, exchange) in cls._instances.keys():
            pass
        else:
            _instance = super().__new__(cls)
            cls._instances[(symbol, exchange)] = _instance
            cls.count += 1
        return cls._instances[(symbol, exchange)]

    def __init__(self, symbol: str, exchange: str):
        self.symbol = symbol
        self.exchange = exchange
        self.InternalProduct = self._internal_product()
        self.name = f'{self.symbol}.{self.exchange}'

    @classmethod
    def from_name(cls, name):
        if '.' in name:
            exchange = name.split('.')[-1]
            symbol = '.'.join(name.split('.')[:-1])
        else:
            exchange = ''
            symbol = name
        return cls(symbol=symbol, exchange=exchange)

    def _internal_product(self, ):
        # 特殊例子
        if self.exchange == 'CZCE':
            if self.symbol == 'ZC':
                return 'ZZTC'
        elif self.exchange == 'SHFE':
            if self.symbol == 'au':
                return 'SQau2'
        elif self.exchange == 'CFFEX':
            if self.symbol == 'IF':
                return 'CSI300'
            elif self.symbol == 'IC':
                return 'CSI500'
            elif self.symbol == 'IH':
                return 'SSE50'
        elif self.exchange == 'LME':
            if self.symbol == 'AH3M':
                return 'LmeAH'
            elif self.symbol == 'CA3M':
                return 'LmeCA'
            elif self.symbol == 'L-ZS3M':
                return 'LmeZS'
            elif self.symbol == 'NI3M':
                return 'LmeNI'
            elif self.symbol == 'PB3M':
                return 'LmePB'
            elif self.symbol == 'SN3M':
                return 'LmeSN'

        # 一般情况
        if self.exchange == 'DCE':
            return f'DL{self.symbol}'
        elif self.exchange == 'CZCE':
            return f'ZZ{self.symbol}'
        elif self.exchange in ['SHFE', 'INE']:
            return f'SQ{self.symbol}'
        elif self.exchange == 'LME':
            return f'Lme{self.symbol}'
        elif self.exchange in ['CFFEX', 'CME', 'CME_CBT', 'NYBOT', 'SGXQ']:
            # TT TF
            return self.symbol
        else:
            return self.symbol

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def __gt__(self, other):
        return bool(1 - self.__lt__(other))

    def __repr__(self):
        return f'Product: {self.name}'



"""
    dataclass
"""


@dataclass(order=True)
class TradeData:
    datetime: datetime
    ticker: Ticker
    direction: Direction
    offset_flag: OffsetFlag
    price: float = 0
    volume: float = 0
    commission: float = 0

    def __str__(self):
        return ','.join([
            self.datetime.strftime("%Y%m%d %H%M%S.%f"),
            self.ticker.name,
            self.direction.name,
            self.offset_flag.name,
            str(self.price),
            str(self.volume),
            str(self.commission)
        ])


@dataclass(order=True)
class PositionData:
    datetime: datetime
    ticker: Ticker
    direction: Direction
    volume: float = 0
    volume_today: float = None
    price: float = 0

    def __str__(self):
        return ','.join([
            self.datetime.strftime('%Y%m%d %H%M%S'),
            self.ticker.name,
            self.direction.name,
            str(self.volume),
            str(self.volume_today) if self.volume_today else '',
            str(self.price),
        ])


@dataclass(order=True)
class AccountData:
    account: str
    balance: float = 0
    available: float = 0
    risk_ration: float = 0

    def __str__(self):
        return ','.join([
            self.account,
            str(self.balance),
            str(self.available),
            str(self.risk_ration),
        ])


@dataclass
class TickData:
    """
    Tick data contains information about:
        * last trade in market
        * orderbook snapshot
        * intraday market statistics.
    """

    ticker: Ticker
    datetime: datetime

    name: str = ""
    volume: float = 0
    open_interest: float = 0
    last_price: float = 0
    last_volume: float = 0
    limit_up: float = 0
    limit_down: float = 0

    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    pre_close: float = 0

    bid_price_1: float = 0
    bid_price_2: float = 0
    bid_price_3: float = 0
    bid_price_4: float = 0
    bid_price_5: float = 0

    ask_price_1: float = 0
    ask_price_2: float = 0
    ask_price_3: float = 0
    ask_price_4: float = 0
    ask_price_5: float = 0

    bid_volume_1: float = 0
    bid_volume_2: float = 0
    bid_volume_3: float = 0
    bid_volume_4: float = 0
    bid_volume_5: float = 0

    ask_volume_1: float = 0
    ask_volume_2: float = 0
    ask_volume_3: float = 0
    ask_volume_4: float = 0
    ask_volume_5: float = 0

    localtime: datetime = None

    def __post_init__(self):
        """"""
        self.vt_symbol = self.ticker.name


@dataclass
class BarData:
    """
    Candlestick bar data of a certain trading period.
    """

    ticker: Ticker
    datetime: datetime

    interval: Interval = None
    volume: float = 0
    open_interest: float = 0
    open_price: float = 0
    high_price: float = 0
    low_price: float = 0
    close_price: float = 0

    def __post_init__(self):
        """"""
        self.vt_symbol = self.ticker.name


# @dataclass
# class LogData:
#     """
#     Log data is used for recording log messages on GUI or in log files.
#     """
#
#     msg: str
#     # level: int = INFO
#
#     def __post_init__(self):
#         """"""
#         self.time = datetime.now()



"""
GeneralTickerInfo.csv
TradingSession.csv
"""


@dataclass
class ProductInfoData:
    product: Product
    prefix: str  # Futures / Stock / Options / ...
    currency: str

    point_value: float  # 1张合约 的 “价值 / 报价”乘数，   value / share = price * point_value
    min_move: float  # 价格最小变动幅度；1个tick 对应的 价格变动数值
    lot_size: float  # 最少交易多少手 （的倍数），1手 是多少 张(shares)
    commission_on_rate: float  # 手续费，交易价值的比率
    commission_per_share: float  # 手续费，每张多少钱
    slippage_points: float
    flat_today_discount: float  # 平今佣金倍率。1：相同；0：不收钱；2：收2倍
    margin: float  # 保证金率


class ProductInfoTable(Singleton, UnsetDict):
    """
    继承 字典dict，不可直接需改的字典，
    需要通过 get 和 set，获取或赋值

    嵌套的，不可修改的字典

    { product_name: product_info_data, }

    不区分timezone，因为其实不需要
    """

    def __delitem__(self, key):
        pass

    def get(self, product: Product) -> ProductInfoData or None:
        try:
            return super(ProductInfoTable, self).get(product)
        except:
            return None

    def set(self, product: Product, info: ProductInfoData):
        super(ProductInfoTable, self).set(product, info)


class GeneralTickerInfoFile:
    FileName = 'GeneralTickerInfo.csv'
    Header = 'Adapter,InternalProduct,Exchange,Prefix,TradingExchangeZoneIndex,Currency,' \
             'PointValue,MinMove,LotSize,ExchangeRateXxxUsd,CommissionOnRate,CommissionPerShareInXxx,' \
             'MinCommissionInXxx,MaxCommissionInXxx,StampDutyRate,' \
             'SlippagePoints,Product,FlatTodayDiscount,Margin,IsLive'

    def __init__(self):
        pass

    @classmethod
    def read(cls, p,) -> ProductInfoTable:
        assert os.path.isfile(p)
        product_info_obj: ProductInfoTable = ProductInfoTable()

        with open(p) as f:
            l_lines = f.readlines()
        l_lines = [_.strip() for _ in l_lines if _.strip()]
        if len(l_lines) <= 1:
            return product_info_obj

        for line in l_lines[1:]:
            _line_split = line.split(',')
            assert len(_line_split) == 20
            _product_symbol = _line_split[16]
            _exchange = _line_split[2]
            _product = Product(symbol=_product_symbol, exchange=_exchange)
            _product_info_data = ProductInfoData(
                product=_product,
                prefix=_line_split[3],
                currency=_line_split[5],
                point_value=float(_line_split[6]),
                min_move=float(_line_split[7]),
                lot_size=float(_line_split[8]),
                commission_on_rate=float(_line_split[10]),
                commission_per_share=float(_line_split[11]),
                slippage_points=float(_line_split[15]),
                flat_today_discount=float(_line_split[17]),
                margin=float(_line_split[18]),
            )
            product_info_obj.set(_product, _product_info_data)
        return product_info_obj


@dataclass
class TradingSessionData:
    Date: date
    Product: Product
    TradingSession: List[List[time]]
    ExchangeTimezone: str


class TradingSessionTable(Singleton, UnsetDict):

    def __delitem__(self, key):
        pass
    
    def get_timezone(self, timezone: str) -> List[TradingSessionData]:
        l_data = []
        try:
            for _key in self.keys():
                _tz, _product, _sd = _key
                if _tz == timezone:
                    l_data.append(_sd)
            return l_data
        except:
            return l_data

    def get_timezone_product(self, timezone: str, product: Product) -> List[TradingSessionData]:
        l_data = []
        try:
            for _key in self.keys():
                _tz, _product, _sd = _key
                if (_tz == timezone) and (_product == product):
                    l_data.append(_sd)
            return l_data
        except:
            return l_data

    def get(self, timezone: str, product: Product, using_date: date) -> TradingSessionData or None:
        try:
            l_candidate_date = []
            for _key in self.keys():
                _tz, _product, _sd = _key
                if (_tz == timezone) and (_product == product):
                    l_candidate_date.append(_sd)
            if len(l_candidate_date) == 0:
                return None
            elif len(l_candidate_date) == 1:
                return super(TradingSessionTable, self).get((timezone, product, l_candidate_date[0]))
            else:
                _max_date = max([_ for _ in l_candidate_date if _ <= using_date])
                if _max_date:
                    return super(TradingSessionTable, self).get((timezone, product, _max_date))
                else:
                    return super(TradingSessionTable, self).get((timezone, product, min(l_candidate_date)))
        except:
            return None

    def set(self, timezone: str, product: Product, start_date: date, info):
        super(TradingSessionTable, self).set((timezone, product, start_date), info)


def _gen_trading_session(s) -> List[List[time]]:
    _l = []
    for _pair in s.split('&'):
        _s = datetime.strptime(_pair.split('-')[0], '%H%M%S').time()
        _e = datetime.strptime(_pair.split('-')[1], '%H%M%S').time()
        _l.append([_s, _e])
    return _l


class TradingSessionFile:
    FileName = 'TradingSession.csv'
    Header = 'Date,ProductInfo,DaySession,NightSession,ExchangeTimezone'

    def __init__(self):
        pass

    @classmethod
    def read(cls, p, timezone: str = '210') -> TradingSessionTable:
        assert os.path.isfile(p)
        trading_session_obj: TradingSessionTable = TradingSessionTable()

        with open(p) as f:
            l_lines = f.readlines()
        l_lines = [_.strip() for _ in l_lines if _.strip()]
        if len(l_lines) <= 1:
            return trading_session_obj

        for line in l_lines[1:]:
            _line_split = line.split(',')
            assert len(_line_split) == 5
            _start_date = datetime.strptime(_line_split[0], '%Y%m%d').date()
            _product = Product.from_name(_line_split[1])
            _trading_session_data = TradingSessionData(
                Date=_start_date,
                Product=_product,
                TradingSession=_gen_trading_session(_line_split[2]),
                ExchangeTimezone=timezone
            )
            trading_session_obj.set(
                timezone=timezone, product=_product, start_date=_start_date, info=_trading_session_data)
        return trading_session_obj



# class TradeSeriesFile:
#     def __init__(self):
#         pass
#
#     @classmethod
#     def to_csv(cls, root, data: List[TradeData]):
#         output_lines = []
#         for n, trade_data in enumerate(sorted(data)):
#             output_lines.append(str(trade_data))
#
#         root = os.path.abspath(root)
#         if not os.path.isdir(root):
#             os.makedirs(root)
#         path = os.path.join(root, 'TradeSeries.csv')
#         with open(path, 'w+') as f:
#             f.write('datetime,ticker,direction,offset_flag,price,volume,commission\n')
#             f.write('\n'.join(output_lines))
#
#
# class PositionSeriesFile:
#     def __init__(self):
#         pass
#
#     @classmethod
#     def to_csv(cls, root, data: List[PositionData], date: str or None = None):
#         output_lines = []
#         for n, trade_data in enumerate(sorted(data)):
#             output_lines.append(str(trade_data))
#
#         root = os.path.abspath(root)
#         if date:
#             root = os.path.join(root, str(date))
#         if not os.path.isdir(root):
#             os.makedirs(root)
#         path = os.path.join(root, 'PositionSeries.csv')
#         with open(path, 'w+') as f:
#             f.write('datetime,ticker,direction,volume,volume_today,price\n')
#             f.write('\n'.join(output_lines))
#
