"""Crypto API."""

from typing import Dict, List
from sqlite3 import Error

import requests
import sqlite3
import pandas as pd
import logging
import sys


# API Documentation - https://www.coingecko.com/en/api#explore-api

def get_coins() -> List[Dict]:
    """This function will get the top 10 coins at the current time, sorted by market cap in desc order."""
    response = requests.get(
        'https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false')
    # Important keys
    # - id
    # - symbol
    # - name
    # - current_price
    return response.json()


def get_coin_price_history(coin_id: str) -> List[Dict]:
    response = requests.get(
        f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days=9&interval=daily")

    # Returns a list of tuples
    # Item 0 -> Unix Timestamp
    # Item 1 -> price
    return response.json()['prices']


# utilize this function when submitting an order
def submit_order(coin_id: str, quantity: int, bid: float):
    """
    Mock function to submit an order to an exchange.

    Assume order went through successfully and the return value is the price the order was filled at.
    """
    app_logger.info('{} bid {} price {}'.format(coin_id, quantity, bid))
    return bid


def persist_coin(par1, par2, par3, par4):
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO coins(id, symbol, coin_name, current_price) VALUES (?,?,?,?)''',
                  (par1, par2, par3, par4))
        conn.commit()
    except Error as e:
        print(e)


def fetch_persisted_coins():
    global df
    try:
        c = conn.cursor()
        c.execute('''SELECT id, symbol, coin_name, current_price FROM coins''')
        df = pd.DataFrame(c.fetchall(), columns=['id', 'symbo', 'name', 'price'])
    except Error as e:
        print(e)


def prepare_order():
    for i, row in df.iterrows():
        price_hist = get_coin_price_history(row['id'])
        avg = float(sum(price[1] for price in price_hist) / len(price_hist))
        if row['price'] < avg:
            submit_order(row['id'], 1, row['price'])


def connect_database():
    global conn
    try:
        conn = sqlite3.connect(':memory:')
        c = conn.cursor()
        c.execute(
            '''CREATE TABLE IF NOT EXISTS coins([id] STRING PRIMARY KEY, [symbol] STRING, [coin_name] STRING, [current_price] INTEGER)'''
        )
        conn.commit()
    except Error as e:
        print(e)


def close_connection():
    try:
        if conn:
            conn.close()
    except Error as e:
        print(e)


def configure_logger():
    global app_logger
    app_logger = logging.getLogger()
    app_logger.setLevel(logging.INFO)

    output_file_handler = logging.FileHandler(filename='./storage/logs/app.log', mode='w')
    stdout_handler = logging.StreamHandler(sys.stdout)

    app_logger.addHandler(output_file_handler)
    app_logger.addHandler(stdout_handler)


def main():
    configure_logger()
    connect_database()
    coins = get_coins()
    for coin in coins[:3]:
        persist_coin(coin['id'], coin['symbol'], coin['name'], coin['current_price'])
    fetch_persisted_coins()
    prepare_order()
    close_connection()
