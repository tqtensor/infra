SHELL := /bin/bash

pulumi:
	./scripts/pulumi_helper.sh

toml-sort:
	uv run toml-sort -i pyproject.toml --sort-table-keys --sort-inline-tables --sort-inline-arrays
