# ITon - Work, Communicate, Explore

## Описание проекта
Это **бэкенд-приложение** для **Telegram Mini App**, разработанное на **Django**.

## ...

---

## 🛠Технологии и стек

- **Python 3.10+**
- **Django 4.x**
- **PostgreSQL** — база данных.
- **Aiogram** — для интеграции с Telegram.
- **Google API's** — для работы с локациями, книгами и вузами.
- **Docker** — для контейнеризации проекта.
- **DRF (Django REST Framework)** — создание REST API.

---

##  Структура проекта

```bash
/
│
├── core/                   # Конфигурация проекта
│   ├── settings.py           # Основные настройки Django
│   ├── urls.py               # Главные маршруты
│   └── wsgi.py               # WSGI для деплоя
│
├── users/                    # Приложение "Пользователи"
│   ├── models.py             # Модели пользователей
│   ├── serializers.py        # DRF-сериализаторы
│   ├── views.py              # API-вьюхи
│   ├── urls.py               # Эндпоинты для пользователей
│   └── tests.py              # Тесты для приложения
│
├── events/                   # Приложение "Мероприятия"
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── vacancies/                # Приложение "Вакансии"
│
├── notifications/            # Управление уведомлениями
│   ├── models.py
│   ├── services.py           # Логика отправки уведомлений
│   └── telegram_api.py       # Обёртка над Telegram Bot API
│
├── manage.py                 # Django CLI
└── requirements.txt          # Зависимости проекта
```

#  Установка и запуск
## 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/telegram-mini-app-backend.git
cd telegram-mini-app-backend
```
## 2. Создание и активация виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Для Linux/macOS
venv\Scripts\activate     # Для Windows
```
## 3. Установка зависимостей
```bash
pip install -r unix-requirements.txt # Для Linux/macOS
pip install -r requirements.txt # Для Windows
```
## 4. Настройка переменных окружения
### Создайте файл .env в корне проекта и заполните его значениями из .env.template

## 5. Применение миграций и создание суперпользователя
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
## 6. Запуск локального сервера
```bash
python manage.py runserver
```
### Сервер будет доступен по адресу: http://127.0.0.1:8000/

# Авторы
## Quatry — Backend Developer


### Этот проект распространяется под MIT License. Подробнее в файле LICENSE.
