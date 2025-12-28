# Document Generator Webapp

This project is a simple front-end written in Django that allow to easly generate synthetic data for Machine Learning models training, by starting from a template document.

## Run with Docker
```
docker compose up
```
initialise the database
```
uv run python manage.py makemigrations
docker compose exec document_app uv run python manage.py migrate --noinput
```

## Access the web interface
http://localhost:8000/document_app/


### Run tests
```
uv run coverage run manage.py test && uv run coverage report -m
```

### Pre-commit

Runs:
- ruff for linting and formatting
- mypy for tpye checking

```
uv run pre-commit run --all-files
```
