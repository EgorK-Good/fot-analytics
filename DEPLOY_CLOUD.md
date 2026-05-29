# Развёртывание «Аналитик+» в облаке

Приложение — **Streamlit**. Самый простой бесплатный вариант: **Streamlit Community Cloud** (официальный хостинг от создателей Streamlit).

---

## Важно перед публикацией

| Ограничение | Что это значит |
|-------------|----------------|
| **SQLite на бесплатном облаке** | База `fot_analytics.db` живёт на диске контейнера. После перезапуска/пересборки данные могут **сброситься**. Для диплома: загружайте **демо-данные** после каждого деплоя. |
| **Папка `data/inbox`** | Автоимпорт из папки на сервере **неудобен** в облаке. Используйте вкладку **«Файлы»** или **OData**. |
| **Prophet** | Первая сборка в облаке может занять **10–20 минут** (тяжёлая зависимость). |
| **Пароль admin** | На публичном URL смените логин/пароль в разделе **«Пользователи»** или не публикуйте ссылку широко. |

---

## Вариант 1 — Streamlit Community Cloud (рекомендуется)

**Сайт:** https://share.streamlit.io  
**Цена:** бесплатно (публичные приложения)  
**Нужно:** аккаунт GitHub, репозиторий с кодом

### Шаг 1. Репозиторий на GitHub

1. Зарегистрируйтесь на https://github.com  
2. Создайте **новый репозиторий** (например `fot-analytics`), без README если зальёте код сами  
3. На компьютере в PowerShell:

```powershell
cd C:\Users\amiry\Desktop\FOTAnalytics\fot_analytics_python
git init
git add .
git commit -m "Initial commit: FOT Analytics Streamlit app"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/fot-analytics.git
git push -u origin main
```

> Замените `ВАШ_ЛОГИН/fot-analytics` на свой репозиторий.  
> Файл `fot_analytics.db` в `.gitignore` — в Git не попадёт (так и задумано).

**Если весь проект лежит в `FOTAnalytics` с подпапкой:**

- либо пушите **только** содержимое `fot_analytics_python` (как выше),
- либо пушите корень `FOTAnalytics` и на шаге 3 укажите путь к приложению.

### Шаг 2. Подключение Streamlit Cloud

1. Войдите на https://share.streamlit.io через **GitHub**  
2. **New app** → выберите репозиторий `fot-analytics`  
3. Заполните поля:

| Поле | Значение |
|------|----------|
| **Branch** | `main` |
| **Main file path** | `app.py` (если корень репо = `fot_analytics_python`) |
| | или `fot_analytics_python/app.py` (если корень репо = `FOTAnalytics`) |
| **App URL** | например `fot-analytics` → адрес будет `https://fot-analytics-xxxx.streamlit.app` |

4. **Deploy** и дождитесь сборки (логи внизу; при ошибке Prophet — см. раздел «Проблемы»).

### Шаг 3. Первый вход в облаке

1. Откройте выданный URL  
2. Войдите: `admin` / `admin`  
3. **Импорт 1С** → **Демо-данные** → загрузить набор  
4. Откройте **Главная** / **Аналитика**

### Где смотреть приложение

После деплоя ссылка вида:

`https://<имя-приложения>-<хеш>.streamlit.app`

Она же в личном кабинете: https://share.streamlit.io → ваше приложение → **View app**.

---

## Вариант 2 — Render.com

**Сайт:** https://render.com  
**Цена:** бесплатный tier (с «засыпанием» сервиса при простое)

1. Репозиторий на GitHub (как выше)  
2. **New +** → **Web Service** → подключить репозиторий  
3. Параметры:

| Параметр | Значение |
|----------|----------|
| **Root Directory** | `fot_analytics_python` (если репо — корень FOTAnalytics) |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0` |
| **Instance** | Free |

4. После деплоя откройте URL вида `https://fot-analytics.onrender.com`

---

## Вариант 3 — Railway

**Сайт:** https://railway.app  
Удобен для Streamlit, есть бесплатный лимит по кредитам.

1. **New Project** → **Deploy from GitHub repo**  
2. Root: `fot_analytics_python`  
3. Команда запуска (в настройках сервиса):

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

4. Railway выдаст публичный домен `*.up.railway.app`

---

## Вариант 4 — Hugging Face Spaces

**Сайт:** https://huggingface.co/spaces  
**SDK:** Streamlit

1. **Create new Space** → SDK **Streamlit**  
2. Загрузите файлы из `fot_analytics_python` (или подключите Git)  
3. В Space должны быть: `app.py`, `requirements.txt`, папки `pages/`, `services/`, и т.д.

Подходит для демонстрации в дипломе; лимиты RAM могут быть жёстче для Prophet.

---

## Вариант 5 — Свой VPS (Timeweb, Selectel, AWS, Azure)

Полный контроль, SQLite сохраняется на диске.

```bash
# На сервере Ubuntu
sudo apt update && sudo apt install -y python3.11-venv
git clone https://github.com/ВАШ_ЛОГИН/fot-analytics.git
cd fot-analytics   # или fot_analytics_python
python3.11 -m venev .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Доступ: `http://IP_СЕРВЕРА:8501`. Для HTTPS — nginx + Let's Encrypt.

---

## Локальный запуск (для проверки перед облаком)

```powershell
cd C:\Users\amiry\Desktop\FOTAnalytics\fot_analytics_python
.\.venv\Scripts\activate
streamlit run app.py
```

Браузер: http://localhost:8501

---

## Частые проблемы при деплое

| Ошибка | Решение |
|--------|---------|
| Сборка падает на `prophet` | Подождать повторный деплой; в репо есть `packages.txt` с `build-essential` |
| Пустой дашборд | Загрузить **демо-данные** в облаке |
| Не находит `pages/` | Проверить **Main file path** — `app.py` должен быть в той же папке, что и `pages/` |
| Медленная «Аналитика» | Нормально для Prophet на free-tier |

---

## Что указать в дипломе

- **Среда эксплуатации:** веб-браузер, сервер Streamlit (облако Streamlit Community Cloud / Render / VPS).  
- **URL:** вставить реальную ссылку после деплоя.  
- **Доступ:** логин/пароль тестового пользователя (не публикуйте боевой пароль в открытой работе — укажите «выдаётся администратором»).
