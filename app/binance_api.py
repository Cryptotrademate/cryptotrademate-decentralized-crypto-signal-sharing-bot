import requests
import pandas as pd
import time

BINANCE_API_BASE = "https://api.binance.com/api/v3"


def fetch_binance_ohlcv(pair, interval="1h", limit=100):
    """Fetch historical OHLCV data from Binance."""
    url = f"{BINANCE_API_BASE}/klines"
    params = {"symbol": pair, "interval": interval, "limit": limit}
    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df
    else:
        raise Exception(f"Error fetching data: {response.json()}")


def fetch_market_data(pair):
    """Fetch market data for a specific pair."""
    url = f"{BINANCE_API_BASE}/ticker/24hr"
    params = {"symbol": pair}
    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        price = float(data["lastPrice"])
        volume = float(data["quoteVolume"])
        percent_change = float(data["priceChangePercent"])
        return {
            "price": f"${price:,.8f}".rstrip('0').rstrip('.'),
            "volume": f"${volume:,.2f}",
            "percent_change": f"{percent_change:.2f}%"
        }
    else:
        raise Exception(f"Error fetching market data: {response.json()}")


def fetch_binance_ohlcv_full(pair, interval="1d", lookback_days=365):
    """Fetch historical OHLCV data from Binance for up to 1 year."""
    end_time = int(pd.Timestamp.now().timestamp() * 1000)
    start_time = int((pd.Timestamp.now() - pd.Timedelta(days=lookback_days)).timestamp() * 1000)
    url = f"{BINANCE_API_BASE}/klines"
    params = {
        "symbol": pair,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time
    }

    response = requests.get(url, params=params)
    data = response.json()

    if response.status_code == 200:
        df = pd.DataFrame(data, columns=[
            "timestamp", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "trades",
            "taker_buy_base", "taker_buy_quote", "ignore"
        ])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        df = df[["open", "high", "low", "close", "volume"]].astype(float)
        return df
    else:
        raise Exception(f"Error fetching data: {response.json()}")