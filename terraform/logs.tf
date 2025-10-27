resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.project_name}-backend"
  retention_in_days = 7
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "prometheus" {
  name              = "/ecs/${var.project_name}-prometheus"
  retention_in_days = 7
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "grafana" {
  name              = "/ecs/${var.project_name}-grafana"
  retention_in_days = 7
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "loki" {
  name              = "/ecs/${var.project_name}-loki"
  retention_in_days = 7
  tags              = local.tags
}

resource "aws_cloudwatch_log_group" "promtail" {
  name              = "/ecs/${var.project_name}-promtail"
  retention_in_days = 7
  tags              = local.tags
}