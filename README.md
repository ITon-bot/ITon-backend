# ITon

## Описание проекта
Это **бэкенд-приложение** для **Telegram Mini App**, разработанное на **Django**.

## ...

---

## 🛠Технологии и стек

- **Python 3.10+**
- **Django 4.x**
- **PostgreSQL**
- **Docker**
- **Django REST Framework**

---

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
