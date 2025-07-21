#!/usr/bin/env bash
# @file: start_influx_grafana.sh
# @brief: Script to set up InfluxDB and Grafana as container apps using Docker.
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

set -a
# shellcheck disable=SC1091
source ./influx_grafana_config.env
set +a

docker_running() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running or not available. Please start Docker and try again."
        exit 1
    fi
}

install_docker() {
    if ! command -v apt-get &> /dev/null; then
        echo "❌ This script requires docker to be installed. Please install Docker manually."
        echo "For manual installation, refer to the official Docker documentation: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    echo "🐳 Installing Docker..."

    sudo apt-get update
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker’s official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
        $(lsb_release -cs) stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    sudo usermod -aG docker "$USER"
    echo "✅ Docker installed. Please log out and back in (or reboot) to use Docker without sudo."
}

config_docker() {
    echo "🔧 Creating Docker network 'monitor-net'..."
    docker network create monitor-net || echo "⚠️  Network 'monitor-net' already exists."

    echo "📁 Creating Docker volumes for persistence..."
    docker volume create influxdb-data
    docker volume create grafana-storage
}

start_influxdb() {
    echo "🚀 Starting InfluxDB container..."
    docker run -d \
        --name=influxdb \
        --network=monitor-net \
        -p "$INFLUXDB_PORT":"$INFLUXDB_PORT" \
        -v influxdb-data:/var/lib/influxdb2 \
        -e DOCKER_INFLUXDB_INIT_MODE=setup \
        -e DOCKER_INFLUXDB_INIT_USERNAME="$INFLUXDB_USERNAME" \
        -e DOCKER_INFLUXDB_INIT_PASSWORD="$INFLUXDB_PASSWORD" \
        -e DOCKER_INFLUXDB_INIT_ORG="$INFLUXDB_ORG" \
        -e DOCKER_INFLUXDB_INIT_BUCKET="$INFLUXDB_BUCKET" \
        -e DOCKER_INFLUXDB_INIT_ADMIN_TOKEN="$INFLUXDB_ADMIN_TOKEN" \
        influxdb:2.7
}   

start_grafana() {
    echo "🚀 Starting Grafana container..."
    docker run -d \
        --name=grafana \
        --network=monitor-net \
        -p "$GRAFANA_PORT":"$GRAFANA_PORT" \
        -v grafana-storage:/var/lib/grafana \
        -e GF_SECURITY_ADMIN_USER="$GRAFANA_ADMIN_USER" \
        -e GF_SECURITY_ADMIN_PASSWORD="$GRAFANA_ADMIN_PASSWORD" \
        -e GF_SECURITY_DISABLE_INITIAL_ADMIN_CHANGE="$GRAFANA_DISABLE_INITIAL_ADMIN_CHANGE" \
        grafana/grafana
}

main() {
    [[ -n $DEBUG ]] && set -x
    set -eou pipefail

    if ! command -v docker &> /dev/null; then
        install_docker
    fi
    docker_running
    config_docker

    start_influxdb
    start_grafana

    echo "📡 Local IP address: $SERVER_IP"

    echo "✅ Setup complete!"
    echo "🌐 InfluxDB available at: http://$SERVER_IP:$INFLUXDB_PORT"
    echo "    - Username: $INFLUXDB_USERNAME"
    echo "    - Password: $INFLUXDB_PASSWORD"
    echo "    - Org: $INFLUXDB_ORG"
    echo "    - Bucket: $INFLUXDB_BUCKET"
    echo "    - Token: $INFLUXDB_ADMIN_TOKEN"
    echo
    echo "🌐 Grafana available at: http://$SERVER_IP:$GRAFANA_PORT"
    echo "    - Username: $GRAFANA_ADMIN_USER"
    echo "    - Password: $GRAFANA_ADMIN_PASSWORD"
}

# Run the script as it is being executed directly
[ "${BASH_SOURCE[0]}" -ef "$0" ] && main "$@"