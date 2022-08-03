#!/bin/bash

echo "Downloading input file"
aws s3 cp s3://${INPUT_FILE_PATH} ./ --region ${AWS_REGION}

ls

echo "Starting Gurobi solver"
python solver.py ${INPUT_FILE_NAME} ${OUTPUT_FILE_NAME}

echo "Copying ${OUTPUT_FILE_NAME} to S3 at ${OUTPUT_S3_PATH}/${OUTPUT_FILE_NAME} ..."
aws s3 cp ./${OUTPUT_FILE_NAME} s3://${OUTPUT_S3_PATH}/${OUTPUT_FILE_NAME} --region ${AWS_REGION}
