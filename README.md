# Портфолио Старкова Ивана

Учебный проект сайта-портфолио для курсовой работы на стеке `Vue 3 + FastAPI + SQLite`.

## Что реализовано

- главная страница с биографией, фото и краткой информацией;
- блок с таймлайном обучения и развития;
- список проектов, данные для которого хранятся в SQLite;
- форма обратной связи с сохранением сообщений в базу данных;
- админ-панель с авторизацией, добавлением, редактированием и удалением проектов;
- просмотр сообщений из формы обратной связи;
- адаптивная верстка и раздача собранного frontend через FastAPI.

## Структура

- `backend/` — FastAPI, SQLAlchemy, SQLite;
- `frontend/` — Vue 3 + Vite;
- `frontend/public/images/ivan-starkov.jpg` — фотография для портфолио.

## Запуск

### 1. Установить Python

Нужен Python `3.11+`.

### 2. Запустить backend

```powershell
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend будет доступен на `http://127.0.0.1:8000`.

### 3. Запустить frontend

Во второй консоли:

```powershell
cd frontend
cmd /c npm install
cmd /c npm run dev
```

Frontend будет доступен на `http://127.0.0.1:5173`.

## Сборка frontend для FastAPI

```powershell
cd frontend
cmd /c npm install
cmd /c npm run build
```

После этого FastAPI сможет раздавать готовый сайт из папки `frontend/dist`.

## Данные администратора

- логин: `admin`
- пароль: `starkov2004`

Для курсовой лучше потом поменять пароль через переменные окружения:

- `PORTFOLIO_ADMIN_USERNAME`
- `PORTFOLIO_ADMIN_PASSWORD`
- `PORTFOLIO_SECRET_KEY`

## Что хранится в базе

- профиль и краткая биография;
- учебный таймлайн;
- проекты;
- сообщения из контактной формы;
- администратор.

