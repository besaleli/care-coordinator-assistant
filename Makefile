.PHONY: run
run:
	docker compose up

.PHONY: build-run
build-run:
	docker compose up \
		--build \
		--force-recreate
