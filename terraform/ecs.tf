# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  configuration {
    execute_command_configuration {
      logging = "DEFAULT"
    }
  }

  tags = local.tags
}

# Task Definitions
data "template_file" "backend_task_definition" {
  template = file("${path.module}/backend-task-definition.json.tpl")
  vars = {
    task_execution_role_arn = aws_iam_role.ecs_task_execution_role.arn
    task_role_arn           = aws_iam_role.ecs_task_role.arn
    ecr_repo_url            = aws_ecr_repository.backend.repository_url
    secret_arn              = aws_secretsmanager_secret.main.arn
    backend_log_group_name  = aws_cloudwatch_log_group.backend.name
    aws_region              = var.aws_region
    efs_id                  = aws_efs_file_system.main.id
  }
}

resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.project_name}-backend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  container_definitions    = data.template_file.backend_task_definition.rendered
  tags                     = local.tags
}

data "template_file" "monitoring_task_definition" {
  template = file("${path.module}/monitoring-task-definition.json.tpl")
  vars = {
    task_execution_role_arn   = aws_iam_role.ecs_task_execution_role.arn
    task_role_arn             = aws_iam_role.ecs_task_role.arn
    secret_arn                = aws_secretsmanager_secret.main.arn
    prometheus_log_group_name = aws_cloudwatch_log_group.prometheus.name
    grafana_log_group_name    = aws_cloudwatch_log_group.grafana.name
    loki_log_group_name       = aws_cloudwatch_log_group.loki.name
    promtail_log_group_name   = aws_cloudwatch_log_group.promtail.name
    aws_region                = var.aws_region
    efs_id                    = aws_efs_file_system.main.id
  }
}

resource "aws_ecs_task_definition" "monitoring" {
  family                   = "${var.project_name}-monitoring-stack"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  container_definitions    = data.template_file.monitoring_task_definition.rendered
  tags                     = local.tags
}


# ECS Services
resource "aws_ecs_service" "backend" {
  name            = "${var.project_name}-backend-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }
  
  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  service_registries {
    registry_arn = aws_service_discovery_service.backend.arn
  }

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  enable_execute_command = true
  tags                     = local.tags
}

resource "aws_ecs_service" "monitoring" {
  name            = "${var.project_name}-monitoring-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.monitoring.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  capacity_provider_strategy {
    capacity_provider = "FARGATE_SPOT"
    weight            = 1
  }

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.grafana.arn
    container_name   = "grafana"
    container_port   = 3000
  }

  service_registries {
    registry_arn = aws_service_discovery_service.grafana.arn
  }

  health_check_grace_period_seconds = 120

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  enable_execute_command = true
  tags                     = local.tags
}