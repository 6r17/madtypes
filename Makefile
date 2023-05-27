venv:
	rm -rf env
	python3 -m virtualenv env
	env/bin/pip3 install -e .
	env/bin/pip3 install -e .["dev"]

test:
	env/bin/pytest tests -vv --cov=madtypes --cov-report=term-missing

upload:
	rm -rf madtypes.egg-info
	env/bin/pip3 install twine
	env/bin/python3 setup.py sdist bdist_wheel
	env/bin/twine upload dist/* --verbose
