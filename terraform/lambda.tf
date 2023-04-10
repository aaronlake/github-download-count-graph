locals {
  environment_vars = jsondecode(file("../function/environ.json"))
}

data "archive_file" "zip" {
  source_file = "../function/main.py"
  type        = "zip"
  output_path = "../lambda.zip"
}

resource "aws_lambda_function" "ublue" {
  function_name    = "ublue-download-count"
  filename         = "../lambda.zip"
  source_code_hash = filebase64sha256(data.archive_file.zip.output_path)
  role             = aws_iam_role.ublue.arn
  handler          = "lambda.lambda_handler"
  runtime          = "python3.9"
  environment {
    variables = {
      URL       = local.environment_vars.URL
      S3_BUCKET = local.environment_vars.S3_BUCKET
      S3_KEY    = local.environment_vars.S3_KEY
      GRAPH     = local.environment_vars.GRAPH
    }
  }
  tags = {
    Project = "ublue"
    Repo    = "ublue-os/website"
  }
}
