
#!/usr/bin/env bash
set -euo pipefail

IMAGE="${PHARMAFLOW_IMAGE:-samuelsesay/pharmaflow-dashboard:day8}"
BUCKET="${PHARMAFLOW_S3_BUCKET:-pharmaflow-data-673502297238-eu-west-2}"
REGION="${AWS_DEFAULT_REGION:-eu-west-2}"

echo "Starting PharmaFlow dashboard deployment..."

# Ensure Docker is available
docker info >/dev/null

# Download the published dashboard image
docker pull "$IMAGE"

# Remove previous dashboard container if present
docker rm -f pharmaflow-dashboard 2>/dev/null || true

# Start the dashboard with EC2 IAM role credentials
docker run -d \
  --name pharmaflow-dashboard \
  --restart unless-stopped \
  -p 127.0.0.1:8501:8501 \
  -e PHARMAFLOW_S3_BUCKET="$BUCKET" \
  -e AWS_DEFAULT_REGION="$REGION" \
  -e AWS_EC2_METADATA_DISABLED=false \
  "$IMAGE"


echo "Waiting for PharmaFlow dashboard health check..."

for attempt in $(seq 1 12); do
  status="$(docker inspect \
    --format '{{.State.Health.Status}}' \
    pharmaflow-dashboard 2>/dev/null || true)"

  if [ "$status" = "healthy" ]; then
    echo "PharmaFlow dashboard is healthy."
    docker ps --filter name=pharmaflow-dashboard
    exit 0
  fi

  if [ "$status" = "unhealthy" ]; then
    echo "Dashboard health check failed."
    docker logs --tail 50 pharmaflow-dashboard
    exit 1
  fi

  echo "Waiting for dashboard... attempt $attempt/12"
  sleep 10
done

echo "Dashboard did not become healthy within the waiting period."
docker logs --tail 50 pharmaflow-dashboard
exit 1

