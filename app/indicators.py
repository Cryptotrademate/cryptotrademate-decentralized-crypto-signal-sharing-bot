import ta

def calculate_indicators(data):
    """Calculate technical indicators."""
    # Trend Indicators
    data["SMA50"] = ta.trend.sma_indicator(data["close"], window=50)
    data["EMA200"] = ta.trend.ema_indicator(data["close"], window=200)
    macd = ta.trend.MACD(data["close"])
    data["MACD"] = macd.macd()
    data["MACD_Signal"] = macd.macd_signal()

    # Momentum Indicators
    data["RSI"] = ta.momentum.rsi(data["close"], window=14)
    data["StochRSI"] = ta.momentum.stochrsi(data["close"], window=14)

    # Volatility Indicators
    data["ATR"] = ta.volatility.average_true_range(data["high"], data["low"], data["close"], window=14)
    bb = ta.volatility.BollingerBands(data["close"], window=20, window_dev=2)
    data["BB_High"] = bb.bollinger_hband()
    data["BB_Low"] = bb.bollinger_lband()

    # Volume Indicators
    data["OBV"] = ta.volume.on_balance_volume(data["close"], data["volume"])

    return data
