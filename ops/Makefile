REGISTRY=registry.local:5000/delcop
IMAGE=$(REGISTRY)/n8n
TAG?=dev-$(shell date +%Y%m%d%H%M)

build:
	docker build -t $(IMAGE):$(TAG) -f infra/Dockerfile .

run-local:
	docker compose -f infra/docker-compose.local.yml up --build -d

push:
	docker push $(IMAGE):$(TAG)
	docker tag $(IMAGE):$(TAG) $(IMAGE):latest
	docker push $(IMAGE):latest

deploy-staging:
	ssh usuario@staging-host "export TAG=$(TAG); cd /srv/n8n-platform/infra && \
	  docker login registry.local:5000 && \
	  docker compose -f docker-compose.staging.yml pull && \
	  docker compose -f docker-compose.staging.yml up -d --remove-orphans"

logs-staging:
	ssh usuario@staging-host "cd /srv/n8n-platform/infra && docker compose -f docker-compose.staging.yml logs -f"
