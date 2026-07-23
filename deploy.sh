#!/bin/bash

docker build -t auth-service:latest .
docker stack deploy -c docker-compose.yml auth_service
