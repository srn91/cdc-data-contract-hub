.PHONY: report serve test lint verify clean

report:
	python3 -m app.cli report

serve:
	uvicorn app.main:app --host 127.0.0.1 --port 8001

test:
	pytest -q

lint:
	ruff check app tests

verify: lint test report

clean:
	rm -rf generated
