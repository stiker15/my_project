import json
import os
from datetime import datetime

import pandas as pd
import requests
import yfinance as yf
from dotenv import load_dotenv
from pandas import DataFrame

load_dotenv()
PACH_TO_FILE_EXCEL = "../data/operations.xlsx"


def get_time_for_greeting():
    """
    Функция возвращает «Доброе утро» / «Добрый день» / «Добрый вечер»
    / «Доброй ночи» в зависимости от текущего времени.
    """
    user_datetime_hour = datetime.now().hour
    if 5 <= user_datetime_hour < 12:
        return "Доброе утро"
    elif 12 <= user_datetime_hour < 18:
        return "Добрый день"
    elif 18 <= user_datetime_hour < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_data_time(date_time: str, data_format: str = "%Y-%m-%d %H:%M:%S") -> list[str]:
    dt = datetime.strptime(date_time, data_format)
    start_of_month = dt.replace(day=1)

    return [
        start_of_month.strftime("%d.%m.%Y %H:%M:%S"),
        dt.strftime("%d.%m.%Y %H:%M:%S"),
    ]


def get_path_and_period(path_of_file: str, period_date: list) -> DataFrame:
    """
    Функция принимает путь к exel файлу и список дат и возвращает
    таблицу в заданном периоде
    """
    df = pd.read_excel(path_of_file, sheet_name="Отчет по операциям")

    df["Дата операции"] = pd.to_datetime(df["Дата операции"], dayfirst=True)
    start_date = datetime.strptime(period_date[0], "%d.%m.%Y %H:%M:%S")
    end_date = datetime.strptime(period_date[1], "%d.%m.%Y %H:%M:%S")

    filtered_df = df[
        (df["Дата операции"] >= start_date) & (df["Дата операции"] <= end_date)
    ]
    sorted_df = filtered_df.sort_values(by="Дата операции", ascending=True)
    return sorted_df


def get_card_with_spend(sorted_df: DataFrame) -> list[dict]:
    """
    Функция принимает DataFrame и Возвращает список карт с расходами
    """
    card_spend_transaction = []
    card_sorted = sorted_df[
        ["Номер карты", "Сумма операции", "Кэшбэк", "Сумма операции с округлением"]
    ]
    for i, r in card_sorted.iterrows():
        if r['Сумма операции'] < 0:
            last_digits = str(r["Номер карты"]).replace("*", "")
            total_spent = r["Сумма операции с округлением"]
            cashback = total_spent // 100
            r = {
                "last_digits": last_digits,
                "total_spent": total_spent,
                "cashback": cashback,
            }
            card_spend_transaction.append(r)

    return card_spend_transaction


def get_top_transaction(sorted_df: DataFrame, get_top):
    """
    Функция принимает DataFrame и возвращает get_top топ-транзакций по сумме платежа
    """
    top_pay_transaction = []
    sorted_pay_df = sorted_df.sort_values(by="Сумма операции", ascending=False)
    top_transaction = sorted_pay_df.head(get_top)
    top_transaction_sorted = top_transaction[
        ["Дата платежа", "Сумма операции", "Категория", "Описание"]
    ]
    for i, r in top_transaction_sorted.iterrows():
        transaction = {
            "date": f"{r['Дата платежа']}",
            "amount": f"{r['Сумма операции']}",
            "category": f"{r['Категория']}",
            "description": f"{r['Описание']}",
        }
        top_pay_transaction.append(transaction)

    return top_pay_transaction


def get_currency(path_to_json: str) -> list[dict]:
    """
    Функция принимает на вход значения из json файла по ключу "user_currencies"
    и возвращает курс валют
    """
    currency_rates = []
    with open(path_to_json, "r", encoding="utf-8") as file:

        data = json.load(file)
        currences = data['user_currencies']

        for currence in currences:
            params = {"amount": 1, "from": currence, "to": "RUB"}
            api_key = os.getenv('API_KEY')
            response = requests.get(
                f"https://api.apilayer.com/exchangerates_data/convert",
                headers={"apikey": api_key},
                params=params,
            )

            status_code = response.status_code
            if status_code == 200:
                result = response.json()
                currency_code_response = result["query"]["from"]
                currency_amount = round(result['result'], 2)
                currency_rates.append(
                    {
                        "currency": f"{currency_code_response}",
                        "rate": f"{currency_amount}",
                    }
                )
        return currency_rates


def get_stock(path_to_json: str) -> list[dict]:
    """
    Функция принимает на вход значения из json файла по ключу "user_stocks"
    и возвращает стоимость акций
    """
    stock_prices = []
    with open(path_to_json, "r", encoding="utf-8") as file:
        data = json.load(file)
        stocks = data['user_stocks']

        for stock in stocks:
            ticker = yf.Ticker(stock)
            price = ticker.info.get("regularMarketPrice")
            stock_prices.append({"symbol": stock, "price": price})

    return stock_prices
