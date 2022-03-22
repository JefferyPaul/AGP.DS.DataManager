功能
    数据检查
        Bar数据检查,
            根据mostAct检查最活跃合约;
            分钟数据是否有缺失,OHLCV检查;
        计算MostAct,
        盘中Tick数据接收监控,
    数据获取
        指定交易所获取品种
        指定品种获取合约
        指定品种/合约获取单日/日期区间的bar/tick数据

细节
    日内数据确实检查,需要用到 TradingSession 信息
