resource "aws_sfn_state_machine" "agentic" {
  name     = "agentic-state-machine"
  role_arn = aws_iam_role.sfn_role.arn

  definition = file("${path.module}/../step_function/step_function.json")
}