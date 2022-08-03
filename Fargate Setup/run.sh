#!/bin/bash

docker run \
    -e INPUT_FILE_NAME='input.json' \
    -e INPUT_FILE_PATH='creavt-thumb-upload/input.json' \
    -e OUTPUT_FILE_NAME='output.json' \
    -e OUTPUT_S3_PATH='creavt-thumb-upload/results' \
    -e AWS_REGION='eu-west-1' \
		-e AWS_ACCESS_KEY_ID='<ACCESS KEY>' \
		-e AWS_SECRET_ACCESS_KEY='<SECRET ACCESS KEY>' \
    -e AWS_DEFAULT_REGION='eu-west-1' \
		gurobi-solver
