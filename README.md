# GitHub Download Count Graph

This is a simple script that generates a download count graph for a GitHub repository.

![Example graph](https://ublue-os-graph.s3.us-east-2.amazonaws.com/ublue-os-graph.png)

## Usage

Modify the `/function/environ.json` file to include your GitHub repository and S3 bucket information.

```json
{
  "URL": "GITHUB REPOSITORY URL",
  "S3_BUCKET": "S3_BUCKET",
  "S3_KEY": "S3_KEY",
  "GRAPH": "GRAPH NAME"
}
```

Then, run the following command to deploy the function to AWS Lambda.

```bash
cd terraform
terraform init
terraform apply
```
