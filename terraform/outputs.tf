output "alb_dns_name" {
  description = "The DNS name of the Application Load Balancer."
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  description = "The URL of the ECR repository."
  value       = aws_ecr_repository.backend.repository_url
}

output "secrets_manager_arn" {
  description = "The ARN of the secret in AWS Secrets Manager."
  value       = aws_secretsmanager_secret.main.arn
}