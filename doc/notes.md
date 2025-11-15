python -m venv .venv
.venv/Scripts/activate
pip install django
pip freeze > requirements.txt
django-admin startproject tiktoeken .
python manage.py startapp core