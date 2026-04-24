#!/usr/bin/env bash
set -euo pipefail
PROJECT=${1:-agrotech}
ENV=${2:-dev}
REGION=${3:-us-east-1}
STACK_NAME="${PROJECT}-${ENV}-agras-mvp"
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Deploying CloudFormation stack ${STACK_NAME} in ${REGION}..."
aws cloudformation deploy \
  --region "${REGION}" \
  --template-file "${ROOT_DIR}/infra/cloudformation.yaml" \
  --stack-name "${STACK_NAME}" \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides Projeto="${PROJECT}" Ambiente="${ENV}"

RAW_BUCKET=$(aws cloudformation describe-stacks --region "${REGION}" --stack-name "${STACK_NAME}" --query "Stacks[0].Outputs[?OutputKey=='RawBucketName'].OutputValue" --output text)
LAMBDA_NAME="${PROJECT}-${ENV}-agras-processor"

echo "Packaging Lambda..."
cd "${ROOT_DIR}/lambda/processor"
zip -q -r /tmp/agras_processor.zip processor.py
aws lambda update-function-code --region "${REGION}" --function-name "${LAMBDA_NAME}" --zip-file fileb:///tmp/agras_processor.zip >/dev/null

echo "Uploading sample data to s3://${RAW_BUCKET}/incoming/..."
aws s3 cp "${ROOT_DIR}/data/sample_agras_flight_5000.json" "s3://${RAW_BUCKET}/incoming/sample_agras_flight_5000.json" --region "${REGION}"

echo "Done. Wait a few seconds and check the processed bucket output."
