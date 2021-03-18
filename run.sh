#!/usr/bin/env sh

# check if docker-composed is installed on host system
if [ -n "$(command -v docker-compose)" ]
then
  runner="docker-compose"
else
  echo "ERROR! You must have docker-compose installed in order to run this project!"
  exit 1
fi

howto() {
  # TODO: implement usage text
  exit 0
}

run_project() {
  cp res/.env_prod .env
  cp res/docker-compose_prod.yml docker-compose.yml
  $runner up -d && $runner logs -f
  exit 0
}

test_project() {
  cp res/.env_test .env
  cp res/docker-compose_test.yml docker-compose.yml
  $runner up --exit-code-from route-manager
  exit 0
}

# main
if [ $# -eq 1 ]
then
  if [ $1 = "test" ]
  then
    test_project
  elif [ $1 = "prod" ]
  then
    run_project
  fi
fi

howto
