build: clean
	python -m build
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

lint:
	flake8 myver/ tests/ --max-complexity=10 --max-line-length=127

test:
	python -m pytest -vv -rfEs ./tests/

coverage: clean-coverage
	coverage run --branch --source=myver/ -m pytest -v -rfEs tests/
	coverage html -d htmlcov/
	coverage report
