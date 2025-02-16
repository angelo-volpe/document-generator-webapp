## Run with Docker
```
docker compose up
```
initialise the database
```
python manage.py makemigrations
docker compose exec document_app python manage.py migrate --noinput
```

## Access the web interface
http://localhost:8000/document_generator/


### Run tests
```
poetry install --with dev
coverage run manage.py test
coverage report -m
```

### Code Style
```
black .
```