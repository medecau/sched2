.PHONY: help
help:	## Show this help.
	grep '^[^#[:space:]\.].*:' Makefile

.PHONY: lint
lint:	## Run linters.
	poetry run isort .
	poetry run black .

.Phony: check
check:	## Run linters in check mode.
	poetry run isort --check .
	poetry run black --check .

.PHONY: publish
publish: check	## Publish to PyPI.
	poetry publish --build
