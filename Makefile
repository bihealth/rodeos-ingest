.PHONY: all
all: black

.PHONY: black
black:
	black -l 100 .

.PHONY: test
test:
	black -l 100 --check .

.PHONY: pytest
pytest:
	pytest tests

.PHONY: lint-all
lint-all: bandit pyflakes pep257 prospector

.PHONY: bandit
bandit:
	bandit -c bandit.yml -r omics_ingest

.PHONY: pyflakes
pyflakes:
	pyflakes omics_ingest tests

.PHONY: pep257
pep257:
	pep257

.PHONY: prospector
prospector:
	prospector -i src
