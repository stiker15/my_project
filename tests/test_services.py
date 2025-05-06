import pandas as pd
import json
from src.services import analyze_cashback_categories_from_excel


def test_analyze_cashback_categories_from_excel_basic(tmp_path):
    # Подготавливаем данные
    df = pd.DataFrame({
        "Дата операции": ["15.03.2024", "16.03.2024", "17.02.2024", "18.03.2024"],
        "Категория": ["Еда", "Еда", "АЗС", "Такси"],
        "Кэшбэк": [10, 20, 5, 30]
    })
    excel_file = tmp_path / "cashback.xlsx"
    df.to_excel(excel_file, index=False)

    # Вызываем функцию
    result_json = analyze_cashback_categories_from_excel(excel_file, 2024, 3)
    result = json.loads(result_json)

    # Проверяем результат
    assert result == {"Еда": 30, "Такси": 30}


def test_analyze_cashback_categories_from_excel_all_zero_cashback(tmp_path):
    df = pd.DataFrame({
        "Дата операции": ["01.05.2024", "02.05.2024"],
        "Категория": ["Фастфуд", "АЗС"],
        "Кэшбэк": [0, 0]
    })
    excel_file = tmp_path / "cashback2.xlsx"
    df.to_excel(excel_file, index=False)

    result_json = analyze_cashback_categories_from_excel(excel_file, 2024, 5)
    result = json.loads(result_json)

    assert result == {}


def test_analyze_cashback_categories_from_excel_empty_file(tmp_path):
    df = pd.DataFrame(columns=["Дата операции", "Категория", "Кэшбэк"])
    excel_file = tmp_path / "empty.xlsx"
    df.to_excel(excel_file, index=False)

    result_json = analyze_cashback_categories_from_excel(excel_file, 2024, 1)
    result = json.loads(result_json)

    assert result == {}


def test_analyze_cashback_categories_from_excel_partial_nan(tmp_path):
    df = pd.DataFrame({
        "Дата операции": ["15.04.2024", None, "20.04.2024"],
        "Категория": ["Аптека", "Еда", "Еда"],
        "Кэшбэк": [15, 25, None]
    })
    excel_file = tmp_path / "cashback_nan.xlsx"
    df.to_excel(excel_file, index=False)

    result_json = analyze_cashback_categories_from_excel(excel_file, 2024, 4)
    result = json.loads(result_json)
    # только "Аптека": 15, так как вторая запись пропустится из-за None в дате, третья из-за None в кэшбэке
    assert result == {"Аптека": 15}
