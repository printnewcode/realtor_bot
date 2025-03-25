# GAI_bot
Bot for ai chat

Telegram bot with ai chat

1. clone repositori
2. create and activate .venv
```python -m venv .venv```
```.venv\Scripts\activate```
5. create .env file with 
```python3
BOT_TOKEN=
OWNER_ID=
HOOK=
```
4. install requirements 'pip install -r requirements.txt'
5. ngrok http 8000 link to HOOK in .env
6. python manage.py makemigrations
7. python manage.py migrate
8. python manage.py createsuperuser
9. python manage.py runserver
10. 127.0.0.1:8000/bot/  - setting webhook
11. ADMIN 127.0.0.1:8000/admin/
