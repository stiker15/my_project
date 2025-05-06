import pytest
import pandas as pd
import os
import tempfile
import json
from src.reports import spending_by_category, repot_decorator


@pytest.fixture
def sample_transactions():
    data = [
        {"Дата операции": "01.01.2024 10:00:00", "Категория": "Продукты", "Сумма": 100},
        {"Дата операции": "15.04.2024 15:00:00", "Категория": "Развлечения", "Сумма": 150},
        {"Дата операции": "18.05.2024 09:20:00", "Категория": "Продукты", "Сумма": 200}
    ]

    return pd.DataFrame(data)


def test_report_file_creation_and_contents(sample_transactions, monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        filename = os.path.join(tmpdir, "testreport.json")
        # Патчим input, чтобы декоратор взял корректное имя файла
        monkeypatch.setattr("builtins.input", lambda prompt: filename)
        decorated = repot_decorator(filename)(spending_by_category)

        # Выбираем существующую категорию и дату в нужном диапазоне
        result = decorated(sample_transactions, "Продукты", date="2024-05-20")
        assert isinstance(result, pd.DataFrame)
        assert os.path.exists(filename)

        # Проверяем содержимое файла
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert all("Категория" in rec for rec in data)
            assert any(rec["Категория"] == "Продукты" for rec in data)


def test_report_file_creation_default_name(sample_transactions, monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Переходим во временную директорию
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            # Патчинг input — пользователь ничего не вводит
            monkeypatch.setattr("builtins.input", lambda prompt: "")
            decorated = repot_decorator()(spending_by_category)
            result = decorated(sample_transactions, "Продукты", date="2024-05-20")
            assert isinstance(result, pd.DataFrame)
            # Проверяем, что файл с нужным именем был создан
            expected = "report_Продукты_2024-05-20.json"
            assert os.path.exists(expected)
        finally:
            os.chdir(old_cwd)
