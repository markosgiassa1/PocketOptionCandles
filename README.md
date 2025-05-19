# PocketOptionCandles
# Pocket Option Candle Aggregator and Trading Bot

This Python script connects to Pocket Option's trading platform using the `BinaryOptionsToolsV2` library to:

- Fetch and aggregate candle (OHLC) data for a selected asset at a user-defined timeframe.
- Display candle data from recent candles with time offsets.
- Show the current account balance.
- Allow the user to place buy or sell trades on the selected asset.
- Provide an interactive CLI for asset selection, timeframe input, and trade management.
- Continuously update candle data and balance while offering options to repeat queries or exit.

The script handles aggregation of smaller timeframe candles into larger intervals if necessary, and synchronizes with the current candle timing for accurate trading decisions.

---

### Usage

1. Run the script.
2. Select an asset from the displayed list by entering its number.
3. Enter the candle timeframe in seconds (e.g., 5, 15, 60).
4. View candle data for recent candles.
5. Choose to buy, sell, repeat the candle fetch, or exit.
6. If buying or selling, input trade amount and duration.
7. The bot will place the trade and update candle data after a short delay.

---

### Notes

- The script uses a demo session ID by default.
- Ensure you have a valid session ID if switching to a real account.
- Candle data aggregation supports custom timeframes by grouping smaller candles.
- The user is responsible for entering valid inputs; invalid inputs will prompt retry messages.

---

### Requirements

See `requirements.txt` for the necessary Python packages.

---

### Disclaimer

This script is for educational and experimental purposes only. Trading carries risk and should be done responsibly.
