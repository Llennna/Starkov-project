# 🧑‍💻 Портфолио Старкова Ивана

> Учебный проект сайта-портфолио для курсовой работы.  
> **Стек:** `Vue 3` + `FastAPI` + `SQLite`

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi)
![Vue](https://img.shields.io/badge/Vue-3.4-42b883?logo=vuedotjs)
![SQLite](https://img.shields.io/badge/SQLite-3-003b57?logo=sqlite)

---

## ✨ Что реализовано

- ✅ Главная страница с биографией, фото и краткой информацией  
- 📅 Таймлайн обучения и развития  
- 📂 Список проектов (данные хранятся в SQLite)  
- 📩 Форма обратной связи с сохранением сообщений в БД  
- 🛠 Админ-панель с авторизацией  
  - добавление / редактирование / удаление проектов  
  - просмотр сообщений из формы связи  
- 📱 Адаптивная вёрстка  
- 🚀 Раздача собранного фронтенда через FastAPI

---

## 📁 Структура проекта
```
portfolio/
├── backend/ # FastAPI + SQLAlchemy + SQLite
├── frontend/ # Vue 3 + Vite
└── frontend/public/images/ivan-starkov.jpg # фото для портфолио
```
---

## 🚀 Запуск (локально)


---
### 1️⃣ Установить Python

Требуется **Python 3.11+**


---


### 2️⃣ Запустить backend

```powershell
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```
🔗 Backend будет доступен: http://127.0.0.1:8000

---


### 3️⃣ Запустить frontend (в отдельной консоли)
```
cd frontend
cmd /c npm install
cmd /c npm run dev
```
🔗 Frontend будет доступен: http://127.0.0.1:5173
---


🔐 Данные администратора (по умолчанию)
Поле	Значение
Логин	admin
Пароль	starkov2004
