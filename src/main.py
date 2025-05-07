import pandas as pd

from services import analyze_cashback_categories_from_excel
from src.reports import spending_by_category
from src.utils import PACH_TO_FILE_EXCEL
from views import main_info

if __name__ == "__main__":

    # Запуск views.py
    print(main_info("2020-05-20 15:40:00"))

    # Запуск services.py
    year = int(input("Введите год: "))
    month = int(input("Введите месяц: "))
    print(
        analyze_cashback_categories_from_excel('../data/operations.xlsx', year, month)
    )

    # Запуск reports.py
    df = pd.read_excel(PACH_TO_FILE_EXCEL, sheet_name="Отчет по операциям")
    spending_by_category(df, category="Фастфуд", date="2020-05-20")
