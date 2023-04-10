resource "aws_iam_role" "ublue" {
  name               = "ublue-put-object-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

data "aws_iam_policy_document" "ublue" {
  statement {
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:ListBucket"
    ]

    resources = [
      aws_s3_bucket.ublue.arn,
      "${aws_s3_bucket.ublue.arn}/*"
    ]
  }
}

resource "aws_iam_policy" "ublue" {
  name   = "ublue-put-object-policy"
  policy = data.aws_iam_policy_document.ublue.json
}


resource "aws_iam_role_policy_attachment" "attach" {
  role       = aws_iam_role.ublue.name
  policy_arn = aws_iam_policy.ublue.arn
}
