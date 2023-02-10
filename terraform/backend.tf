terraform {
  backend "s3" {
    # Edit the bucket name and region
    bucket         = "stack-terraform-backend"
    key            = "global/s3/terraform.tfstate"
    region         = "us-east-1"

    # Edit the bucket name and region
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}