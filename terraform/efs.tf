resource "aws_efs_file_system" "main" {
  creation_token = "${var.project_name}-efs"
  performance_mode = "generalPurpose"
  throughput_mode  = "bursting"
  encrypted        = true
  tags             = merge(local.tags, { Name = "${var.project_name}-efs" })
}

resource "aws_efs_mount_target" "private" {
  count           = length(aws_subnet.private)
  file_system_id  = aws_efs_file_system.main.id
  subnet_id       = aws_subnet.private[count.index].id
  security_groups = [aws_security_group.ecs_tasks.id]
}