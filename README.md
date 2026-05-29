# 1С:Аналитика — Фонд оплаты труда (Python)

Веб-приложение для анализа ФОТ и кадров с импортом из 1С, дашбордом в стиле 1С:Аналитика и прогнозами Prophet.

**Стек:** Python, SQLAlchemy, Pandas, Streamlit, Prophet, Plotly

## Запуск

```powershell
cd fot_analytics_python
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Облако (Streamlit Cloud, Render, Railway)

Пошаговая инструкция: **[DEPLOY_CLOUD.md](DEPLOY_CLOUD.md)**  
Кратко: залить код на **GitHub** → https://share.streamlit.io → **New app** → Main file: `app.py` → Deploy.

## Тесты

```powershell
pip install -r requirements-dev.txt
pytest
# с покрытием:
pytest --cov=services --cov=models --cov-report=term-missing
```

Логин: `admin` / `admin`

1. **Импорт 1С** → вкладка «Демо-данные» или загрузите CSV из `data/templates/`
2. **Главная** → KPI и графики

## Импорт из 1С

| Способ | Описание |
|--------|----------|
| **Папка inbox** | Положите CSV/Excel в `data/inbox/` — автоимпорт при входе |
| **Планировщик Windows** | `python scripts/auto_import.py` по расписанию |
| **OData** | URL публикации 1С в разделе «Импорт 1С» → OData API |
| **Вручную** | Загрузка файла через интерфейс |

Шаблоны колонок: `data/templates/сотрудники.csv`, `data/templates/начисления.csv`

## Разделы

- **Главная** — KPI, динамика ФОТ, структура по отделам, распределение окладов
- **Сотрудники** — справочник кадров
- **Начисления** — детализация выплат
- **Аналитика** — прогноз ФОТ и кадров (Prophet)
- **Импорт 1С** — настройки и журнал
- **Отчёты** — Excel
