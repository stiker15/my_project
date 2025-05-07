import json
import logging
from datetime import datetime

import pandas as pd

logging.basicConfig(level=logging.INFO)


def analyze_cashback_categories_from_excel(filepath, year=None, month=None):
    # Получаем текущий год и месяц, если не переданы параметры
    now = datetime.now()
    year = year if year is not None else now.year
    month = month if month is not None else now.month
    # Чтение данных из Excel
    df = pd.read_excel(filepath)

    # Приведем к формату нужные поля
    df['Дата операции'] = pd.to_datetime(
        df['Дата операции'], dayfirst=True, errors='coerce'
    )
    df['Кэшбэк'] = pd.to_numeric(df['Кэшбэк'], errors='coerce')

    # Фильтрация по году и месяцу
    filtered = df[
        (df['Дата операции'].dt.year == year) & (df['Дата операции'].dt.month == month)
    ]

    # Группируем и суммируем кэшбэк
    cashback_per_category = (
        filtered.groupby('Категория')['Кэшбэк'].sum().round().astype(int).to_dict()
    )

    # Оставить только категории где кэшбэк больше 0
    cashback_per_category = {k: v for k, v in cashback_per_category.items() if v > 0}

    logging.info(f"Cashback per category for {year}-{month}: {cashback_per_category}")
    return json.dumps(cashback_per_category, ensure_ascii=False, indent=4)
