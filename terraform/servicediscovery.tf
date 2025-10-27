resource "aws_service_discovery_private_dns_namespace" "main" {
  name = "${var.project_name}.local"
  vpc  = aws_vpc.main.id
}

resource "aws_service_discovery_service" "backend" {
  name = "backend"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    dns_records {
      ttl  = 60
      type = "A"
    }
  }

  health_check_config {
    failure_threshold = 1
  }
}

resource "aws_service_discovery_service" "grafana" {
  name = "grafana"
  
  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main.id
    dns_records {
      ttl  = 60
      type = "A"
    }
  }

  health_check_config {
    failure_threshold = 1
  }
}
