resource "aws_s3_bucket" "ublue" {
  bucket = local.environment_vars.S3_BUCKET
  tags = {
    Name        = "ublue"
    Environment = "dev"
  }
}

resource "aws_s3_bucket_acl" "acl" {
  bucket = aws_s3_bucket.ublue.id
  acl    = "public-read"
}

resource "aws_s3_object" "index" {
  bucket = aws_s3_bucket.ublue.id
  key    = "downloads.csv"
  source = "./downloads.csv"
}
