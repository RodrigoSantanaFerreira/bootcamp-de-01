
resource "aws_glue_crawler" "crawler_processed" {
  database_name = var.athena_database_name
  name          = "${var.project_name}-crawler-processed-${var.environment}"
  role          = aws_iam_role.glue_job.arn

  delta_target {
    delta_tables = ["s3://processed-stack-bootcampde/tb_coins/"]
    write_manifest = "true"
  }
}

resource "aws_glue_crawler" "crawler_curated" {
  database_name = var.athena_database_name
  name          = "${var.project_name}-crawler-curated-${var.environment}"
  role          = aws_iam_role.glue_job.arn

  delta_target {
    delta_tables = ["s3://curated-stack-bootcampde/coins_circulating_supply/","s3://curated-stack-bootcampde/top10_prices_2022/"]
    write_manifest = "true"
  }
}