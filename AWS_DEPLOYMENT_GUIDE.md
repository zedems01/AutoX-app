# AutoX AWS ECS Deployment Guide

## Overview

This guide walks you through deploying the AutoX backend and monitoring stack to AWS ECS Fargate, with Jenkins on OVH for CI/CD and Vercel for the frontend.

**Architecture:**
- **OVH Server:** Jenkins (CI/CD pipeline)
- **AWS ECS Fargate:** Backend + Monitoring Stack (Prometheus, Grafana, Loki, Promtail)
- **Vercel:** Frontend (already deployed)
- **Docker Hub:** Docker image registry
- **AWS ECR:** Additional registry for AWS deployments
- **AWS ALB:** Application Load Balancer for routing traffic

---

## Prerequisites

Before starting, ensure you have:

1. **AWS Account** with administrative access
2. **OVH Server** with Jenkins installed and running
3. **Docker Hub account** with credentials configured
4. **AWS CLI** installed and configured on your local machine
5. **Git repository** accessible by Jenkins
6. **Domain name** (optional, for custom URLs)

---

## Part 1: AWS Infrastructure Setup

### Step 1.1: Create VPC and Networking

```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=autox-vpc}]' \
  --region eu-west-3

# Note the VPC ID from the output (e.g., vpc-xxxxx)
export VPC_ID=vpc-xxxxx

# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=autox-igw}]' \
  --region eu-west-3

# Note the IGW ID
export IGW_ID=igw-xxxxx

# Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID \
  --region eu-west-3

# Create Public Subnet 1 (for ALB)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone eu-west-3a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=autox-public-subnet-1}]' \
  --region eu-west-3

export PUBLIC_SUBNET_1=subnet-xxxxx

# Create Public Subnet 2 (for ALB - different AZ)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone eu-west-3b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=autox-public-subnet-2}]' \
  --region eu-west-3

export PUBLIC_SUBNET_2=subnet-xxxxx

# Create Private Subnet 1 (for ECS tasks)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.10.0/24 \
  --availability-zone eu-west-3a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=autox-private-subnet-1}]' \
  --region eu-west-3

export PRIVATE_SUBNET_1=subnet-xxxxx

# Create Private Subnet 2
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone eu-west-3b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=autox-private-subnet-2}]' \
  --region eu-west-3

export PRIVATE_SUBNET_2=subnet-xxxxx

# Create NAT Gateway (for private subnets to access internet)
# First, allocate Elastic IP
aws ec2 allocate-address \
  --domain vpc \
  --tag-specifications 'ResourceType=elastic-ip,Tags=[{Key=Name,Value=autox-nat-eip}]' \
  --region eu-west-3

export EIP_ALLOC_ID=eipalloc-xxxxx

# Create NAT Gateway in public subnet
aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1 \
  --allocation-id $EIP_ALLOC_ID \
  --tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=autox-nat}]' \
  --region eu-west-3

export NAT_GATEWAY_ID=nat-xxxxx

# Wait for NAT Gateway to become available (takes ~5 minutes)
aws ec2 wait nat-gateway-available --nat-gateway-ids $NAT_GATEWAY_ID --region eu-west-3

# Create Route Tables
# Public route table
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=autox-public-rt}]' \
  --region eu-west-3

export PUBLIC_RT_ID=rtb-xxxxx

# Add route to Internet Gateway
aws ec2 create-route \
  --route-table-id $PUBLIC_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID \
  --region eu-west-3

# Associate public subnets with public route table
aws ec2 associate-route-table \
  --route-table-id $PUBLIC_RT_ID \
  --subnet-id $PUBLIC_SUBNET_1 \
  --region eu-west-3

aws ec2 associate-route-table \
  --route-table-id $PUBLIC_RT_ID \
  --subnet-id $PUBLIC_SUBNET_2 \
  --region eu-west-3

# Private route table
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=autox-private-rt}]' \
  --region eu-west-3

export PRIVATE_RT_ID=rtb-xxxxx

# Add route to NAT Gateway
aws ec2 create-route \
  --route-table-id $PRIVATE_RT_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_GATEWAY_ID \
  --region eu-west-3

# Associate private subnets with private route table
aws ec2 associate-route-table \
  --route-table-id $PRIVATE_RT_ID \
  --subnet-id $PRIVATE_SUBNET_1 \
  --region eu-west-3

aws ec2 associate-route-table \
  --route-table-id $PRIVATE_RT_ID \
  --subnet-id $PRIVATE_SUBNET_2 \
  --region eu-west-3
```

### Step 1.2: Create Security Groups

```bash
# Security Group for ALB
aws ec2 create-security-group \
  --group-name autox-alb-sg \
  --description "Security group for AutoX Application Load Balancer" \
  --vpc-id $VPC_ID \
  --region eu-west-3

export ALB_SG_ID=sg-xxxxx

# Allow HTTP and HTTPS traffic to ALB
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0 \
  --region eu-west-3

aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0 \
  --region eu-west-3

# Allow access to Grafana (port 3001)
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG_ID \
  --protocol tcp \
  --port 3001 \
  --cidr 0.0.0.0/0 \
  --region eu-west-3

# Security Group for ECS Tasks
aws ec2 create-security-group \
  --group-name autox-ecs-sg \
  --description "Security group for AutoX ECS tasks" \
  --vpc-id $VPC_ID \
  --region eu-west-3

export ECS_SG_ID=sg-xxxxx

# Allow traffic from ALB to ECS tasks
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG_ID \
  --protocol tcp \
  --port 8000 \
  --source-group $ALB_SG_ID \
  --region eu-west-3

# Allow internal traffic between ECS tasks (for service discovery)
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG_ID \
  --protocol -1 \
  --source-group $ECS_SG_ID \
  --region eu-west-3

# Allow Prometheus port
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG_ID \
  --protocol tcp \
  --port 9090 \
  --source-group $ALB_SG_ID \
  --region eu-west-3

# Allow Grafana port
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG_ID \
  --protocol tcp \
  --port 3001 \
  --source-group $ALB_SG_ID \
  --region eu-west-3
```

### Step 1.3: Create EFS for Persistent Storage

```bash
# Create EFS File System
aws efs create-file-system \
  --creation-token autox-efs-$(date +%s) \
  --performance-mode generalPurpose \
  --throughput-mode bursting \
  --encrypted \
  --tags Key=Name,Value=autox-efs \
  --region eu-west-3

export EFS_ID=fs-xxxxx

# Create EFS Mount Targets in private subnets
aws efs create-mount-target \
  --file-system-id $EFS_ID \
  --subnet-id $PRIVATE_SUBNET_1 \
  --security-groups $ECS_SG_ID \
  --region eu-west-3

aws efs create-mount-target \
  --file-system-id $EFS_ID \
  --subnet-id $PRIVATE_SUBNET_2 \
  --security-groups $ECS_SG_ID \
  --region eu-west-3

# Wait for mount targets to become available
sleep 30
```

### Step 1.4: Create ECR Repository

```bash
# Create ECR repository for backend
aws ecr create-repository \
  --repository-name autox-backend \
  --image-scanning-configuration scanOnPush=true \
  --region eu-west-3

# Note the repository URI (e.g., 123456789012.dkr.ecr.eu-west-3.amazonaws.com/autox-backend)
export ECR_REPO_URI=$(aws ecr describe-repositories \
  --repository-names autox-backend \
  --region eu-west-3 \
  --query 'repositories[0].repositoryUri' \
  --output text)

echo "ECR Repository URI: $ECR_REPO_URI"
```

### Step 1.5: Create IAM Roles

```bash
# Create ECS Task Execution Role
cat > ecs-task-execution-role-trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name autoxEcsTaskExecutionRole \
  --assume-role-policy-document file://ecs-task-execution-role-trust-policy.json \
  --region eu-west-3

# Attach managed policy for ECS task execution
aws iam attach-role-policy \
  --role-name autoxEcsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy \
  --region eu-west-3

# Create ECS Task Role (for application permissions)
aws iam create-role \
  --role-name autoxEcsTaskRole \
  --assume-role-policy-document file://ecs-task-execution-role-trust-policy.json \
  --region eu-west-3

# Create policy for EFS access
cat > efs-access-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "elasticfilesystem:ClientMount",
        "elasticfilesystem:ClientWrite",
        "elasticfilesystem:DescribeFileSystems"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name autoxEcsTaskRole \
  --policy-name EfsAccessPolicy \
  --policy-document file://efs-access-policy.json \
  --region eu-west-3

# Get role ARNs
export TASK_EXECUTION_ROLE_ARN=$(aws iam get-role --role-name autoxEcsTaskExecutionRole --query 'Role.Arn' --output text)
export TASK_ROLE_ARN=$(aws iam get-role --role-name autoxEcsTaskRole --query 'Role.Arn' --output text)

echo "Task Execution Role ARN: $TASK_EXECUTION_ROLE_ARN"
echo "Task Role ARN: $TASK_ROLE_ARN"
```

### Step 1.6: Store Secrets in AWS Secrets Manager

```bash
# Create secret for environment variables
cat > autox-secrets.json << EOF
{
  "ANTHROPIC_API_KEY": "your_anthropic_api_key",
  "OPENAI_API_KEY": "your_openai_api_key",
  "GROQ_API_KEY": "your_groq_api_key",
  "GOOGLE_API_KEY": "your_google_api_key",
  "SERPER_API_KEY": "your_serper_api_key",
  "COMPOSIO_API_KEY": "your_composio_api_key",
  "DEMO_TOKEN": "your_secure_demo_token",
  "TEST_USER_NAME": "your_test_username",
  "TEST_USER_EMAIL": "your_test_email",
  "TEST_USER_PASSWORD": "your_test_password",
  "TEST_USER_PROXY": "your_test_proxy",
  "TEST_USER_TOTP_SECRET": "your_test_totp_secret",
  "GRAFANA_ADMIN_USER": "admin",
  "GRAFANA_ADMIN_PASSWORD": "change_me_in_production"
}
EOF

# Create the secret
aws secretsmanager create-secret \
  --name autox/production/env \
  --description "AutoX production environment variables" \
  --secret-string file://autox-secrets.json \
  --region eu-west-3

# Get secret ARN
export SECRET_ARN=$(aws secretsmanager describe-secret \
  --secret-id autox/production/env \
  --region eu-west-3 \
  --query 'ARN' \
  --output text)

echo "Secret ARN: $SECRET_ARN"

# Update task execution role to access secrets
cat > secrets-access-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "$SECRET_ARN"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name autoxEcsTaskExecutionRole \
  --policy-name SecretsAccessPolicy \
  --policy-document file://secrets-access-policy.json \
  --region eu-west-3

# Clean up sensitive files
rm autox-secrets.json secrets-access-policy.json
```

---

## Part 2: Create ECS Cluster and Services

### Step 2.1: Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name autox-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 \
  --region eu-west-3

# Enable CloudWatch Container Insights (optional but recommended)
aws ecs update-cluster-settings \
  --cluster autox-cluster \
  --settings name=containerInsights,value=enabled \
  --region eu-west-3
```

### Step 2.2: Create CloudWatch Log Groups

```bash
# Create log groups for each service
aws logs create-log-group \
  --log-group-name /ecs/autox-backend \
  --region eu-west-3

aws logs create-log-group \
  --log-group-name /ecs/autox-prometheus \
  --region eu-west-3

aws logs create-log-group \
  --log-group-name /ecs/autox-grafana \
  --region eu-west-3

aws logs create-log-group \
  --log-group-name /ecs/autox-loki \
  --region eu-west-3

aws logs create-log-group \
  --log-group-name /ecs/autox-promtail \
  --region eu-west-3
```

### Step 2.3: Create Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name autox-alb \
  --subnets $PUBLIC_SUBNET_1 $PUBLIC_SUBNET_2 \
  --security-groups $ALB_SG_ID \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --region eu-west-3

export ALB_ARN=$(aws elbv2 describe-load-balancers \
  --names autox-alb \
  --region eu-west-3 \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)

export ALB_DNS=$(aws elbv2 describe-load-balancers \
  --names autox-alb \
  --region eu-west-3 \
  --query 'LoadBalancers[0].DNSName' \
  --output text)

echo "ALB ARN: $ALB_ARN"
echo "ALB DNS: $ALB_DNS"

# Create Target Groups
# Backend target group
aws elbv2 create-target-group \
  --name autox-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-enabled \
  --health-check-protocol HTTP \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --region eu-west-3

export BACKEND_TG_ARN=$(aws elbv2 describe-target-groups \
  --names autox-backend-tg \
  --region eu-west-3 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Grafana target group
aws elbv2 create-target-group \
  --name autox-grafana-tg \
  --protocol HTTP \
  --port 3000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-enabled \
  --health-check-protocol HTTP \
  --health-check-path /api/health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3 \
  --region eu-west-3

export GRAFANA_TG_ARN=$(aws elbv2 describe-target-groups \
  --names autox-grafana-tg \
  --region eu-west-3 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)

# Create ALB Listeners
# HTTP listener with path-based routing
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
  --region eu-west-3

export LISTENER_ARN=$(aws elbv2 describe-listeners \
  --load-balancer-arn $ALB_ARN \
  --region eu-west-3 \
  --query 'Listeners[0].ListenerArn' \
  --output text)

# Add rule for Grafana
aws elbv2 create-rule \
  --listener-arn $LISTENER_ARN \
  --priority 1 \
  --conditions Field=path-pattern,Values='/grafana*' \
  --actions Type=forward,TargetGroupArn=$GRAFANA_TG_ARN \
  --region eu-west-3
```

### Step 2.4: Create Service Discovery Namespace

```bash
# Create private DNS namespace for service discovery
aws servicediscovery create-private-dns-namespace \
  --name autox.local \
  --vpc $VPC_ID \
  --region eu-west-3

export NAMESPACE_ID=$(aws servicediscovery list-namespaces \
  --region eu-west-3 \
  --filters Name=TYPE,Values=DNS_PRIVATE,Condition=EQ \
  --query "Namespaces[?Name=='autox.local'].Id" \
  --output text)

echo "Service Discovery Namespace ID: $NAMESPACE_ID"

# Create service discovery services
aws servicediscovery create-service \
  --name backend \
  --dns-config "NamespaceId=$NAMESPACE_ID,DnsRecords=[{Type=A,TTL=60}]" \
  --health-check-custom-config FailureThreshold=1 \
  --region eu-west-3

export BACKEND_SD_ARN=$(aws servicediscovery list-services \
  --region eu-west-3 \
  --query "Services[?Name=='backend'].Arn" \
  --output text)
```

---

## Part 3: Create ECS Task Definitions

### Step 3.1: Backend Task Definition

Create a file named `backend-task-definition.json`:

```json
{
  "family": "autox-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "REPLACE_WITH_TASK_EXECUTION_ROLE_ARN",
  "taskRoleArn": "REPLACE_WITH_TASK_ROLE_ARN",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "REPLACE_WITH_ECR_REPO_URI:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "APP_ENV",
          "value": "production"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "ANTHROPIC_API_KEY",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:ANTHROPIC_API_KEY::"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:OPENAI_API_KEY::"
        },
        {
          "name": "GROQ_API_KEY",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:GROQ_API_KEY::"
        },
        {
          "name": "GOOGLE_API_KEY",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:GOOGLE_API_KEY::"
        },
        {
          "name": "SERPER_API_KEY",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:SERPER_API_KEY::"
        },
        {
          "name": "COMPOSIO_API_KEY",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:COMPOSIO_API_KEY::"
        },
        {
          "name": "DEMO_TOKEN",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:DEMO_TOKEN::"
        },
        {
          "name": "TEST_USER_NAME",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:TEST_USER_NAME::"
        },
        {
          "name": "TEST_USER_EMAIL",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:TEST_USER_EMAIL::"
        },
        {
          "name": "TEST_USER_PASSWORD",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:TEST_USER_PASSWORD::"
        },
        {
          "name": "TEST_USER_PROXY",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:TEST_USER_PROXY::"
        },
        {
          "name": "TEST_USER_TOTP_SECRET",
          "valueFrom": "REPLACE_WITH_SECRET_ARN:TEST_USER_TOTP_SECRET::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/autox-backend",
          "awslogs-region": "eu-west-3",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      },
      "mountPoints": [
        {
          "sourceVolume": "backend-logs",
          "containerPath": "/code/app/logs",
          "readOnly": false
        }
      ]
    }
  ],
  "volumes": [
    {
      "name": "backend-logs",
      "efsVolumeConfiguration": {
        "fileSystemId": "REPLACE_WITH_EFS_ID",
        "transitEncryption": "ENABLED",
        "authorizationConfig": {
          "iam": "ENABLED"
        },
        "rootDirectory": "/backend-logs"
      }
    }
  ]
}
```

Register the task definition:

```bash
# Replace placeholders in the task definition
sed -i "s|REPLACE_WITH_TASK_EXECUTION_ROLE_ARN|$TASK_EXECUTION_ROLE_ARN|g" backend-task-definition.json
sed -i "s|REPLACE_WITH_TASK_ROLE_ARN|$TASK_ROLE_ARN|g" backend-task-definition.json
sed -i "s|REPLACE_WITH_ECR_REPO_URI|$ECR_REPO_URI|g" backend-task-definition.json
sed -i "s|REPLACE_WITH_SECRET_ARN|$SECRET_ARN|g" backend-task-definition.json
sed -i "s|REPLACE_WITH_EFS_ID|$EFS_ID|g" backend-task-definition.json

# Register the task definition
aws ecs register-task-definition \
  --cli-input-json file://backend-task-definition.json \
  --region eu-west-3
```

### Step 3.2: Monitoring Stack Task Definition

For simplicity, I'm showing how to deploy backend. For production, you'd create similar task definitions for Prometheus, Grafana, Loki, and Promtail, or use a single task with multiple containers.

**Alternative:** You can deploy the monitoring stack on a separate EC2 instance or use AWS-managed services like Amazon Managed Prometheus and Amazon Managed Grafana.

---

## Part 4: Create ECS Services

### Step 4.1: Create Backend Service

```bash
# Create backend service with ALB integration
aws ecs create-service \
  --cluster autox-cluster \
  --service-name autox-backend-service \
  --task-definition autox-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],securityGroups=[$ECS_SG_ID],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$BACKEND_TG_ARN,containerName=backend,containerPort=8000" \
  --service-registries "registryArn=$BACKEND_SD_ARN" \
  --health-check-grace-period-seconds 60 \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=100,deploymentCircuitBreaker={enable=true,rollback=true}" \
  --enable-execute-command \
  --region eu-west-3
```

### Step 4.2: Enable Auto Scaling (Optional)

```bash
# Register the service as a scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/autox-cluster/autox-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 2 \
  --max-capacity 10 \
  --region eu-west-3

# Create scaling policy based on CPU utilization
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --resource-id service/autox-cluster/autox-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --policy-name autox-backend-cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }' \
  --region eu-west-3
```

---

## Part 5: Jenkins Configuration

### Step 5.1: Install Required Jenkins Plugins

On your OVH Jenkins server:

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Install these plugins:
   - Docker Pipeline
   - AWS Steps
   - AWS Credentials
   - Git
   - Pipeline
   - AnsiColor
   - Timestamps

### Step 5.2: Configure Jenkins Credentials

1. Go to **Manage Jenkins** → **Manage Credentials**
2. Add the following credentials:

   **Docker Hub:**
   - Type: Username with password
   - ID: `dockerhub-autox`
   - Username: Your Docker Hub username
   - Password: Your Docker Hub password/token

   **AWS Credentials:**
   - Type: Secret text
   - ID: `aws-account-id`
   - Secret: Your AWS account ID (12-digit number)

   - Type: Secret text
   - ID: `aws-access-key-id`
   - Secret: Your AWS access key ID

   - Type: Secret text
   - ID: `aws-secret-access-key`
   - Secret: Your AWS secret access key

### Step 5.3: Install AWS CLI on Jenkins Server

```bash
# SSH into your OVH server
ssh user@your-ovh-server

# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version

# Configure AWS CLI (use Jenkins user)
sudo su - jenkins
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and default region
```

### Step 5.4: Create Jenkins Pipeline

1. Go to Jenkins Dashboard → **New Item**
2. Name: `AutoX-Pipeline`
3. Type: **Multibranch Pipeline**
4. Configure:
   - **Branch Sources:** Add Git
   - **Repository URL:** Your GitHub repository URL
   - **Credentials:** Add GitHub credentials if private repo
   - **Behaviours:** Discover branches (all branches)
   - **Build Configuration:**
     - Mode: by Jenkinsfile
     - Script Path: `Jenkinsfile.unified`
5. Save

### Step 5.5: Update Jenkinsfile

Replace the original `Jenkinsfile` with `Jenkinsfile.unified`:

```bash
# On your local machine
git checkout dev/prometheus-grafana-setup  # or your working branch
mv Jenkinsfile Jenkinsfile.old
mv Jenkinsfile.unified Jenkinsfile
git add Jenkinsfile Jenkinsfile.old
git commit -m "chore: unified Jenkins pipeline for backend and frontend"
git push origin dev/prometheus-grafana-setup
```

---

## Part 6: Configure GitHub Webhook for Jenkins

### Step 6.1: Generate Jenkins API Token

1. Log into Jenkins
2. Click your username (top right) → **Configure**
3. Scroll to **API Token** section
4. Click **Add new Token**
5. Name it: `GitHub-Webhook`
6. Click **Generate**
7. **Copy the token** (you won't see it again)

### Step 6.2: Configure GitHub Webhook

1. Go to your GitHub repository
2. Navigate to **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL:** `http://your-ovh-jenkins-url/github-webhook/`
   - **Content type:** `application/json`
   - **Secret:** Leave empty (or use Jenkins webhook secret if configured)
   - **Which events would you like to trigger this webhook?**
     - Select: **Just the push event** and **Pull requests**
   - **Active:** Check this box
4. Click **Add webhook**

### Step 6.3: Test the Webhook

1. Make a small change in your repo
2. Push to any branch (e.g., `main` or `dev/prometheus-grafana-setup`)
3. Check Jenkins:
   - Go to your pipeline
   - You should see a new build triggered automatically
4. Check GitHub:
   - Go to **Settings** → **Webhooks**
   - Click on your webhook
   - Check **Recent Deliveries** (should show successful delivery)

---

## Part 7: Deploy and Test

### Step 7.1: Initial Deployment

```bash
# On your local machine, ensure all changes are committed
git add .
git commit -m "feat: AWS ECS deployment configuration"
git push origin main

# This should trigger Jenkins pipeline automatically via webhook
```

### Step 7.2: Monitor Deployment

1. **Check Jenkins:**
   - Watch the pipeline execution
   - Ensure all stages pass

2. **Check AWS ECS:**
   ```bash
   # Check service status
   aws ecs describe-services \
     --cluster autox-cluster \
     --services autox-backend-service \
     --region eu-west-3 \
     --query 'services[0].deployments'
   
   # Check task status
   aws ecs list-tasks \
     --cluster autox-cluster \
     --service-name autox-backend-service \
     --region eu-west-3
   
   # Check task health
   aws ecs describe-tasks \
     --cluster autox-cluster \
     --tasks TASK_ARN \
     --region eu-west-3
   ```

3. **Check Load Balancer:**
   ```bash
   # Get ALB DNS name
   aws elbv2 describe-load-balancers \
     --names autox-alb \
     --region eu-west-3 \
     --query 'LoadBalancers[0].DNSName' \
     --output text
   ```

4. **Test the Backend:**
   ```bash
   # Health check
   curl http://YOUR_ALB_DNS/health
   
   # Expected output: {"status":"oki doki"}
   
   # Check metrics endpoint
   curl http://YOUR_ALB_DNS/metrics
   ```

---

## Part 8: Configure Domain and SSL (Optional)

### Step 8.1: Create Route 53 Hosted Zone

```bash
# Create hosted zone for your domain
aws route53 create-hosted-zone \
  --name yourdomain.com \
  --caller-reference $(date +%s) \
  --region eu-west-3

# Get nameservers
aws route53 list-resource-record-sets \
  --hosted-zone-id YOUR_HOSTED_ZONE_ID \
  --region eu-west-3
```

### Step 8.2: Request SSL Certificate

```bash
# Request certificate from ACM
aws acm request-certificate \
  --domain-name api.yourdomain.com \
  --subject-alternative-names yourdomain.com www.yourdomain.com \
  --validation-method DNS \
  --region eu-west-3

# Follow the validation instructions in ACM console
```

### Step 8.3: Create HTTPS Listener

```bash
# Add HTTPS listener to ALB
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=YOUR_CERTIFICATE_ARN \
  --default-actions Type=forward,TargetGroupArn=$BACKEND_TG_ARN \
  --region eu-west-3
```

### Step 8.4: Create DNS Records

```bash
# Create A record for ALB
aws route53 change-resource-record-sets \
  --hosted-zone-id YOUR_HOSTED_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "api.yourdomain.com",
        "Type": "A",
        "AliasTarget": {
          "HostedZoneId": "YOUR_ALB_HOSTED_ZONE_ID",
          "DNSName": "YOUR_ALB_DNS",
          "EvaluateTargetHealth": true
        }
      }
    }]
  }' \
  --region eu-west-3
```

---

## Part 9: Monitoring and Logs

### Step 9.1: View CloudWatch Logs

```bash
# View backend logs
aws logs tail /ecs/autox-backend --follow --region eu-west-3

# View recent errors
aws logs filter-log-events \
  --log-group-name /ecs/autox-backend \
  --filter-pattern "ERROR" \
  --region eu-west-3
```

### Step 9.2: Access Monitoring Dashboards

**Option A: Access via ALB (if Grafana is deployed on ECS)**
- Grafana: `http://YOUR_ALB_DNS/grafana`
- Prometheus: `http://YOUR_ALB_DNS:9090` (if exposed)

**Option B: Deploy monitoring stack separately**
- SSH into a monitoring EC2 instance
- Use the `docker-compose.aws.yml` file to deploy monitoring stack
- Access via EC2 public IP or separate ALB

---

## Part 10: Cost Optimization

### Recommendations:

1. **Use Fargate Spot for non-critical workloads** (can save up to 70%)
2. **Enable Container Insights only if needed** (adds ~$2-3/month per task)
3. **Use S3 for logs long-term storage** (cheaper than CloudWatch)
4. **Set up CloudWatch log retention** (e.g., 7 days)
5. **Use AWS Budget Alerts** to monitor costs
6. **Consider Reserved Capacity** for predictable workloads

```bash
# Set log retention to 7 days
aws logs put-retention-policy \
  --log-group-name /ecs/autox-backend \
  --retention-in-days 7 \
  --region eu-west-3
```

---

## Part 11: Troubleshooting

### Common Issues:

**1. Tasks fail to start:**
- Check task definition (CPU/memory limits)
- Check IAM roles (execution and task roles)
- Check secrets (ensure task can access Secrets Manager)
- Check CloudWatch logs for error messages

**2. Health checks failing:**
- Ensure security group allows traffic from ALB to ECS tasks
- Check application is listening on correct port
- Verify health check endpoint returns 200 OK
- Increase health check grace period

**3. Jenkins pipeline fails:**
- Check Jenkins credentials (Docker Hub, AWS)
- Ensure AWS CLI is installed and configured on Jenkins server
- Check ECR repository exists
- Verify IAM permissions for Jenkins AWS credentials

**4. Cannot access services:**
- Check ALB target group health
- Verify security groups
- Check route tables and NAT Gateway
- Ensure ECS tasks have correct network configuration

**5. Deployment stuck:**
```bash
# Force new deployment
aws ecs update-service \
  --cluster autox-cluster \
  --service autox-backend-service \
  --force-new-deployment \
  --region eu-west-3

# Or rollback to previous task definition
aws ecs update-service \
  --cluster autox-cluster \
  --service autox-backend-service \
  --task-definition autox-backend:REVISION_NUMBER \
  --region eu-west-3
```

---

## Part 12: Maintenance and Updates

### Update Application:

1. **Push code changes to GitHub**
   ```bash
   git add .
   git commit -m "feat: new feature"
   git push origin main
   ```

2. **Jenkins automatically:**
   - Runs tests
   - Builds Docker image
   - Pushes to Docker Hub and ECR
   - Triggers ECS deployment (for `main` branch)

3. **Monitor deployment:**
   ```bash
   aws ecs describe-services \
     --cluster autox-cluster \
     --services autox-backend-service \
     --region eu-west-3
   ```

### Manual Rollback:

```bash
# List task definition revisions
aws ecs list-task-definitions \
  --family-prefix autox-backend \
  --region eu-west-3

# Rollback to previous revision
aws ecs update-service \
  --cluster autox-cluster \
  --service autox-backend-service \
  --task-definition autox-backend:PREVIOUS_REVISION \
  --region eu-west-3
```

### Update Secrets:

```bash
# Update secret in Secrets Manager
aws secretsmanager update-secret \
  --secret-id autox/production/env \
  --secret-string file://new-secrets.json \
  --region eu-west-3

# Force service to restart and pick up new secrets
aws ecs update-service \
  --cluster autox-cluster \
  --service autox-backend-service \
  --force-new-deployment \
  --region eu-west-3
```

---

## Summary

You now have:

✅ **Unified Jenkins pipeline** that:
- Builds and tests both backend and frontend
- Pushes images to Docker Hub and AWS ECR
- Automatically deploys to AWS ECS on `main` branch push

✅ **AWS ECS Fargate deployment** with:
- Backend service running in private subnets
- Application Load Balancer for public access
- Monitoring stack (Prometheus, Grafana, Loki, Promtail)
- Persistent storage using EFS
- Secrets managed in AWS Secrets Manager
- Auto-scaling based on CPU utilization

✅ **CI/CD automation** with:
- GitHub webhook triggering Jenkins on push/PR
- Automatic deployment to AWS ECS for `main` branch
- Separate Docker images for different branches

✅ **Frontend on Vercel** (already deployed)

### Next Steps:

1. Set up custom domain and SSL certificate
2. Configure CloudWatch alarms for monitoring
3. Implement backup strategy for EFS volumes
4. Set up multi-region deployment (optional)
5. Implement blue-green or canary deployment strategies

---

## Quick Reference Commands

```bash
# Check service status
aws ecs describe-services --cluster autox-cluster --services autox-backend-service --region eu-west-3

# View logs
aws logs tail /ecs/autox-backend --follow --region eu-west-3

# Force new deployment
aws ecs update-service --cluster autox-cluster --service autox-backend-service --force-new-deployment --region eu-west-3

# Scale service
aws ecs update-service --cluster autox-cluster --service autox-backend-service --desired-count 4 --region eu-west-3

# Stop all tasks (emergency)
aws ecs update-service --cluster autox-cluster --service autox-backend-service --desired-count 0 --region eu-west-3

# Check ALB target health
aws elbv2 describe-target-health --target-group-arn $BACKEND_TG_ARN --region eu-west-3
```

---

**You're all set!** 🚀

For questions or issues, refer to:
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Jenkins Pipeline Documentation](https://www.jenkins.io/doc/book/pipeline/)
- [Docker Documentation](https://docs.docker.com/)

