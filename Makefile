backend-dev:
	cd src/backend && uvicorn app.main:app --reload --port 8000

backend-test:
	cd src/backend && pytest

frontend-dev:
	cd src/frontend && npm run dev

compose-up:
	docker compose up --build

compose-down:
	docker compose down
