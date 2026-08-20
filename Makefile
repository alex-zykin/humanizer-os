.PHONY: install test coverage lint format typecheck eval docs selfcheck release-check build smoke clean all

install:
	python -m pip install -e ".[dev]"

test:
	pytest -q

coverage:
	pytest --cov=humanizer_os --cov-report=term-missing --cov-report=xml

lint:
	ruff check .

format:
	ruff format .
	ruff check --fix .

typecheck:
	mypy src/humanizer_os

eval:
	python scripts/evaluate.py

docs:
	python scripts/check_docs.py
	python scripts/generate_rule_catalog.py --check

selfcheck:
	humanizer-os audit \
		README.md SKILL.md CHANGELOG.md CODE_OF_CONDUCT.md CONTRIBUTING.md SECURITY.md SUPPORT.md \
		THIRD_PARTY_NOTICES.md docs skills/humanizer-os-en/SKILL.md \
		--lang en --genre docs --fail-on warning
	humanizer-os audit README.ru.md skills/humanizer-os-ru/SKILL.md \
		--lang ru --genre docs --fail-on warning

release-check:
	python scripts/check_release.py

build:
	python -m build

smoke: build
	python -m venv /tmp/humanizer-os-smoke
	/tmp/humanizer-os-smoke/bin/python -m pip install --force-reinstall dist/*.whl
	/tmp/humanizer-os-smoke/bin/humanizer-os --version
	/tmp/humanizer-os-smoke/bin/python -m pip check

clean:
	rm -rf build dist .pytest_cache .mypy_cache .ruff_cache htmlcov coverage.xml .coverage

all: lint typecheck coverage eval docs selfcheck release-check build
