import pandas as pd
import json
from datetime import datetime
from unittest.mock import patch, Mock


from src.utils import (
    get_time_for_greeting, get_data_time, get_path_and_period,
    get_card_with_spend, get_top_transaction, get_currency, get_stock
)


def test_get_time_for_greeting(monkeypatch):
    class MockDatetime(datetime):
        @classmethod
        def now(cls):
            return cls(2024, 6, 1, 9)  # 9:00
    with patch("src.utils.datetime", MockDatetime):
        assert get_time_for_greeting() == "Доброе утро"


def test_get_data_time():
    result = get_data_time("2024-06-08 17:14:00")
    assert result[0].startswith("01.")  # начало месяца
    assert result[1].startswith("08.")  # тот же день


def test_get_path_and_period(tmp_path):
    # создаём тестовый excel
    df = pd.DataFrame({
        "Дата операции": ["01.06.2024 09:00:00", "08.06.2024 12:00:00"],
        "Сумма операции": [-100, 500],
        "Категория": ["Такси", "Фастфуд"]
    })
    excelfile = tmp_path / "test.xlsx"
    df.to_excel(excelfile, sheet_name="Отчет по операциям", index=False)
    period = ["01.06.2024 00:00:00", "09.06.2024 23:59:59"]
    res = get_path_and_period(str(excelfile), period)
    assert len(res) == 2


def test_get_card_with_spend():
    df = pd.DataFrame({
        "Номер карты": ["*1234", "*5678"],
        "Сумма операции": [-100, 200],
        "Кэшбэк": [0, 1],
        "Сумма операции с округлением": [100, 200]
    })
    cards = get_card_with_spend(df)
    assert cards[0]["last_digits"] == "1234"


def test_get_top_transaction():
    df = pd.DataFrame({
        "Дата платежа": ["08.06.2024", "07.06.2024"],
        "Сумма операции": [100, 200],
        "Категория": ["Еда", "АЗС"],
        "Описание": ["старбакс", "bp"]
    })
    res = get_top_transaction(df, 1)
    assert len(res) == 1
    assert res[0]["amount"] == "200"


def test_get_currency(tmp_path):
    fakejson = tmp_path / "currencies.json"
    data = {"user_currencies": ["USD"]}
    fakejson.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"query": {"from": "USD"}, "result": 88.8}
    with patch("src.utils.requests.get", return_value=fake_response):
        with patch("os.getenv", return_value="FAKEKEY"):
            res = get_currency(str(fakejson))
            assert res[0]["rate"] == "88.8"


def test_get_stock(tmp_path):
    fakejson = tmp_path / "stocks.json"
    data = {"user_stocks": ["AAPL"]}
    fakejson.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    fake_ticker = Mock()
    fake_ticker.info = {"regularMarketPrice": 123}
    with patch("src.utils.yf.Ticker", return_value=fake_ticker):
        res = get_stock(str(fakejson))
        assert res[0]["symbol"] == "AAPL"
