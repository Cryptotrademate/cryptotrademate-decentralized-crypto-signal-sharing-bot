from app.indicators import calculate_indicators
from app.binance_api import fetch_binance_ohlcv, fetch_binance_ohlcv_full

def generate_signal(data):
    """Generate trading signals based on indicator conditions."""
    current_price = data["close"].iloc[-1]
    indicators = calculate_indicators(data)
    atr = indicators["ATR"].iloc[-1]

    signal = "Hold"
    buy_zones = []
    tp_levels = []
    sl = None
    summary = "Market is Neutral"

    if (
        indicators["SMA50"].iloc[-1] > indicators["EMA200"].iloc[-1] and
        indicators["RSI"].iloc[-1] < 30 and
        indicators["StochRSI"].iloc[-1] < 0.2 and
        indicators["MACD"].iloc[-1] > indicators["MACD_Signal"].iloc[-1]
    ):
        signal = "Buy"
        sl = current_price - (1 * atr)
        tp1 = current_price + (2 * atr)
        tp2 = current_price + (4 * atr)
        buy_zones = [current_price, current_price - (0.5 * atr), current_price - (1 * atr)]
        tp_levels = [tp1, tp2]
        summary = "Bullish conditions detected. Upward momentum expected."

    elif (
        indicators["SMA50"].iloc[-1] < indicators["EMA200"].iloc[-1] and
        indicators["RSI"].iloc[-1] > 70 and
        indicators["StochRSI"].iloc[-1] > 0.8 and
        indicators["MACD"].iloc[-1] < indicators["MACD_Signal"].iloc[-1]
    ):
        signal = "Sell"
        buy_zones = []
        tp_levels = []
        sl = None
        summary = "Bearish conditions detected. Downward momentum expected."

    return {
        "current_price": current_price,
        "signal": signal,
        "buy_zones": buy_zones,
        "take_profit_levels": tp_levels,
        "stop_loss": sl,
        "summary": summary,
    }


def backtest_signals(pair):
    """Backtest trading signals on historical data."""
    try:
        data = fetch_binance_ohlcv_full(pair)
        data_with_indicators = calculate_indicators(data)
        initial_balance = 1000  # USD
        balance = initial_balance
        position = None
        trade_history = []

        for i in range(len(data_with_indicators)):
            row = data_with_indicators.iloc[i]
            signal_data = generate_signal(data_with_indicators.iloc[:i+1])

            if signal_data["signal"] == "Buy" and not position:
                position = {"entry_price": row["close"], "stop_loss": signal_data["stop_loss"]}
                trade_history.append({"action": "Buy", "price": row["close"], "timestamp": row.name})
            elif signal_data["signal"] == "Sell" and position:
                pnl = (row["close"] - position["entry_price"]) / position["entry_price"] * balance
                balance += pnl
                trade_history.append({"action": "Sell", "price": row["close"], "timestamp": row.name, "pnl": pnl})
                position = None

        total_return = (balance - initial_balance) / initial_balance * 100
        win_trades = sum(1 for t in trade_history if t.get("pnl", 0) > 0)
        loss_trades = len(trade_history) - win_trades
        win_rate = win_trades / len(trade_history) * 100 if trade_history else 0

        return {
            "pair": pair,
            "initial_balance": initial_balance,
            "final_balance": balance,
            "total_return": total_return,
            "win_rate": win_rate,
            "trades": trade_history
        }

    except Exception as e:
        return {"error": str(e)}
