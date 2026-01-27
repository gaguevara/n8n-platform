# AWS Deployment Guide

## Arquitectura AWS

```
                    ┌─────────────────────────────────────────────────┐
                    │                     VPC                          │
                    │  ┌─────────────────────────────────────────────┐ │
Internet ──▶ ALB ──▶│  │            Private Subnet                   │ │
                    │  │  ┌─────────┐     ┌─────────┐                │ │
                    │  │  │   ECS   │     │   RDS   │                │ │
                    │  │  │ Fargate │────▶│ Postgres│                │ │
                    │  │  └─────────┘     └─────────┘                │ │
                    │  └─────────────────────────────────────────────┘ │
                    └─────────────────────────────────────────────────┘
```

## Prerequisitos

1. AWS CLI configurado con credenciales
2. ECR repository creado: `delcop/n8n`
3. ECS Cluster creado: `n8n-cluster`
4. RDS PostgreSQL instance
5. Secrets en Secrets Manager

## Setup Inicial

### 1. Crear ECR Repository

```bash
aws ecr create-repository \
    --repository-name delcop/n8n \
    --region us-east-1 \
    --image-scanning-configuration scanOnPush=true
```

### 2. Crear Secrets en Secrets Manager

```bash
aws secretsmanager create-secret \
    --name n8n/prod/encryption-key \
    --secret-string "$(openssl rand -hex 32)"

aws secretsmanager create-secret \
    --name n8n/prod/db-credentials \
    --secret-string '{"username":"n8n","password":"SECURE_PASSWORD"}'
```

### 3. Task Definition

```json
{
  "family": "n8n-prod",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/n8nTaskRole",
  "containerDefinitions": [
    {
      "name": "n8n",
      "image": "ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/delcop/n8n:latest",
      "portMappings": [
        {
          "containerPort": 5678,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "DB_TYPE", "value": "postgresdb"},
        {"name": "DB_POSTGRESDB_HOST", "value": "n8n-db.xxxxx.us-east-1.rds.amazonaws.com"},
        {"name": "DB_POSTGRESDB_PORT", "value": "5432"},
        {"name": "DB_POSTGRESDB_DATABASE", "value": "n8n"},
        {"name": "N8N_PROTOCOL", "value": "https"},
        {"name": "N8N_SECURE_COOKIE", "value": "true"},
        {"name": "WEBHOOK_URL", "value": "https://n8n.delcop.com/"},
        {"name": "TZ", "value": "America/Bogota"}
      ],
      "secrets": [
        {
          "name": "N8N_ENCRYPTION_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:n8n/prod/encryption-key"
        },
        {
          "name": "DB_POSTGRESDB_USER",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:n8n/prod/db-credentials:username::"
        },
        {
          "name": "DB_POSTGRESDB_PASSWORD",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:ACCOUNT:secret:n8n/prod/db-credentials:password::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/n8n-prod",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "n8n"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "wget -qO- http://localhost:5678/healthz || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### 4. Crear ECS Service

```bash
aws ecs create-service \
    --cluster n8n-cluster \
    --service-name n8n-service \
    --task-definition n8n-prod \
    --desired-count 1 \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
    --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:...,containerName=n8n,containerPort=5678"
```

## CodeCommit + CodePipeline

### buildspec.yml

```yaml
version: 0.2

phases:
  pre_build:
    commands:
      - echo Logging in to Amazon ECR...
      - aws ecr get-login-password --region $AWS_DEFAULT_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com
      - REPOSITORY_URI=$AWS_ACCOUNT_ID.dkr.ecr.$AWS_DEFAULT_REGION.amazonaws.com/delcop/n8n
      - COMMIT_HASH=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c 1-7)
      - IMAGE_TAG=${COMMIT_HASH:=latest}
  build:
    commands:
      - echo Building the Docker image...
      - docker build -t $REPOSITORY_URI:latest -f infra/Dockerfile .
      - docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG
  post_build:
    commands:
      - echo Pushing the Docker images...
      - docker push $REPOSITORY_URI:latest
      - docker push $REPOSITORY_URI:$IMAGE_TAG
      - echo Writing image definitions file...
      - printf '[{"name":"n8n","imageUri":"%s"}]' $REPOSITORY_URI:$IMAGE_TAG > imagedefinitions.json

artifacts:
  files: imagedefinitions.json
```

## Costos Estimados (us-east-1)

| Recurso | Especificación | Costo/mes |
|---------|----------------|-----------|
| ECS Fargate | 0.5 vCPU, 1GB | ~$15 |
| RDS PostgreSQL | db.t3.micro | ~$15 |
| ALB | 1 LCU promedio | ~$20 |
| ECR | 1GB storage | ~$0.10 |
| CloudWatch | Basic | ~$5 |
| **Total** | | **~$55/mes** |

## Monitoreo

### CloudWatch Alarms

```bash
# CPU High
aws cloudwatch put-metric-alarm \
    --alarm-name n8n-cpu-high \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --statistic Average \
    --period 300 \
    --threshold 80 \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:alerts

# Unhealthy Tasks
aws cloudwatch put-metric-alarm \
    --alarm-name n8n-unhealthy \
    --metric-name UnHealthyHostCount \
    --namespace AWS/ApplicationELB \
    --statistic Average \
    --period 60 \
    --threshold 1 \
    --comparison-operator GreaterThanOrEqualToThreshold \
    --evaluation-periods 2 \
    --alarm-actions arn:aws:sns:us-east-1:ACCOUNT:alerts
```

## Rollback

```bash
# Obtener revision anterior
aws ecs describe-services --cluster n8n-cluster --services n8n-service \
    --query 'services[0].deployments[?status==`PRIMARY`].taskDefinition'

# Rollback a revision específica
aws ecs update-service \
    --cluster n8n-cluster \
    --service n8n-service \
    --task-definition n8n-prod:PREVIOUS_REVISION \
    --force-new-deployment
```
