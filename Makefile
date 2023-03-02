#--- SETUP --------------------------------#

SHELL := /bin/bash

# get all positional arguments passed to make (except the first one, i.e the
# target) and passed them as arguments to the target
RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
# ...and turn them into do-nothing targets
$(eval $(RUN_ARGS):;@:)

.PHONY: echo
echo:
	echo '-> ' $(RUN_ARGS)

.PHONY: format
format:
	docker compose -f docker/docker-compose.local.yml exec api python -m black .
	docker compose -f docker/docker-compose.local.yml exec api python -m isort .


#--- TEST --------------------------------#

.PHONY: run-test
run-test: stop clean
	docker compose -f docker/docker-compose.local.test.yml up -d api
	docker compose -f docker/docker-compose.local.test.yml logs -f


#--- LOCAL -------------------------------#

.PHONY: build
build:
	docker compose -f docker/docker-compose.local.yml build
	docker compose -f docker/docker-compose.local.test.yml build

.PHONY: build-no-cache
build-no-cache:
	docker compose -f docker/docker-compose.local.yml build --no-cache
	docker compose -f docker/docker-compose.local.test.yml build --no-cache

.PHONY: exec-sh
exec-sh:
	docker compose -f docker/docker-compose.local.yml exec api /bin/sh

.PHONY: run
run: run-services run-mc-setup

.PHONY: run-services
run-services:
	docker compose -f docker/docker-compose.local.yml up -d

.PHONY: run-mc-setup
run-mc-setup:
	docker compose -f docker/docker-compose.local.yml exec minio mc mb local/csvs || true
	docker compose -f docker/docker-compose.local.yml exec minio mc anonymous set download local/csvs || true
	docker compose -f docker/docker-compose.local.yml exec minio mc anonymous links local/csvs || true
	docker compose -f docker/docker-compose.local.yml exec minio mc mb local/plots || true
	docker compose -f docker/docker-compose.local.yml exec minio mc anonymous set download local/plots || true
	docker compose -f docker/docker-compose.local.yml exec minio mc anonymous links local/plots || true

.PHONY: api-ipython
api-ipython: docker-run-other
	docker compose -f docker/docker-compose.local.yml exec -w /app/ath/ api ipython

.PHONY: logs
logs:
	docker compose -f docker/docker-compose.local.yml logs -f

.PHONY: logs-api
logs-api:
	docker compose -f docker/docker-compose.local.yml logs -f api

.PHONY: stop
stop:
	docker compose -f docker/docker-compose.local.test.yml down || true
	docker compose -f docker/docker-compose.local.yml down || true

.PHONY: stop-api
stop-api:
	docker compose -f docker/docker-compose.local.yml rm -svf api


#--- DB -------------------------------#

.PHONY: alembic-revision
alembic-revision:
	docker compose -f docker/docker-compose.local.yml exec api python -m alembic.config revision --autogenerate -m '$(RUN_ARGS)'

.PHONY: alembic-upgrade-head
alembic-upgrade-head:
	docker compose -f docker/docker-compose.local.yml exec api python -m alembic.config upgrade head

.PHONY: alembic-upgrade
alembic-upgrade:
	docker compose -f docker/docker-compose.local.yml exec api python -m alembic.config upgrade +1

.PHONY: alembic-downgrade
alembic-downgrade:
	docker compose -f docker/docker-compose.local.yml exec api python -m alembic.config downgrade -1

.PHONY: alembic-current
alembic-current:
	docker compose -f docker/docker-compose.local.yml exec api python -m alembic.config current

.PHONY: alembic-history
alembic-history:
	docker compose -f docker/docker-compose.local.yml exec api python -m alembic.config history


#--- CLI ----------------------------------#

.PHONY: cli-upload-csv
cli-upload-csv:
	docker-compose -f docker/docker-compose.local.yml exec api python -m cli upload --csv-file '$(RUN_ARGS)'


#--- TEARDOWN -----------------------------#

.PHONY: clean
clean: clean-files clean-volumes

.PHONY: clean-files
clean-files:
	find . \( -name __pycache__ -o -name "*.pyc" -o -name .pytest_cache -o -name .mypy_cache \) -exec rm -rf {} +

.PHONY: clean-volumes
clean-volumes:
	docker volume rm -f docker_local_postgres_data docker_local_test_postgres_data docker_local_minio_data docker_local_tusd_data

