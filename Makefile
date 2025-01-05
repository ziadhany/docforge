PYTHON_EXE?=python3
VENV=venv
ACTIVATE?=. ${VENV}/bin/activate;
MANAGE=${VENV}/bin/python manage.py

isort:
	@echo "-> Apply isort changes to ensure proper imports ordering"
	${VENV}/bin/isort --sl -l 100 src tests setup.py

black:
	@echo "-> Apply black code formatter"
	${VENV}/bin/black -l 100 src tests setup.py

valid: isort black

check:
	@echo "-> Run pycodestyle (PEP8) validation"
	@${ACTIVATE} pycodestyle --max-line-length=100 --exclude=.eggs,venv,lib,thirdparty,docs,migrations,settings.py,.cache .
	@echo "-> Run isort imports ordering validation"
	@${ACTIVATE} isort --sl --check-only -l 100 setup.py src tests .
	@echo "-> Run black validation"
	@${ACTIVATE} black --check --check -l 100 src tests setup.py

test:
	@echo "-> Run the test suite"
	${VENV}/bin/pytest -vvs

run:
	${MANAGE} runserver 8000 --insecure

.PHONY: check valid black isort test run