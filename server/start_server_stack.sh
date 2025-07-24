#!/usr/bin/env bash
# @file: start_stack.sh
# @brief: Initialize and start the InfluxDB + Grafana stack via Docker Compose
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

set -a
# shellcheck disable=SC1091
source .env
set +a

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