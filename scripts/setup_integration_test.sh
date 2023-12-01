#!/bin/bash

# This scripts setup the environment for integration test.

set -o errtrace -o nounset -o pipefail -o errexit

YEL='\033[0;33m'
GRA='\033[0;37;1m'
NC='\033[0m' # No Color
cnt_func=0


function install_localstack {
  cnt_func=$((cnt_func+1))
  echo -e "${YEL} Step-$cnt_func: ${GRA} Install Localstack packages${NC}"
  pip install localstack
  pip install localstack-client
}

function checkout_exasol_test_container {
  cnt_func=$((cnt_func+1))
  echo -e "${YEL} Step-$cnt_func: ${GRA} Checkout Exasol test container ${NC}"
   git clone --branch 1.6.0 https://github.com/exasol/integration-test-docker-environment.git
}

function spawn_exasol_environment {
  cnt_func=$((cnt_func+1))
  echo -e "${YEL} Step-$cnt_func: ${GRA} Spawn Exasol environment ${NC}"
  pushd "integration-test-docker-environment"
  ./start-test-env spawn-test-environment \
    --environment-name test --database-port-forward 9563 \
    --bucketfs-port-forward 6666 --db-mem-size 4GB --nameserver 8.8.8.8
  popd
}

function create_docker_network {
  cnt_func=$((cnt_func+1))
  echo -e "${YEL} Step-$cnt_func: ${GRA} Create docker bridge network ${NC}"
  docker network inspect it-network >/dev/null 2>&1 || \
      docker network create -d bridge --subnet 192.168.0.0/24 \
       --gateway 192.168.0.1 it-network
}

function run_localstack_container {
  cnt_func=$((cnt_func+1))
  echo -e "${YEL} Step-$cnt_func: ${GRA} Run Localstack container ${NC}"
  docker run -d  -e SERVICES=s3  -p 4566:4566 -p 4571:4571 --net it-network \
     --ip 192.168.0.2 localstack/localstack
}

function add_exasol_container_into_the_network {
  cnt_func=$((cnt_func+1))
  echo -e "${YEL} Step-$cnt_func: ${GRA} Add Exasol container to the network ${NC}"
  docker network connect it-network db_container_test
}


install_localstack
checkout_exasol_test_container
spawn_exasol_environment
create_docker_network
run_localstack_container
add_exasol_container_into_the_network

