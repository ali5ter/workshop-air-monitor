#!/usr/bin/env bash
# @file: start_stack.sh
# @brief: Initialize and start the InfluxDB + Grafana stack via Docker Compose
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

set -a
# shellcheck disable=SC1091
source .env
set +a

echo "🔍 Checking Docker access..."

if ! docker info &> /dev/null; then
  if [[ "$(uname)" == "Linux" ]]; then
    echo "⚠️  Docker is installed, but your user doesn't have permission to access the Docker daemon."

    if groups "$USER" | grep -q '\bdocker\b'; then
      echo "❌ You're already in the 'docker' group, but it looks like your session hasn't picked it up yet."
      echo "🔄 Please log out and log back in (or reboot) to apply group changes."
      exit 1
    else
      echo "➕ Adding user '$USER' to the 'docker' group..."
      sudo usermod -aG docker "$USER"
      echo "✅ User added to the 'docker' group."
      echo "🔄 Please log out and log back in (or reboot) before re-running this script."
      exit 1
    fi
  else
    echo "❌ Docker is not accessible, and you're not on a supported Linux system."
    echo "ℹ️ On macOS or Docker Desktop, make sure Docker is running."
    exit 1
  fi
else
  echo "✅ Docker is accessible."
fi

echo "📦 Generating Grafana datasource config from template..."
envsubst < ./grafana/provisioning/datasources/influxdb.yaml.template > ./grafana/provisioning/datasources/influxdb.yaml

echo "🚀 Starting InfluxDB and Grafana using Docker Compose..."
docker compose up -d

echo
echo "✅ Setup complete!"
echo "🌐 InfluxDB: http://${SERVER_IP}:${INFLUXDB_PORT}"
echo "    - Org: ${INFLUXDB_ORG}"
echo "    - Bucket: ${INFLUXDB_BUCKET}"
echo "    - Token: ${INFLUXDB_ADMIN_TOKEN}"
echo
echo "🌐 Grafana: http://${SERVER_IP}:${GRAFANA_PORT}"
echo "    - Username: ${GRAFANA_ADMIN_USER}"
echo "    - Password: ${GRAFANA_ADMIN_PASSWORD}"