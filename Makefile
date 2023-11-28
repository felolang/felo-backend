APPLICATION_NAME ?= felo
CODE = felo
TEST = pytest --verbosity=2 --showlocals --log-level=DEBUG

args := $(wordlist 2, 100, $(MAKECMDGOALS))
ifndef args
MESSAGE = "No such command (or you pass two or many targets to ). List of possible commands: make help"
else
MESSAGE = "Done"
endif

all:
	@echo "make deps				- Export dependencies to requirements.txt"


migrate:  ##@Database Do all migrations in database
	cd $(APPLICATION_NAME)/db && PYTHONPATH='../..' alembic upgrade $(args)

revision:  ##@Database Create new revision file automatically with prefix (ex. 2022_01_01_14cs34f_message.py)
	cd $(APPLICATION_NAME)/db && alembic revision --autogenerate

format:
	isort $(CODE) --profile black
	black $(CODE)

lint:
	pylint --rcfile='.pylintrc' --disable=R0913 --disable=W1514 $(CODE)

start:
	uvicorn felo.main:app --reload

reqs:
	poetry export --without-hashes --without dev -f requirements.txt --output requirements.txt

db:
	echo "${DB_PASS}\r"
	gcloud sql connect felo --user admin --database=main
	expect "*Password*"
	send -- "${DB_PASS}\r"
	expect eof

deploy: reqs
	gcloud app deploy

services: 
	docker-compose -f docker-compose.yml up -d --remove-orphans
