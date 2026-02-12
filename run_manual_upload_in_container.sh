#!/usr/bin/env bash
# Copy the 4 PDFs from ./pdfs into the backend container and run the manual upload script there.

set -euo pipefail

PDF_DIR="$(pwd)/pdfs"
if [ ! -d "$PDF_DIR" ]; then
  echo "ERROR: pdfs directory not found at $PDF_DIR"
  exit 1
fi

mapfile -t files < <(printf "%s\n" "$PDF_DIR"/*.pdf)

if [ "${#files[@]}" -ne 4 ]; then
  echo "ERROR: expected exactly 4 PDF files in $PDF_DIR, found ${#files[@]}"
  printf "Found files:\n"
  for f in "${files[@]}"; do
    echo "  - $(basename "$f")"
  done
  exit 1
fi

echo "Locating backend container..."
# Try several strategies to find the backend container id
CONTAINER_ID=""

# 1) docker compose (preferred)
if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
  CONTAINER_ID=$(docker compose ps -q backend 2>/dev/null || true)
fi

# 2) fallback: look for a running container with 'backend' in name
if [ -z "$CONTAINER_ID" ]; then
  CONTAINER_ID=$(docker ps --filter "name=backend" --format "{{.ID}}" | head -n1 || true)
fi

# 3) fallback: look for container with image name containing 'backend:dev'
if [ -z "$CONTAINER_ID" ]; then
  CONTAINER_ID=$(docker ps --filter "ancestor=backend:dev" --format "{{.ID}}" | head -n1 || true)
fi

# 4) fallback: look for container with name containing 'policybot' and 'backend'
if [ -z "$CONTAINER_ID" ]; then
  CONTAINER_ID=$(docker ps --format "{{.ID}} {{.Names}}" | awk '/policybot/ && /backend/ {print $1; exit}' || true)
fi

if [ -z "$CONTAINER_ID" ]; then
  echo "ERROR: could not find backend container. Containers currently running:"
  docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Names}}"
  exit 1
fi

echo "Creating remote temp dir /tmp/manual_upload in container $CONTAINER_ID"
docker exec "$CONTAINER_ID" mkdir -p /tmp/manual_upload

echo "Copying PDFs into container..."
for f in "${files[@]}"; do
  echo "  -> $(basename "$f")"
  docker cp "$f" "$CONTAINER_ID":/tmp/manual_upload/
done

echo "Copying manual_upload script into container..."
docker cp backend/scripts/manual_upload.py "$CONTAINER_ID":/app/scripts/manual_upload.py
docker exec "$CONTAINER_ID" chmod a+r /app/scripts/manual_upload.py || true

echo "Running manual upload inside container (this will print progress)..."
ARGS=( )
for f in "${files[@]}"; do
  ARGS+=(/tmp/manual_upload/"$(basename "$f")")
done

# Use docker compose exec to run in the service context (keeps envs consistent)
CMD="PYTHONPATH=/app python /app/scripts/manual_upload.py ${ARGS[*]} --notebook 'manual_upload'"
echo "Attempting: docker compose exec -T backend $CMD"
if docker compose exec -T backend sh -c "echo ok" >/dev/null 2>&1; then
  # run via compose
  docker compose exec -T backend sh -c "$CMD"
else
  echo "docker compose exec failed or service not available; falling back to docker exec on container $CONTAINER_ID"
  docker exec -i "$CONTAINER_ID" sh -c "$CMD"
fi

echo "Done. Uploaded and processed PDFs. Check backend logs or DB for details."
