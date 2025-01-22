import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.binance_api import fetch_market_data, fetch_binance_ohlcv
from app.signals import generate_signal

# Load environment variables from .env file
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("❌ Bot token is missing. Please set it in the .env file.")

bot = telebot.TeleBot(BOT_TOKEN)


PAIRS_TO_MONITOR = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT"
]

@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    """Send a welcome message with an inline menu."""
    welcome_text = (
        "👋 **Welcome to CryptoTradeMate Decentralized Crypto Signal Sharing Platform!**\n\n"
        "📚 Use the menu below to explore features or type commands manually.\n\n"
        "🌟 **Features**:\n"
        "1️⃣ Get market data for any pair.\n"
        "2️⃣ Receive trading signals.\n"
        "3️⃣ View top 3 signals.\n\n"
        "🚀 Happy Trading!"
    )
    # Create inline keyboard menu
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📊 Market Data", callback_data="market"),
        InlineKeyboardButton("📈 Signal for a Pair", callback_data="signal"),
        InlineKeyboardButton("🌟 Top 3 Signals", callback_data="top3"),
        InlineKeyboardButton("ℹ️ Help", callback_data="help")
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle inline menu button clicks."""
    if call.data == "market":
        bot.send_message(
            call.message.chat.id, 
            "📊 Enter a pair to get market data (e.g., `/market BTCUSDT`)."
        )
    elif call.data == "signal":
        bot.send_message(
            call.message.chat.id, 
            "📈 Enter a pair to get trading signals (e.g., `/signal ETHUSDT`)."
        )
    elif call.data == "top3":
        send_top10_signals(call.message)
    elif call.data == "help":
        send_welcome(call.message)

@bot.message_handler(commands=["market"])
def send_market_data(message):
    """Send market data for a specific pair."""
    try:
        pair = message.text.split(" ")[1].upper()
        data = fetch_market_data(pair)
        response = (
            f"📊 **Market Data for {pair}**\n\n"
            f"💰 **Price**: {data['price']}\n"
            f"📈 **24h Volume**: {data['volume']}\n"
            f"📉 **24h Change**: {data['percent_change']}%\n"
        )
        bot.reply_to(message, response, parse_mode="Markdown")
    except IndexError:
        bot.reply_to(message, "❗ Please provide a valid pair. Example: `/market BTCUSDT`")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=["signal"])
def send_signal(message):
    """Send trading signal for a specific pair."""
    try:
        pair = message.text.split(" ")[1].upper()
        data = fetch_binance_ohlcv(pair)
        signal_data = generate_signal(data)
        response = (
            f"📈 **Signal for {pair}**\n\n"
            f"💵 **Current Price**: {signal_data['current_price']:.2f}\n"
            f"📊 **Signal**: {signal_data['signal']}\n"
            f"📜 **Summary**: {signal_data['summary']}\n"
        )
        if signal_data["signal"] == "Buy":
            response += (
                f"🛒 **Buy Zones**: {', '.join([f'{zone:.2f}' for zone in signal_data['buy_zones']])}\n"
                f"🎯 **Take Profit Levels**: {', '.join([f'{tp:.2f}' for tp in signal_data['take_profit_levels']])}\n"
                f"❌ **Stop Loss**: {signal_data['stop_loss']:.2f}\n"
            )
        bot.reply_to(message, response, parse_mode="Markdown")
    except IndexError:
        bot.reply_to(message, "❗ Please provide a valid pair. Example: `/signal BTCUSDT`")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=["top3"])
def send_top10_signals(message):
    """Send trading signals for top 3 pairs."""
    response = "🌟 **Top 3 Pair Signals**\n\n"
    for pair in PAIRS_TO_MONITOR:
        try:
            data = fetch_binance_ohlcv(pair)
            signal_data = generate_signal(data)
            response += (
                f"🔹 {pair}\n"
                f"💵 **Price**: {signal_data['current_price']:.2f}\n"
                f"📊 **Signal**: {signal_data['signal']}\n"
                f"📜 **Summary**: {signal_data['summary']}\n\n"
            )
        except Exception as e:
            response += f"❌ {pair}: Error - {e}\n"
    bot.reply_to(message, response, parse_mode="Markdown")

if __name__ == "__main__":
    bot.polling()
