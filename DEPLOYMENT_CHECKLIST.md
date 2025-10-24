# AutoX AWS Deployment - Quick Checklist

This is a condensed checklist. For detailed instructions, see `AWS_DEPLOYMENT_GUIDE.md`.

---

## Pre-Deployment Checklist

- [ ] AWS account with admin access
- [ ] OVH server with Jenkins running
- [ ] Docker Hub account
- [ ] AWS CLI installed locally
- [ ] Git repository access
- [ ] All API keys ready (Anthropic, OpenAI, Groq, Google, Serper, Composio)

---

## Phase 1: AWS Infrastructure (Local Machine)

### 1.1 VPC & Networking
```bash
# Set your AWS region
export AWS_REGION=us-east-1

# Use aws-setup-helper.sh to track IDs as you create resources
chmod +x aws-setup-helper.sh
./aws-setup-helper.sh
```

- [ ] Create VPC (10.0.0.0/16)
- [ ] Create Internet Gateway
- [ ] Create 2 Public Subnets (different AZs)
- [ ] Create 2 Private Subnets (different AZs)
- [ ] Create Elastic IP
- [ ] Create NAT Gateway
- [ ] Create & configure Route Tables
- [ ] Associate subnets with route tables

### 1.2 Security Groups
- [ ] Create ALB Security Group (ports: 80, 443, 3001)
- [ ] Create ECS Security Group (allow from ALB + internal traffic)

### 1.3 Storage & Registry
- [ ] Create EFS File System
- [ ] Create EFS Mount Targets in private subnets
- [ ] Create ECR repository (`autox-backend`)

### 1.4 IAM Roles
- [ ] Create ECS Task Execution Role
- [ ] Attach `AmazonECSTaskExecutionRolePolicy`
- [ ] Create ECS Task Role
- [ ] Add EFS access policy
- [ ] Add Secrets Manager access policy

### 1.5 Secrets Management
- [ ] Create secret in AWS Secrets Manager (`autox/production/env`)
- [ ] Add all API keys and credentials to secret
- [ ] Update Task Execution Role to access secrets

---

## Phase 2: ECS Cluster & Services

### 2.1 Cluster Setup
- [ ] Create ECS Cluster (`autox-cluster`)
- [ ] Enable Container Insights (optional)
- [ ] Create CloudWatch Log Groups

### 2.2 Load Balancer
- [ ] Create Application Load Balancer in public subnets
- [ ] Create Target Groups (backend, grafana)
- [ ] Create HTTP Listener with routing rules
- [ ] Note ALB DNS name

### 2.3 Service Discovery
- [ ] Create private DNS namespace (`autox.local`)
- [ ] Create service discovery service for backend

### 2.4 Task Definitions & Services
- [ ] Create backend task definition (use template from guide)
- [ ] Register task definition
- [ ] Create backend ECS service with ALB integration
- [ ] Configure auto-scaling (optional)

---

## Phase 3: Jenkins Configuration (OVH Server)

### 3.1 Install Prerequisites
```bash
# On OVH server
sudo su - jenkins
aws --version  # If not installed, install AWS CLI
```

### 3.2 Jenkins Setup
- [ ] Install required plugins (Docker, AWS Steps, AWS Credentials, Git, Pipeline)
- [ ] Add Docker Hub credentials (`dockerhub-token`)
- [ ] Add AWS credentials:
  - `aws-account-id` (Secret text)
  - `aws-access-key-id` (Secret text)
  - `aws-secret-access-key` (Secret text)
- [ ] Configure AWS CLI for Jenkins user

### 3.3 Pipeline Setup
- [ ] Create Multibranch Pipeline in Jenkins
- [ ] Configure Git repository as branch source
- [ ] Set Script Path to `Jenkinsfile`
- [ ] Save and scan repository

### 3.4 Webhook Configuration
- [ ] Generate Jenkins API token
- [ ] Add webhook in GitHub repository:
  - Payload URL: `http://your-jenkins-url/github-webhook/`
  - Events: Push + Pull Requests
- [ ] Test webhook delivery

---

## Phase 4: Configuration Files

### 4.1 Update Configuration
- [ ] Update `Jenkinsfile` AWS_REGION if not `us-east-1`
- [ ] Copy `.env.aws.template` to `.env` and fill in values
- [ ] Ensure `docker-compose.aws.yml` is properly configured
- [ ] Verify `prometheus.aws.yml` exists in project root

### 4.2 Commit Changes
```bash
git add Jenkinsfile docker-compose.aws.yml prometheus.aws.yml .env.aws.template
git commit -m "feat: AWS ECS deployment setup"
git push origin main
```

---

## Phase 5: Deployment & Testing

### 5.1 Initial Deployment
- [ ] Push code to main branch (triggers Jenkins)
- [ ] Monitor Jenkins pipeline execution
- [ ] Check all stages pass (backend tests, frontend tests, Docker builds)
- [ ] Verify images pushed to Docker Hub and ECR
- [ ] Confirm ECS deployment triggered

### 5.2 Verify AWS Deployment
```bash
# Check ECS service
aws ecs describe-services \
  --cluster autox-cluster \
  --services autox-backend-service \
  --region $AWS_REGION

# Check task status
aws ecs list-tasks \
  --cluster autox-cluster \
  --service-name autox-backend-service \
  --region $AWS_REGION

# Get ALB DNS
aws elbv2 describe-load-balancers \
  --names autox-alb \
  --region $AWS_REGION \
  --query 'LoadBalancers[0].DNSName' \
  --output text
```

### 5.3 Test Endpoints
```bash
# Replace with your ALB DNS
ALB_DNS="your-alb-dns-name"

# Health check
curl http://$ALB_DNS/health

# Metrics endpoint
curl http://$ALB_DNS/metrics
```

- [ ] Backend health check returns `{"status":"oki doki"}`
- [ ] Metrics endpoint returns Prometheus metrics
- [ ] No errors in CloudWatch logs

---

## Phase 6: Monitoring Stack (Optional)

### Option A: Deploy on EC2
- [ ] Launch EC2 instance in public subnet
- [ ] Install Docker & Docker Compose
- [ ] Copy `docker-compose.aws.yml` and `prometheus.aws.yml`
- [ ] Run `docker-compose -f docker-compose.aws.yml up -d`
- [ ] Access Grafana via EC2 public IP

### Option B: Use AWS Managed Services
- [ ] Set up Amazon Managed Prometheus
- [ ] Set up Amazon Managed Grafana
- [ ] Configure data sources

---

## Phase 7: Optional Enhancements

### Domain & SSL
- [ ] Create Route 53 hosted zone
- [ ] Request ACM certificate
- [ ] Add HTTPS listener to ALB
- [ ] Create DNS A records

### Monitoring & Alerts
- [ ] Set up CloudWatch alarms
- [ ] Configure SNS topics for notifications
- [ ] Create custom dashboards

### Backup & Disaster Recovery
- [ ] Configure EFS backup policy
- [ ] Set up cross-region replication (if needed)
- [ ] Document rollback procedures

---

## Troubleshooting Quick Reference

### ECS Tasks Not Starting
```bash
# Check CloudWatch logs
aws logs tail /ecs/autox-backend --follow --region $AWS_REGION

# Check task stopped reason
aws ecs describe-tasks --cluster autox-cluster --tasks TASK_ARN --region $AWS_REGION
```

### Health Checks Failing
- Verify security group allows ALB → ECS traffic on port 8000
- Check application logs in CloudWatch
- Increase health check grace period

### Jenkins Pipeline Fails
- Check Jenkins credentials are correct
- Verify AWS CLI is installed on Jenkins server
- Check ECR repository exists
- Review Jenkins console output

### Can't Access ALB
- Verify security group allows inbound traffic on ports 80/443
- Check target group health status
- Ensure at least one task is running and healthy

---

## Resource Cleanup (When Needed)

To tear down the infrastructure:

```bash
# Delete ECS service
aws ecs delete-service --cluster autox-cluster --service autox-backend-service --force --region $AWS_REGION

# Delete ECS cluster
aws ecs delete-cluster --cluster autox-cluster --region $AWS_REGION

# Delete ALB, Target Groups, etc. (in reverse order of creation)
```

**Note:** Be careful with cleanup - some resources may incur costs if left running.

---

## Key URLs Reference

- **Jenkins:** `http://your-ovh-jenkins-url`
- **ALB Backend:** `http://your-alb-dns/`
- **ALB Health:** `http://your-alb-dns/health`
- **Metrics:** `http://your-alb-dns/metrics`
- **Grafana:** `http://your-alb-dns/grafana` (if deployed on ECS) or `http://ec2-ip:3001`
- **Frontend (Vercel):** `https://your-vercel-domain.vercel.app`

---

## Success Criteria

✅ Jenkins pipeline runs successfully on every push to main  
✅ Backend deployed to AWS ECS Fargate  
✅ ALB health check returns 200 OK  
✅ Prometheus metrics endpoint accessible  
✅ CloudWatch logs showing application activity  
✅ Auto-scaling configured (if enabled)  
✅ Frontend on Vercel connects to backend via ALB  

---

**For detailed step-by-step instructions, refer to `AWS_DEPLOYMENT_GUIDE.md`**


