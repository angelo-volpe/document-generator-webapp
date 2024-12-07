### Requirements
```pip install -r requirements.txt```

### Init DB
```
python manage.py makemigrations
python manage.py migrate
```

## Run Server
```python manage.py runserver```

## Run with PostgeSQL
```
docker compose up
```
initialise the database
```
docker compose exec document_app python manage.py migrate --noinput
```

## Access the web interface
http://localhost:8000/document_generator/