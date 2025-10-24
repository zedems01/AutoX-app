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
  --tag-specifications ResourceType=vpc,Tags=[{Key=Name,Value=autox-vpc}] \
  --region eu-west-3

# Note the VPC ID from the output (e.g., vpc-xxxxx)
export VPC_ID=vpc-xxxxx

# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications ResourceType=internet-gateway,Tags=[{Key=Name,Value=autox-igw}] \
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
  --tag-specifications ResourceType=subnet,Tags=[{Key=Name,Value=autox-public-subnet-1}] \
  --region eu-west-3

export PUBLIC_SUBNET_1=subnet-xxxxx

# Create Public Subnet 2 (for ALB - different AZ)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone eu-west-3b \
  --tag-specifications ResourceType=subnet,Tags=[{Key=Name,Value=autox-public-subnet-2}] \
  --region eu-west-3

export PUBLIC_SUBNET_2=subnet-xxxxx

# Create Private Subnet 1 (for ECS tasks)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.10.0/24 \
  --availability-zone eu-west-3a \
  --tag-specifications ResourceType=subnet,Tags=[{Key=Name,Value=autox-private-subnet-1}] \
  --region eu-west-3

export PRIVATE_SUBNET_1=subnet-xxxxx

# Create Private Subnet 2
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone eu-west-3b \
  --tag-specifications ResourceType=subnet,Tags=[{Key=Name,Value=autox-private-subnet-2}] \
  --region eu-west-3

export PRIVATE_SUBNET_2=subnet-xxxxx

# Create NAT Gateway (for private subnets to access internet)
# First, allocate Elastic IP
aws ec2 allocate-address \
  --domain vpc \
  --tag-specifications ResourceType=elastic-ip,Tags=[{Key=Name,Value=autox-nat-eip}] \
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
  --tag-specifications ResourceType=route-table,Tags=[{Key=Name,Value=autox-public-rt}] \
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

# aws ec2 associate-route-table --route-table-id $PUBLIC_RT_ID --subnet-id $PUBLIC_SUBNET_1 --region eu-west-3

aws ec2 associate-route-table \
  --route-table-id $PUBLIC_RT_ID \
  --subnet-id $PUBLIC_SUBNET_2 \
  --region eu-west-3

# Private route table
aws ec2 create-route-table \
  --vpc-id $VPC_ID \
  --tag-specifications ResourceType=route-table,Tags=[{Key=Name,Value=autox-private-rt}] \
  --region eu-west-3

# aws ec2 create-route-table --vpc-id vpc-0472bf980ee52dcff --tag-specifications ResourceType=route-table,Tags=[{Key=Name,Value=autox-private-rt}] --region eu-west-3

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

# aws ec2 authorize-security-group-ingress --group-id sg-09a7046e7a1b2b7a7 --protocol tcp --port 80 --cidr 0.0.0.0/0 --region eu-west-3

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

# aws ec2 authorize-security-group-ingress --group-id sg-067ca9c7a97d8c38d --protocol tcp --port 8000 --source-group sg-09a7046e7a1b2b7a7 --region eu-west-3

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

# aws efs create-file-system --creation-token autox-efs-$(date +%s) --performance-mode generalPurpose --throughput-mode bursting --encrypted --tags Key=Name,Value=autox-efs --region eu-west-3

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

# aws efs create-mount-target --file-system-id fs-0be9d512838a932d1 --subnet-id subnet-0f652746ad52b3c12 --security-groups sg-067ca9c7a97d8c38d --region eu-west-3

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
  "GEMINI_API_KEY": "",
  "OPENROUTER_API_KEY": "",
  "OPENAI_API_KEY": "",
  "LANGSMITH_TRACING": true,
  "LANGSMITH_API_KEY": "",
  "X_API_KEY": "",
  "TEST_USER_EMAIL": "",
  "TEST_USER_PASSWORD": "",
  "TEST_USER_PROXY": "",
  "TEST_USER_TOTP_SECRET": "",
  "DEMO_TOKEN": "",
  "AWS_ACCESS_KEY_ID": "",
  "AWS_SECRET_ACCESS_KEY": "",
  "GRAFANA_ADMIN_USER": "",
  "GRAFANA_ADMIN_PASSWORD": ""
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
  --default-capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1 \
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
          "name": "......",
          "valueFrom": "........."
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

Create a file named `monitoring-stack-task-definition.json` (this file is already provided in the repository):

This task definition includes all monitoring components in a single task:
- Prometheus (metrics collection)
- Grafana (visualization)
- Loki (log aggregation)
- Promtail (log shipping)

**Important:** Before registering, you need to upload all your monitoring configurations to EFS.

#### Upload Monitoring Configurations to EFS

This step ensures your custom dashboards, datasources, and other settings are loaded by the services.

First, you need a way to access the EFS volume. The easiest method is to use a temporary EC2 instance.

```bash
# Option: Using a temporary EC2 instance in the same VPC
# 1. Launch a small EC2 instance (t2.micro is fine) in one of your private subnets.
# 2. Assign it the ECS security group (`autox-ecs-sg`) to allow EFS access.
# 3. SSH into the EC2 instance and run the following commands:

# Install EFS mount helper
sudo yum install -y amazon-efs-utils

# Mount the EFS volume
  sudo mkdir -p /mnt/efs
sudo mount -t efs -o tls $EFS_ID:/ /mnt/efs

# Create directories for all configurations
sudo mkdir -p /mnt/efs/prometheus-config
sudo mkdir -p /mnt/efs/grafana-provisioning
sudo mkdir -p /mnt/efs/loki-config
sudo mkdir -p /mnt/efs/promtail-config

# Now, from your local machine, copy your config files to the EC2 instance
# Replace `ec2-user@xx.xx.xx.xx` with your EC2 details
scp -i your-key.pem -r ./monitoring/grafana/provisioning ec2-user@xx.xx.xx.xx:~/
scp -i your-key.pem ./monitoring/loki/local-config.yaml ec2-user@xx.xx.xx.xx:~/
scp -i your-key.pem ./monitoring/promtail/promtail-config.yaml ec2-user@xx.xx.xx.xx:~/
scp -i your-key.pem ./prometheus.aws.yml ec2-user@xx.xx.xx.xx:~/

# Back on the EC2 instance, move the files into EFS
sudo mv ~/prometheus.aws.yml /mnt/efs/prometheus-config/prometheus.yml
sudo mv ~/provisioning/* /mnt/efs/grafana-provisioning/
sudo mv ~/local-config.yaml /mnt/efs/loki-config/
sudo mv ~/promtail-config.yaml /mnt/efs/promtail-config/

# Verify the files are in place
sudo ls -lR /mnt/efs/

# Clean up
sudo umount /mnt/efs
# You can now terminate the temporary EC2 instance.
```

**Note:** For production, you should automate this step or use AWS Systems Manager to manage configurations.

Register the monitoring stack task definition:

```bash
# Replace placeholders in the task definition
sed -i "s|REPLACE_WITH_TASK_EXECUTION_ROLE_ARN|$TASK_EXECUTION_ROLE_ARN|g" monitoring-stack-task-definition.json
sed -i "s|REPLACE_WITH_TASK_ROLE_ARN|$TASK_ROLE_ARN|g" monitoring-stack-task-definition.json
sed -i "s|REPLACE_WITH_SECRET_ARN|$SECRET_ARN|g" monitoring-stack-task-definition.json
sed -i "s|REPLACE_WITH_EFS_ID|$EFS_ID|g" monitoring-stack-task-definition.json

# Register the task definition
aws ecs register-task-definition \
  --cli-input-json file://monitoring-stack-task-definition.json \
  --region eu-west-3
```

---

## Part 4: Create ECS Services

### Step 4.1: Create Backend Service (FARGATE_SPOT, Single Instance)

```bash
# Create backend service with ALB integration using FARGATE_SPOT
aws ecs create-service \
  --cluster autox-cluster \
  --service-name autox-backend-service \
  --task-definition autox-backend \
  --desired-count 1 \
  --capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1 \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],securityGroups=[$ECS_SG_ID],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$BACKEND_TG_ARN,containerName=backend,containerPort=8000" \
  --service-registries "registryArn=$BACKEND_SD_ARN" \
  --health-check-grace-period-seconds 60 \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=0,deploymentCircuitBreaker={enable=true,rollback=true}" \
  --enable-execute-command \
  --region eu-west-3
```

**Note:** 
- Using `FARGATE_SPOT` saves up to 70% on compute costs
- `desired-count=1` runs a single instance
- `minimumHealthyPercent=0` allows the service to stop the old task before starting a new one (acceptable for single instance)

### Step 4.2: Create Monitoring Stack Service (FARGATE_SPOT, Single Instance)

First, create service discovery for Grafana (optional, for internal access):

```bash
aws servicediscovery create-service \
  --name grafana \
  --dns-config "NamespaceId=$NAMESPACE_ID,DnsRecords=[{Type=A,TTL=60}]" \
  --health-check-custom-config FailureThreshold=1 \
  --region eu-west-3

export GRAFANA_SD_ARN=$(aws servicediscovery list-services \
  --region eu-west-3 \
  --query "Services[?Name=='grafana'].Arn" \
  --output text)
```

Now create the monitoring stack service:

```bash
# Create monitoring stack service with ALB integration for Grafana
aws ecs create-service \
  --cluster autox-cluster \
  --service-name autox-monitoring-service \
  --task-definition autox-monitoring-stack \
  --desired-count 1 \
  --capacity-provider-strategy capacityProvider=FARGATE_SPOT,weight=1 \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={subnets=[$PRIVATE_SUBNET_1,$PRIVATE_SUBNET_2],securityGroups=[$ECS_SG_ID],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=$GRAFANA_TG_ARN,containerName=grafana,containerPort=3000" \
  --service-registries "registryArn=$GRAFANA_SD_ARN" \
  --health-check-grace-period-seconds 120 \
  --deployment-configuration "maximumPercent=200,minimumHealthyPercent=0,deploymentCircuitBreaker={enable=true,rollback=true}" \
  --enable-execute-command \
  --region eu-west-3
```

**Note:**
- This single task runs all monitoring components (Prometheus, Grafana, Loki, Promtail)
- `health-check-grace-period-seconds=120` gives more time for all containers to start
- Grafana is exposed via ALB for external access
- Prometheus is accessible internally via service discovery

### Step 4.3: Enable Auto Scaling (Optional - Skip for Single Instance Setup)

**For this setup with single instances, auto-scaling is not needed.** If you want to scale in the future:

```bash
# Backend auto-scaling example (not recommended for single instance)
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --resource-id service/autox-cluster/autox-backend-service \
  --scalable-dimension ecs:service:DesiredCount \
  --min-capacity 1 \
  --max-capacity 3 \
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
   - ID: `dockerhub-token`
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

### Current Setup Cost Estimate (Single Instance with FARGATE_SPOT):

**Monthly Cost Breakdown:**
- **Backend Task (1 instance, 1 vCPU, 2GB RAM, FARGATE_SPOT):** ~$5-7/month
- **Monitoring Stack (1 instance, 1 vCPU, 2GB RAM, FARGATE_SPOT):** ~$5-7/month
- **Application Load Balancer:** ~$16-20/month
- **NAT Gateway:** ~$32-35/month (if needed for external API calls)
- **EFS Storage (10GB estimated):** ~$3/month
- **CloudWatch Logs (7-day retention, 5GB/month):** ~$2.5/month
- **Data Transfer:** ~$5/month

**Total Estimated Cost: ~$68-80/month**

### Additional Cost Optimization Tips:

1. ✅ **Already Using FARGATE_SPOT** - Saving up to 70% on compute
2. ✅ **Single Instances** - Minimal task count for small projects
3. **Disable Container Insights if not needed** (saves ~$4-6/month)
4. **Set CloudWatch log retention to 7 days** (implemented below)
5. **Consider removing NAT Gateway** if your app doesn't need external API calls (saves ~$35/month)
6. **Use S3 for long-term log storage** (much cheaper than CloudWatch)
7. **Set up AWS Budget Alerts** to monitor costs

```bash
# Set log retention to 7 days for all log groups
aws logs put-retention-policy \
  --log-group-name /ecs/autox-backend \
  --retention-in-days 7 \
  --region eu-west-3

aws logs put-retention-policy \
  --log-group-name /ecs/autox-prometheus \
  --retention-in-days 7 \
  --region eu-west-3

aws logs put-retention-policy \
  --log-group-name /ecs/autox-grafana \
  --retention-in-days 7 \
  --region eu-west-3

aws logs put-retention-policy \
  --log-group-name /ecs/autox-loki \
  --retention-in-days 7 \
  --region eu-west-3

aws logs put-retention-policy \
  --log-group-name /ecs/autox-promtail \
  --retention-in-days 7 \
  --region eu-west-3

# Set up a budget alert
aws budgets create-budget \
  --account-id $AWS_ACCOUNT_ID \
  --budget file://budget-config.json \
  --notifications-with-subscribers file://budget-notifications.json \
  --region eu-west-3
```

**For even lower costs (if NAT Gateway isn't needed):**
- Remove NAT Gateway: **~$35/month savings**
- Use VPC Endpoints for AWS services instead
- **New Total: ~$33-45/month**

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
- **Backend service** running in private subnets (FARGATE_SPOT, 1 instance)
- **Monitoring stack** with Prometheus, Grafana, Loki, and Promtail (FARGATE_SPOT, 1 instance)
- Application Load Balancer for public access
- Persistent storage using EFS
- Secrets managed in AWS Secrets Manager
- Cost-optimized with FARGATE_SPOT (~70% savings)
- Estimated cost: **~$68-80/month** (or ~$33-45/month without NAT Gateway)

✅ **CI/CD automation** with:
- GitHub webhook triggering Jenkins on push/PR
- Automatic deployment to AWS ECS for `main` branch
- Separate Docker images for different branches

✅ **Frontend on Vercel** (already deployed)

### Architecture Summary:

```
Backend Service:
- 1 task with 1 vCPU, 2GB RAM (FARGATE_SPOT)
- Exposed via ALB on port 80
- Service discovery: backend.autox.local

Monitoring Stack:
- 1 task with 1 vCPU, 2GB RAM (FARGATE_SPOT)
- Contains: Prometheus, Grafana, Loki, Promtail
- Grafana exposed via ALB
- Prometheus accessible internally
```

### Next Steps:

1. Set up custom domain and SSL certificate (optional)
2. Configure CloudWatch alarms for critical metrics
3. Implement EFS backup strategy
4. Consider scaling if traffic increases
5. Monitor costs with AWS Budget Alerts

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

