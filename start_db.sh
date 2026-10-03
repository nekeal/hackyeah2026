#!/bin/bash

docker run --name hackyeah2026-db \
  -e POSTGRES_USER=hackyeah2026 \
  -e POSTGRES_PASSWORD=hackyeah2026 \
  -e POSTGRES_DB=hackyeah2026 \
  -p 5432:5432 \
  -d postgres:latest
