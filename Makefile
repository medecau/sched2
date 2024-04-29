.PHONY: help
help:			## Show this help.
	@grep '^[^#[:space:]\.].*:' Makefile

.PHONY: lint
fix:			## Run linters.
	ruff check --select I --fix .
	ruff format .

.PHONY: check
check:			## Run linters in check mode.
	ruff check --select I .

.PHONY: test
test: check		## Run tests.
	poetry run pytest

.PHONY: publish
publish: test check	## Publish to PyPI.
	poetry publish --build
