SHELL := /bin/bash

toml-sort:
	uv run toml-sort -i pyproject.toml --no-sort-tables --sort-table-keys
