#!/bin/bash

set -e

RESPONSE=$(curl -s -X POST http://localhost:3000/job)
JOB_ID=$(echo $RESPONSE | jq -r '.job_id')

for i in {1..10}; do
  STATUS=$(curl -s http://localhost:3000/job/$JOB_ID | jq -r '.status')

  if [ "$STATUS" = "completed" ]; then
    exit 0
  fi

  sleep 3
done

echo "Job failed"
exit 1