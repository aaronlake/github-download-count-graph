resource "aws_cloudwatch_event_rule" "event" {
  name                = "ublue-download-count"
  description         = "Trigger the ublue-download-count lambda function"
  schedule_expression = "cron(0 1 * * ? *)"
}

resource "aws_cloudwatch_event_target" "target" {
  arn  = aws_lambda_function.ublue.arn
  rule = aws_cloudwatch_event_rule.event.name
}

resource "aws_lambda_permission" "permission" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ublue.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.event.arn
}
