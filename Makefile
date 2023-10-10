.PHONY: start
start:
	uvicorn main:api --reload --port 8080 --host 0.0.0.0

.PHONY: format
format:
	black .
	isort .