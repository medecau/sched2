.PHONY: help
help:	## Show this help.
	grep '^[^#[:space:]\.].*:' Makefile

.PHONY: lint
lint:	## Run linters.
	ruff check --select I --fix .
	ruff format .

.Phony: check
check:	## Run linters in check mode.
	ruff check .

.PHONY: test
test:	## Run tests.
	poetry run pytest

.PHONY: publish
publish: check	## Publish to PyPI.
	poetry publish --build
