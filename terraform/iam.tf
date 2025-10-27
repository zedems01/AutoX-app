# ECS Task Execution Role
resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "${var.project_name}EcsTaskExecutionRole"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action    = "sts:AssumeRole"
      }
    ]
  })
  tags = local.tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# Policy to access secrets
resource "aws_iam_policy" "secrets_access" {
  name        = "${var.project_name}-secrets-access-policy"
  description = "Policy to access secrets from Secrets Manager"
  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = "secretsmanager:GetSecretValue",
        Resource = aws_secretsmanager_secret.main.arn
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "secrets_access" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = aws_iam_policy.secrets_access.arn
}

# ECS Task Role
resource "aws_iam_role" "ecs_task_role" {
  name               = "${var.project_name}EcsTaskRole"
  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect    = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action    = "sts:AssumeRole"
      }
    ]
  })
  tags = local.tags
}

# Policy for EFS access
resource "aws_iam_policy" "efs_access" {
  name        = "${var.project_name}-efs-access-policy"
  description = "Policy for ECS tasks to access EFS"
  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "elasticfilesystem:ClientMount",
          "elasticfilesystem:ClientWrite",
          "elasticfilesystem:DescribeFileSystems"
        ],
        Resource = "*" # For simplicity, can be scoped down to the specific EFS ARN
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "efs_access" {
  role       = aws_iam_role.ecs_task_role.name
  policy_arn = aws_iam_policy.efs_access.arn
}