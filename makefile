build: clean
	python setup.py sdist bdist_wheel
	twine check dist/*

clean: clean-build clean-pyc clean-test clean-coverage

clean-build:
	- rm -rf build/
	- rm -rf dist/
	- rm -rf *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force {} +

clean-test:
	- rm -rf .pytest_cache/

clean-coverage:
	- rm .coverage
	- rm -rf htmlcov/

test:
	python -m pytest tests/

lint:
	flake8 simbump/ tests/