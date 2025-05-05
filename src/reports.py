import functools
import json
import pandas as pd

from typing import Optional
import datetime
import os


def repot_decorator(file_name=None):
    """
        Декоратор для функций-отчетов, который записывает в файл результат,
        если имя файла передано, а если оно не передано тогда берем по умолчанию
    """
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            nonlocal file_name
            if file_name is None:
                file_name = input("Введите название файла: Пример формата: report_.json")
            category = args[1] if len(args) > 1 else kwargs.get('category', 'category')
            date = args[2] if len(args) > 2 else kwargs.get('date')
            if not date:
                date = datetime.datetime.today().strftime('%Y-%m-%d')
            if not file_name:
                file_out = f'report_{category}_{date}.json'
            else:
                file_out = file_name

            dirpath = os.path.dirname(file_out)
            if dirpath:
                os.makedirs(dirpath, exist_ok=True)

            with open(file_out, 'w', encoding="utf-8") as file:
                if isinstance(result, pd.DataFrame):
                    result = result.copy()
                    for col in result.columns:
                        if pd.api.types.is_datetime64_any_dtype(result[col]):
                            result[col] = result[col].astype(str)
                    data = result.to_dict(orient="records")
                    json.dump(data, file, indent=4, ensure_ascii=False)

            return result
        return wrapper
    return inner


@repot_decorator()
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         date: Optional[str] = None) -> pd.DataFrame:
    """
       Функция возвращает траты по категории за последние 3 месяца
    """
    if date is None:
        date = datetime.datetime.today().strftime('%Y-%m-%d')
    end_date = pd.to_datetime(date)
    start_date = end_date - pd.DateOffset(months=3)
    # Преобразуем дату
    if transactions['Дата операции'].dtype == 'O':
        transactions['date'] = pd.to_datetime(transactions['Дата операции'], format="%d.%m.%Y %H:%M:%S")
    else:
        transactions['date'] = transactions['Дата операции']
    # Фильтрация
    mask = (
        transactions['Категория'] == category) & (transactions['date'] >= start_date) & (
        transactions['date'] <= end_date
    )
    return transactions.loc[mask]
