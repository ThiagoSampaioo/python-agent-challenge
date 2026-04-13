up:
	docker compose up -d --build

down:
	docker compose down

test:
	pytest -v