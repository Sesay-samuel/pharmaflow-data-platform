
# Private RDS subnet in eu-west-2a
resource "aws_subnet" "rds_private_a" {
  vpc_id                  = var.vpc_id
  cidr_block              = "172.31.64.0/24"
  availability_zone       = "eu-west-2a"
  map_public_ip_on_launch = false

  tags = {
    Name = "pharmaflow-rds-private-a"
  }
}

# Private RDS subnet in eu-west-2b
resource "aws_subnet" "rds_private_b" {
  vpc_id                  = var.vpc_id
  cidr_block              = "172.31.65.0/24"
  availability_zone       = "eu-west-2b"
  map_public_ip_on_launch = false

  tags = {
    Name = "pharmaflow-rds-private-b"
  }
}

# Private route table without internet access
resource "aws_route_table" "rds_private" {
  vpc_id = var.vpc_id

  tags = {
    Name = "pharmaflow-rds-private-rt"
  }
}

resource "aws_route_table_association" "rds_private_a" {
  subnet_id      = aws_subnet.rds_private_a.id
  route_table_id = aws_route_table.rds_private.id
}

resource "aws_route_table_association" "rds_private_b" {
  subnet_id      = aws_subnet.rds_private_b.id
  route_table_id = aws_route_table.rds_private.id
}

