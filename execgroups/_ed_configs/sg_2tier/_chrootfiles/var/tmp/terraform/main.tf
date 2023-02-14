resource "aws_security_group" "bastion" {
  name = "bastion"
  description = "Bastion Layer Group"
  vpc_id      = var.vpc_id

  ingress {
    description = "https"
    from_port = 443
    to_port = 443
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }    

  ingress {
    description = "ssh"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }    

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.cloud_tags,
    {
      Name = "${var.vpc_name}-bastion"
      Product = "security_group"
    },
  )
}

resource "aws_security_group" "web" {
  name = "web"
  description = "Web Layer Group"
  vpc_id      = var.vpc_id

  ingress {
    description = "http"
    from_port = 80
    to_port = 80
    protocol = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "https"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "ssh"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    security_groups = [ aws_security_group.bastion.id ]
  }    

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.cloud_tags,
    {
      Name = "${var.vpc_name}-web"
      Product = "security_group"
    },
  )
}

resource "aws_security_group" "database" {
  name = "database"
  description = "Database Layer Group"
  vpc_id      = var.vpc_id

  ingress {
    description = "database allowance"
    from_port = 0
    to_port = 0
    protocol = "-1"
    security_groups = [ aws_security_group.web.id ]
  }

  ingress {
    description = "ssh"
    from_port = 22
    to_port = 22
    protocol = "tcp"
    security_groups = [ aws_security_group.bastion.id ]
  }    

  egress {
    from_port = 0
    to_port = 0
    protocol = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.cloud_tags,
    {
      Name = "${var.vpc_name}-database"
      Product = "security_group"
    },
  )
}

resource "aws_security_group_rule" "web_allow_tcp" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "tcp"
  security_group_id = "${aws_security_group.web.id}"
  source_security_group_id = "${aws_security_group.web.id}"
}

resource "aws_security_group_rule" "web_allow_udp" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "udp"
  security_group_id = "${aws_security_group.web.id}"
  source_security_group_id = "${aws_security_group.web.id}"
}

resource "aws_security_group_rule" "bastion_allow_tcp" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "tcp"
  security_group_id = "${aws_security_group.bastion.id}"
  source_security_group_id = "${aws_security_group.bastion.id}"
}

resource "aws_security_group_rule" "bastion_allow_udp" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "udp"
  security_group_id = "${aws_security_group.bastion.id}"
  source_security_group_id = "${aws_security_group.bastion.id}"
}

resource "aws_security_group_rule" "database_allow_tcp" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "tcp"
  security_group_id = "${aws_security_group.database.id}"
  source_security_group_id = "${aws_security_group.database.id}"
}

resource "aws_security_group_rule" "database_allow_udp" {
  type              = "ingress"
  from_port         = 0
  to_port           = 65535
  protocol          = "udp"
  security_group_id = "${aws_security_group.database.id}"
  source_security_group_id = "${aws_security_group.database.id}"
}
