help:                                            ## Show help docs
	@sed -ne '/@sed/!s/## //p' $(MAKEFILE_LIST)

# === CI COMMANDS ===
check-types:                                     ## Check static typing
	uv run mypy --strict --ignore-missing-imports --implicit-optional --allow-untyped-decorators --disable-error-code import-untyped --disable-error-code no-redef src
	# todo https://github.com/astral-sh/ty

check-style:                                     ## Check formatting
	uv run ruff check --select I src tests
	uv run ruff format --check --line-length=120 src tests

fix-style:                                       ## Fix formatting
	uv run ruff check --select I --fix src tests
	uv run ruff format --line-length=120 src tests

sast:                                            ## Run static application security testing
	uv run bandit --recursive src

run-tests:                                       ## Run tests with coverage and report
	uv run pytest --numprocesses=auto --cov-report=term-missing --cov-report=html --cov-fail-under=95 --cov src

check-static-all: check-types check-style sast   ## Run all static checks

check-test-all: check-static-all run-tests       ## Run all checks/tests

package-build:                                   ## Build Python package
	uv build

package-publish:                                 ## Publish Python package to PyPI
	uv publish

# === CUSTOM COMMANDS ===
mcp-inspector:
	npx @modelcontextprotocol/inspector uv run python src/jupytercad_mcp/server.py
