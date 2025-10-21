# AutoX AWS Deployment - Quick Start Guide

This is your **single guide** for deploying AutoX to AWS ECS with Jenkins CI/CD.

---

## 📋 What You Have

After this implementation, you have:

1. ✅ **Unified Jenkinsfile** - Single pipeline for backend + frontend
2. ✅ **AWS Docker Compose** - Backend + monitoring stack configuration
3. ✅ **Prometheus Config** - Optimized for AWS ECS
4. ✅ **Comprehensive Guide** - Step-by-step AWS setup instructions
5. ✅ **Deployment Checklist** - Track your progress
6. ✅ **Helper Scripts** - Simplify AWS setup

---

## 🗂️ File Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `AWS_DEPLOYMENT_GUIDE.md` | **Complete deployment instructions** | Follow this for step-by-step AWS setup |
| `DEPLOYMENT_CHECKLIST.md` | **Quick checklist** | Track progress, ensure nothing is missed |
| `DEPLOYMENT_SUMMARY.md` | **Overview & architecture** | Understand how everything fits together |
| `Jenkinsfile` | **CI/CD pipeline** | Automatically runs on git push |
| `docker-compose.aws.yml` | **Docker services config** | Deploy backend + monitoring on AWS |
| `prometheus.aws.yml` | **Prometheus config** | Used by monitoring stack |
| `.env.aws.template` | **Environment variables** | Copy to `.env` and fill in values |
| `aws-setup-helper.sh` | **Track AWS resource IDs** | Run during AWS setup to organize resource IDs |

---

## 🚀 Deployment Steps (High-Level)

### Step 1: Read the Documentation (5 minutes)
```bash
# Start here to understand the architecture
cat DEPLOYMENT_SUMMARY.md

# Then review the full guide
cat AWS_DEPLOYMENT_GUIDE.md
```

### Step 2: AWS Infrastructure Setup (1-2 hours)
```bash
# Make helper script executable
chmod +x aws-setup-helper.sh

# Follow AWS_DEPLOYMENT_GUIDE.md Part 1-2
# Use aws-setup-helper.sh to track resource IDs
./aws-setup-helper.sh

# Load variables for subsequent commands
source .aws-vars.sh
```

**Key AWS Resources to Create:**
- VPC with public/private subnets
- Security groups
- EFS file system
- ECR repository
- IAM roles
- Secrets Manager secret
- ECS cluster
- Application Load Balancer
- ECS task definitions and services

### Step 3: Jenkins Configuration (30 minutes)
1. Install required Jenkins plugins
2. Add credentials (Docker Hub, AWS)
3. Create Multibranch Pipeline
4. Configure GitHub webhook

**See:** `AWS_DEPLOYMENT_GUIDE.md` Part 5-6

### Step 4: Deploy (15 minutes)
```bash
# Commit and push changes
git add Jenkinsfile docker-compose.aws.yml prometheus.aws.yml .env.aws.template
git commit -m "feat: AWS ECS deployment setup"
git push origin main

# Jenkins will automatically:
# - Run tests
# - Build Docker images
# - Push to Docker Hub and ECR
# - Trigger ECS deployment
```

### Step 5: Verify (10 minutes)
```bash
# Get ALB DNS name
aws elbv2 describe-load-balancers \
  --names autox-alb \
  --region us-east-1 \
  --query 'LoadBalancers[0].DNSName' \
  --output text

# Test backend
curl http://YOUR_ALB_DNS/health
# Expected: {"status":"oki doki"}

# Check metrics
curl http://YOUR_ALB_DNS/metrics
# Expected: Prometheus metrics output
```

---

## ⚙️ Configuration Checklist

### Before Starting:
- [ ] AWS account with admin access
- [ ] OVH server with Jenkins running
- [ ] Docker Hub account
- [ ] All API keys ready:
  - [ ] ANTHROPIC_API_KEY
  - [ ] OPENAI_API_KEY
  - [ ] GROQ_API_KEY
  - [ ] GOOGLE_API_KEY
  - [ ] SERPER_API_KEY
  - [ ] COMPOSIO_API_KEY
- [ ] Test user credentials (if using demo mode)

### AWS Configuration:
- [ ] Set AWS region in `Jenkinsfile` (default: us-east-1)
- [ ] Create all secrets in AWS Secrets Manager
- [ ] Copy `.env.aws.template` to `.env` (for local testing)

### Jenkins Configuration:
- [ ] Add Jenkins credentials:
  - [ ] `dockerhub-autox` (username/password)
  - [ ] `aws-account-id` (secret text)
  - [ ] `aws-access-key-id` (secret text)
  - [ ] `aws-secret-access-key` (secret text)
- [ ] Configure Node.js tool (name: `node22`)
- [ ] Install AWS CLI on Jenkins server

---

## 🔄 Continuous Deployment Flow

```
Developer Push to GitHub
        ↓
GitHub Webhook → Jenkins (OVH)
        ↓
┌───────────────────────┐
│   Jenkins Pipeline    │
│                       │
│  1. Checkout code     │
│  2. Run backend tests │
│  3. Run frontend tests│
│  4. Build images      │
│  5. Push to registries│
│  6. Trigger AWS ECS   │
└───────────────────────┘
        ↓
AWS ECS Pulls New Image
        ↓
Rolling Update (Blue-Green)
        ↓
New Version Live! ✅
```

---

## 📊 Monitoring Access

After deployment, you can access:

| Service | URL | Purpose |
|---------|-----|---------|
| **Backend API** | `http://YOUR_ALB_DNS/` | Main application |
| **Health Check** | `http://YOUR_ALB_DNS/health` | Service health |
| **Metrics** | `http://YOUR_ALB_DNS/metrics` | Prometheus metrics |
| **Grafana** | `http://YOUR_ALB_DNS/grafana` | Dashboards (if on ECS) |
| **Frontend** | `https://your-app.vercel.app` | User interface |
| **CloudWatch Logs** | AWS Console | Container logs |

---

## 🆘 Quick Troubleshooting

### Issue: ECS tasks not starting
```bash
# Check CloudWatch logs
aws logs tail /ecs/autox-backend --follow --region us-east-1

# Check task status
aws ecs describe-tasks \
  --cluster autox-cluster \
  --tasks TASK_ARN \
  --region us-east-1
```

### Issue: Health checks failing
- Check security group allows ALB → ECS traffic on port 8000
- Verify application is listening on correct port (8000)
- Check CloudWatch logs for errors

### Issue: Jenkins pipeline fails
- Verify all credentials are configured correctly
- Check AWS CLI is installed on Jenkins server
- Ensure ECR repository exists
- Review Jenkins console output

### Issue: Can't access backend via ALB
```bash
# Check target group health
aws elbv2 describe-target-health \
  --target-group-arn YOUR_TARGET_GROUP_ARN \
  --region us-east-1

# Verify security groups
# ALB SG: Allow inbound 80/443
# ECS SG: Allow inbound 8000 from ALB SG
```

**For more troubleshooting, see:** `AWS_DEPLOYMENT_GUIDE.md` Part 11

---

## 💰 Cost Estimate

**Minimal Setup:** ~$95-105/month
- ECS Fargate (2 tasks)
- Application Load Balancer
- NAT Gateway
- EFS storage
- CloudWatch logs

**Production Setup:** ~$166-241/month
- Auto-scaling (2-10 tasks)
- Container Insights
- Enhanced monitoring
- EFS snapshots

**Cost Optimization:**
- Use Fargate Spot (70% savings)
- Set CloudWatch log retention to 7 days
- Scale down dev environments when not in use

---

## 🎯 Success Criteria

You're done when:

- ✅ Jenkins pipeline runs successfully on push to `main`
- ✅ Backend is running on AWS ECS Fargate
- ✅ ALB health check returns `{"status":"oki doki"}`
- ✅ Prometheus metrics are accessible
- ✅ CloudWatch logs show application activity
- ✅ Frontend on Vercel can connect to backend

---

## 📚 Additional Resources

### Project Documentation:
- **Architecture Overview:** `DEPLOYMENT_SUMMARY.md`
- **Step-by-Step Guide:** `AWS_DEPLOYMENT_GUIDE.md`
- **Progress Checklist:** `DEPLOYMENT_CHECKLIST.md`

### External Documentation:
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Compose Specification](https://docs.docker.com/compose/compose-file/)
- [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/configuration/)

---

## 🚦 What to Do Right Now

1. **Read this file** ✅ (you're here!)
2. **Review** `DEPLOYMENT_SUMMARY.md` to understand the architecture
3. **Start following** `AWS_DEPLOYMENT_GUIDE.md` for detailed setup
4. **Use** `DEPLOYMENT_CHECKLIST.md` to track your progress
5. **Run** `aws-setup-helper.sh` during AWS setup to organize resource IDs

---

## 📝 Notes

### About the Unified Jenkinsfile:
- Replaces both the old root `Jenkinsfile` and `x_automation_app/frontend/Jenkinsfile`
- Handles both backend and frontend in a single pipeline
- Automatically deploys to AWS ECS on `main` branch push
- Frontend is still deployed to Vercel separately (manually or via Vercel integration)

### About Docker Compose:
- `docker-compose.aws.yml` is for AWS deployment only
- Original `docker-compose.yml` can still be used for local development
- Monitoring stack can be deployed on separate EC2 or use AWS managed services

### About Secrets:
- **Never commit** `.env` files to git
- Use AWS Secrets Manager for production secrets
- Use Jenkins credentials for CI/CD secrets

---

## ✨ You're Ready!

Follow the guides, use the checklist, and you'll have a production-ready AWS deployment with automated CI/CD via Jenkins.

**Start with:** `AWS_DEPLOYMENT_GUIDE.md` → Part 1

Good luck! 🚀

---

**Questions?** Refer to the troubleshooting sections in the guides or check AWS/Jenkins documentation.

