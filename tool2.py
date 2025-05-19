# -*- coding: utf-8 -*-

import asyncio
from datetime import datetime, timedelta
from collections import defaultdict
from BinaryOptionsToolsV2.pocketoption import PocketOptionAsync
from tabulate import tabulate

demo_ssid = '42["auth",{"session":"tokenorssidhere","isDemo":1,"uid":68498820,"platform":2}]'
api = PocketOptionAsync(demo_ssid)

# Full asset list from your original dictionary keys
ACTIVES = [
    '#AAPL', '#AAPL_otc', '#AXP', '#AXP_otc', '#BA', '#BA_otc', '#CSCO',
    '#CSCO_otc', '#FB', '#FB_otc', '#INTC', '#INTC_otc', '#JNJ',
    '#JNJ_otc', '#JPM', '#MCD', '#MCD_otc', '#MSFT', '#MSFT_otc', '#PFE',
    '#PFE_otc', '#TSLA', '#TSLA_otc', '#XOM', '#XOM_otc', '100GBP',
    '100GBP_otc', 'AEX25', 'AMZN_otc', 'AUDCAD', 'AUDCAD_otc', 'AUDCHF',
    'AUDCHF_otc', 'AUDJPY', 'AUDJPY_otc', 'AUDNZD_otc', 'AUDUSD', 'AUDUSD_otc',
    'AUS200', 'AUS200_otc', 'BABA', 'BABA_otc', 'BCHEUR', 'BCHGBP',
    'BCHJPY', 'BTCGBP', 'BTCJPY', 'BTCUSD', 'CAC40', 'CADCHF',
    'CADCHF_otc', 'CADJPY', 'CADJPY_otc', 'CHFJPY', 'CHFJPY_otc', 'CHFNOK_otc',
    'CITI', 'CITI_otc', 'D30EUR', 'D30EUR_otc', 'DASH_USD', 'DJI30',
    'DJI30_otc', 'DOTUSD', 'E35EUR', 'E35EUR_otc', 'E50EUR', 'E50EUR_otc',
    'ETHUSD', 'EURAUD', 'EURCAD', 'EURCHF', 'EURCHF_otc', 'EURGBP',
    'EURGBP_otc', 'EURHUF_otc', 'EURJPY', 'EURJPY_otc', 'EURNZD_otc',
    'EURRUB_otc', 'EURUSD', 'EURUSD_otc', 'F40EUR', 'F40EUR_otc', 'FDX_otc',
    'GBPAUD', 'GBPAUD_otc', 'GBPCAD', 'GBPCHF', 'GBPJPY', 'GBPJPY_otc',
    'GBPUSD', 'H33HKD', 'JPN225', 'JPN225_otc', 'LNKUSD', 'NASUSD',
    'NASUSD_otc', 'NFLX', 'NFLX_otc', 'NZDJPY_otc', 'NZDUSD_otc', 'SMI20',
    'SP500', 'SP500_otc', 'TWITTER', 'TWITTER_otc', 'UKBrent',
    'UKBrent_otc', 'USCrude', 'USCrude_otc', 'USDCAD', 'USDCAD_otc',
    'USDCHF', 'USDCHF_otc', 'USDJPY', 'USDJPY_otc', 'USDRUB_otc',
    'VISA_otc', 'XAGEUR', 'XAGUSD', 'XAGUSD_otc', 'XAUEUR', 'XAUUSD',
    'XAUUSD_otc', 'XNGUSD', 'XNGUSD_otc', 'XPDUSD', 'XPDUSD_otc',
    'XPTUSD', 'XPTUSD_otc', 'Microsoft_otc', 'Facebook_OTC', 'Tesla_otc',
    'Boeing_OTC', 'American_Express_otc'
]

def parse_time(t):
    try:
        return datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%fZ')
    except ValueError:
        return datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')

def floor_time(dt, delta):
    """Floor datetime dt to nearest lower multiple of timedelta delta."""
    seconds = (dt - datetime(1970,1,1)).total_seconds()
    floored = seconds - (seconds % delta.total_seconds())
    return datetime.utcfromtimestamp(floored)

async def get_aggregated_candles(asset, base_interval_seconds):
    # Adjust period to 1s (or the smallest unit PocketOption supports)
    if base_interval_seconds >= 86400:
        raw_period = 3600  # use hourly candles for daily aggregation
    elif base_interval_seconds >= 3600:
        raw_period = 60
    else:
        raw_period = 1

    candles = await api.history(asset, raw_period)

    grouped = defaultdict(list)
    for c in candles:
        dt = parse_time(c['time'])
        bucket = floor_time(dt, timedelta(seconds=base_interval_seconds))
        grouped[bucket].append(c)

    sorted_buckets = sorted(grouped.keys(), reverse=True)

    aggregated_candles = []
    for bucket in sorted_buckets:
        bucket_candles = grouped[bucket]
        if not bucket_candles:
            continue
        open_price = bucket_candles[0]['open']
        close_price = bucket_candles[-1]['close']
        high_price = max(c['high'] for c in bucket_candles)
        low_price = min(c['low'] for c in bucket_candles)
        aggregated_candles.append({
            'time': bucket.isoformat() + 'Z',
            'open': open_price,
            'close': close_price,
            'high': high_price,
            'low': low_price
        })

    return aggregated_candles

async def print_candle_offsets(asset, timeframe, offsets):
    aggregated_candles = await get_aggregated_candles(asset, timeframe)

    rows = []
    headers = ['Offset (# candles ago)', 'Time (UTC start)', 'High', 'Open', 'Close', 'Low']

    latest_idx = 0  # sorted descending: index 0 = latest candle

    for offset in offsets:
        idx = offset  # offset counts from latest candle in descending list
        if idx < len(aggregated_candles):
            c = aggregated_candles[idx]
            rows.append([
                f"{offset}",
                c['time'],
                c['high'],
                c['open'],
                c['close'],
                c['low']
            ])
        else:
            rows.append([f"{offset}", "N/A", "N/A", "N/A", "N/A", "N/A"])

    print(f"\nAggregated candles for asset {asset} with timeframe {timeframe}s:\n")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

async def get_balance():
    balance = await api.balance()
    print(f"\nCurrent balance: {balance}\n")


async def place_trade(action, asset, amount, duration):
    if action not in ['buy', 'sell']:
        print("Invalid action. Please choose 'buy' or 'sell'.")
        return

    try:
        if action == 'buy':
            await api.buy(asset, amount, duration)
        elif action == 'sell':
            await api.sell(asset, amount, duration)

        print(f"\nTrade placed: {action} {amount} on {asset} for {duration} seconds\n")
    except Exception as e:
        print(f"Error placing trade: {e}")


import time  # add this import at the top of your script

async def main():
    print("Available Assets:")
    for idx, asset in enumerate(ACTIVES, 1):
        print(f"{idx}. {asset}")

    try:
        asset_choice = int(input("Select an asset by number: ")) - 1
        if asset_choice < 0 or asset_choice >= len(ACTIVES):
            print("Invalid number, please select a valid asset number.")
            return
        asset = ACTIVES[asset_choice]
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    try:
        timeframe = int(input("Enter candle timeframe in seconds (e.g., 5, 15, 60): "))
        if timeframe <= 0:
            print("Timeframe must be positive integer.")
            return
    except ValueError:
        print("Invalid input for timeframe.")
        return

    offsets = [9, 8, 7, 6, 5, 4, 3, 2, 1]

    while True:
        # Calculate seconds left until the current candle closes
        #now = datetime.utcnow()
        #seconds_passed = (now - floor_time(now, timedelta(seconds=timeframe))).total_seconds()
        #seconds_left = timeframe - seconds_passed

        #print(f"Time until current {timeframe}s candle closes: {int(seconds_left)} seconds", end='\r')

        #try:
            #while seconds_left > 0:
                #print(f"Time until current {timeframe}s candle closes: {int(seconds_left)} seconds", end='\r')
                #await asyncio.sleep(1)
                #seconds_left -= 1
        #except KeyboardInterrupt:
            #print("\nTimer interrupted by user. Proceeding to fetch candle data...\n")

        # Candle closed now, fetch and print new candle data
        #print("\nCandle closed. Fetching new candle data...\n")
        await print_candle_offsets(asset, timeframe, offsets)
        await get_balance()

        action = input("Do you want to buy, sell, repeat, or exit? (Type 'buy', 'sell', 'repeat', or 'exit'): ").lower()
          # Calculate seconds left in current candle
        now = datetime.utcnow()
        current_candle_start = floor_time(now,               timedelta(seconds=timeframe))
        seconds_passed = (now - current_candle_start).total_seconds()
        seconds_left = int(timeframe - seconds_passed)

        print(f"\nTime until current candle closes: {seconds_left} seconds\n")

        if action == 'exit':
            print("Exiting...")
            break
        elif action == 'repeat':
            print("\nRepeating candle fetch and balance update...\n")
            # Just repeat candle + balance fetch, then continue loop
            continue
        elif action not in ['buy', 'sell']:
            print("Invalid action. Please enter 'buy', 'sell', 'repeat', or 'exit'.")
            continue

        try:
            amount = float(input("Enter the trade amount: "))
            time_duration = int(input("Enter the trade duration in seconds: "))
        except ValueError:
            print("Invalid input for amount or duration.")
            continue

        await place_trade(action, asset, amount, time_duration)

        print("\nWaiting a few seconds before updating candles...\n")
        await asyncio.sleep(5)  # optional delay to let new candle data arrive

if __name__ == '__main__':
    asyncio.run(main())