all: format lint

format:
	python3 -m isort geez/
	python3 -m black geez/

lint:
	python3 -m isort -c geez/
	python3 -m black --check geez/
	python3 -m flake8 geez/
	python3 -m mypy geez/
