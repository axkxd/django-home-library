# Моя Библиотека - проект на Django

### Обзор
Это веб-приложение создает онлайн-каталог для библиотеки, где пользователи могут просматривать доступные книги и управлять своими учетными записями.

Основные реализованные функции:
- Модели для книг, авторов, экземпляров книг, языка и жанра.
- Пользователи могут регистрироваться и авторизоваться.
- Пользователи могут просматривать списки книг, авторов и просматривать подробную информацию о них.
- Пользователи с правами администратора могут создавать модели и управлять ими.
- Пользователи с дополнительными правами могут продлевать подписку на книгу.

    ![image info](https://github.com/axkxd/django-home-library/blob/main/blog/static/images/lib.png)

### Быстрый старт

Чтобы запустить этот проект, сделайте следующее:
1. Настройте среду разработки Python. 
    
    Linux
    
    `sudo apt-get install python3-venv`    If needed
    
    `python3 -m venv .venv`
    
    `source .venv/bin/activate`

    Windows
    
    `py -3 -m venv .venv`
    
    `.venv\scripts\activate`

2. Выполните команды (для Windows – `py` вместо `python3`):

    `python3 -m pip install --upgrade pip`
    
    `python3 -m pip install -r requirements.txt`
    
    `python3 manage.py makemigrations`
    
    `python3 manage.py migrate`
    
    `python3 manage.py collectstatic`

    Запустите тесты. Все должно работать.
    
    `python3 manage.py test`

    При необходимости, создайте суперпользователя.
    
    `python3 manage.py createsuperuser`

    `python3 manage.py runserver`

3. Чтобы посмотреть сайт перейдите по url `http://127.0.0.1:8000`
