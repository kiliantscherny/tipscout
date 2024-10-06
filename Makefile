# Makefile

# Variables
DOCKER_COMPOSE = docker-compose

# Commands
.PHONY: init
init:
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up airflow-init
	$(DOCKER_COMPOSE) up -d

.PHONY: restart
restart:
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down:
	$(DOCKER_COMPOSE) down --volumes --rmi all