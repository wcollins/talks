resource "aws_vpc" "this" {
  cidr_block  = "10.5.0.0/16"

  tags = {
    Name = format("vpc-%s", random_string.this.result)
  }

}

resource "aws_subnet" "this" {
  vpc_id      = aws_vpc.this.id
  cidr_block  = "10.5.1.0/24"

  tags = {
    Name = format("subnet-%s", random_string.this.result)
  }

}

resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id

  tags    = {
    Name  = format("igw-%s", random_string.this.result)
  }

}

resource "aws_route_table" "this" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block         = "0.0.0.0/0"
    gateway_id         = aws_internet_gateway.this.id
  }

  tags    = {
    Name  = format("rtb-%s", random_string.this.result)
  }

}

resource "aws_route_table_association" "this" {
  subnet_id       = aws_subnet.this.id
  route_table_id  = aws_route_table.this.id

  tags    = {
    Name  = format("rtb-assoc-%s", random_string.this.result)
  }

}

resource "aws_instance" "this" {
  ami                         = "ami-0f0ba639982a32edb"
  instance_type               = "t3.nano"
  subnet_id                   = aws_subnet.this.id
  associate_public_ip_address = true

  tags    = {
    Name  = "ec2-useast2-stage"
  }

}

resource "aws_security_group" "this" {
  vpc_id      = aws_vpc.this.id
  name        = format("grp-%s", random_string.this.result)

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags    = {
    Name  = format("grp-%s", random_string.this.result)
  }

}

resource "aws_network_interface_sg_attachment" "this" {
  security_group_id     = aws_security_group.this.id
  network_interface_id  = aws_instance.this.primary_network_interface_id
}