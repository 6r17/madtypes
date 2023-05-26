venv:
	rm -rf env
	python3 -m virtualenv env
	env/bin/pip3 install -e .
	env/bin/pip3 install -e .["dev"]

test:
	env/bin/pytest tests -vv --cov=madtypes --cov-report=term-missing
