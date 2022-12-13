# Project installation


##### Link to the GIT repository:

- *https://gitlab.godeltech.com/gte-internal/python/identity-server-poc*

##### Running docker:

- *sudo docker compose -f ./docker-compose.dev.yml up*

##### Starting poetry:

- *poetry install*
- *poetry shell*

##### Server start:

- uvicorn src.main:app --reload

##### Settings for tests:

- Add to the pyproject.toml this:

*[tool.pytest.ini_options]
pythonpath = [
  ".", "src",
]*

- Create file "*pytest.ini*" and add to it this:

*[pytest]
pythonpath = . src*

- Run tests with "*poetry run pytest""*

##### Settings for debugger:

Add to your *.vscode/settings.json* file your paths to Virtualenv folder and to the python. To get this paths use "*poetry env info*".

Example (add your versions to *.vscode/settings.json*):
*"python.pythonPath": "/home/danya/.cache/pypoetry/virtualenvs/identity-server-poc-hY52nw-1-py3.10",
"python.defaultInterpreterPath": "/home/danya/.cache/pypoetry/virtualenvs/identity-server-poc-hY52nw-1-py3.10/bin/python",*

##### PostgreSQL admin:

*http://localhost/login?next=%2Fbrowser%2F*

- login: *admin@example.com*, password: *admin* .After logging create your personal accaunt.
- After relogging:right click "*Server*" -> "*Register*" ->"*Server*".

    Name:*is_db*

    Host name/adress:*172.20.0.1* (or your own adress)

    Username:***postgres***

    Password:*postgres*

##### Alembic update or change DB:
- upgrade:
    "alembic upgrade heads"
- change:
    "alembic revision --autogenerate -m "[_**Your comment**_]" "

##### Links:


* Server:

    *http://127.0.0.1:8000/*

* Swagger:

*
    http://127.0.0.1:8000/docs*

- PostgreSQL admin:
    *http://localhost/login?next=%2Fbrowser%2F*
