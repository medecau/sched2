.PHONY: help
help:			## Show this help.
	@grep '^[^#[:space:]\.].*:' Makefile

.PHONY: lint
fix:			## Run linters.
	ruff check --fix .
	ruff format .

.PHONY: check
check:			## Run linters in check mode.
	ruff check .
	ruff format --check .

.PHONY: test
test: check		## Run tests.
	tox -qp auto

.PHONY: publish
publish: test check	## Publish to PyPI.
	uv build
	uv publish
