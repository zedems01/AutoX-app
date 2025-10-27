resource "aws_secretsmanager_secret" "main" {
  name = "${var.project_name}/production/env"
  tags = local.tags
}

resource "aws_secretsmanager_secret_version" "main" {
  secret_id     = aws_secretsmanager_secret.main.id
  secret_string = jsonencode(var.secrets)
}