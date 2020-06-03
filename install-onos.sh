#!/usr/bin/env bash

# Download docker image of ONOS
docker pull onosproject/onos

# Run docker image of ONOS
docker run -t -d -p 6653:6653 -p 8181:8181 -p 8101:8101 -p 5005:5005 -p 830:830 --env JAVA_DEBUG_PORT="0.0.0.0:5005" --name onos onosproject/onos debug

# Getting ONOS IP address
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker ps -q  --filter ancestor=onosproject/onos)

echo "127.0.0.1:8181/onos/ui/index.html"