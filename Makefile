.PHONY: run
run:
	docker compose up

.PHONY: build-run
build-run:
	docker compose up \
		--build \
		--force-recreate

.PHONY: lock
lock:
	poetry lock -C care-ml && \
	poetry lock -C care-app
