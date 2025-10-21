#!/bin/bash

# AWS Setup Helper Script for AutoX Deployment
# This script helps you save and export environment variables needed for AWS setup

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}AutoX AWS Setup Helper${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# Create a file to store variables
VARS_FILE=".aws-vars.sh"

# Function to prompt for variable
prompt_var() {
    local var_name=$1
    local var_description=$2
    local current_value=${!var_name}
    
    if [ -n "$current_value" ]; then
        echo -e "${YELLOW}$var_description${NC}"
        echo -e "Current value: ${GREEN}$current_value${NC}"
        read -p "Press Enter to keep or enter new value: " new_value
        if [ -n "$new_value" ]; then
            eval "$var_name='$new_value'"
        fi
    else
        read -p "$var_description: " new_value
        eval "$var_name='$new_value'"
    fi
    
    echo "export $var_name='${!var_name}'" >> "$VARS_FILE"
}

# Source existing vars if file exists
if [ -f "$VARS_FILE" ]; then
    echo -e "${YELLOW}Loading existing variables...${NC}"
    source "$VARS_FILE"
    echo ""
fi

# Clear the vars file
> "$VARS_FILE"

echo "This script will collect and save AWS resource IDs."
echo "You can re-run this script to update values."
echo ""

# Collect all variables
prompt_var "AWS_REGION" "AWS Region (e.g., us-east-1)"
prompt_var "VPC_ID" "VPC ID (e.g., vpc-xxxxx)"
prompt_var "IGW_ID" "Internet Gateway ID (e.g., igw-xxxxx)"
prompt_var "PUBLIC_SUBNET_1" "Public Subnet 1 ID (e.g., subnet-xxxxx)"
prompt_var "PUBLIC_SUBNET_2" "Public Subnet 2 ID (e.g., subnet-xxxxx)"
prompt_var "PRIVATE_SUBNET_1" "Private Subnet 1 ID (e.g., subnet-xxxxx)"
prompt_var "PRIVATE_SUBNET_2" "Private Subnet 2 ID (e.g., subnet-xxxxx)"
prompt_var "EIP_ALLOC_ID" "Elastic IP Allocation ID (e.g., eipalloc-xxxxx)"
prompt_var "NAT_GATEWAY_ID" "NAT Gateway ID (e.g., nat-xxxxx)"
prompt_var "PUBLIC_RT_ID" "Public Route Table ID (e.g., rtb-xxxxx)"
prompt_var "PRIVATE_RT_ID" "Private Route Table ID (e.g., rtb-xxxxx)"
prompt_var "ALB_SG_ID" "ALB Security Group ID (e.g., sg-xxxxx)"
prompt_var "ECS_SG_ID" "ECS Security Group ID (e.g., sg-xxxxx)"
prompt_var "EFS_ID" "EFS File System ID (e.g., fs-xxxxx)"
prompt_var "ECR_REPO_URI" "ECR Repository URI (e.g., 123456789012.dkr.ecr.us-east-1.amazonaws.com/autox-backend)"
prompt_var "TASK_EXECUTION_ROLE_ARN" "Task Execution Role ARN"
prompt_var "TASK_ROLE_ARN" "Task Role ARN"
prompt_var "SECRET_ARN" "Secrets Manager Secret ARN"
prompt_var "ALB_ARN" "Application Load Balancer ARN"
prompt_var "ALB_DNS" "ALB DNS Name"
prompt_var "BACKEND_TG_ARN" "Backend Target Group ARN"
prompt_var "GRAFANA_TG_ARN" "Grafana Target Group ARN (optional)"
prompt_var "LISTENER_ARN" "ALB Listener ARN"
prompt_var "NAMESPACE_ID" "Service Discovery Namespace ID"
prompt_var "BACKEND_SD_ARN" "Backend Service Discovery ARN"

echo ""
echo -e "${GREEN}Variables saved to $VARS_FILE${NC}"
echo -e "${YELLOW}To use these variables in your shell, run:${NC}"
echo -e "${GREEN}source $VARS_FILE${NC}"
echo ""
echo -e "${YELLOW}You can now run AWS CLI commands using these variables.${NC}"

# Make the vars file executable
chmod +x "$VARS_FILE"

# Create a backup
cp "$VARS_FILE" "${VARS_FILE}.backup"
echo -e "${GREEN}Backup created: ${VARS_FILE}.backup${NC}"

