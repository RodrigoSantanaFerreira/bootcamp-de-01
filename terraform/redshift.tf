resource "aws_redshift_cluster" "redshift-cluster" {
  cluster_identifier = "redshift-cluster"
  database_name      = "coins"
  master_username    = "awsuser"
  master_password    = "U%SlC7*Y807n"
  node_type          = "dc2.large"
  cluster_type       = "single-node"
  skip_final_snapshot = true
}